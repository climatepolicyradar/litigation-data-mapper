#!/usr/bin/env python3
"""
Debugging tool for the litigation label pipeline:

    WordPress -> litigation-data-mapper -> families-api (RDS) -> data-in-pipeline -> search labels

`fetch` downloads/refreshes the local caches this tool needs.
`check <label>` runs a concept through every cached stage and reports diffs/errors -
e.g. a `principal_law` concept that resolves to different parents in different
families, a duplicate WordPress taxonomy term, an orphaned/stale family, or a
taxonomy term missing from the cache due to pagination drift.
`scan` walks the whole cached WordPress taxonomy (the source data every other
stage inherits from) and reports every duplicate term / dangling parent it finds,
without needing to name a specific label.

Usage:
    python scripts/label_debugger.py fetch [--profile production]
                                            [--refresh-wp-data] [--refresh-ldm-data] [--refresh-dip-data]
    python scripts/label_debugger.py check "Directives" [--verify-live]
    python scripts/label_debugger.py scan [--verify-live]

Requires AWS credentials for the `fetch` S3 downloads and (optionally) SSM access
for `--verify-live` on `check`. Does not require any other repo on disk - this is
self-contained within litigation-data-mapper.
"""

import argparse
import json
import shutil
import subprocess  # nosec: B404
import sys
from collections import defaultdict
from pathlib import Path

import boto3
import requests
from requests.auth import HTTPBasicAuth

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE_DIR = REPO_ROOT / ".cache" / "scripts" / "label_debugger"

S3_BUCKET = "cpr-cache"
TAXONOMY_KEYS = {
    "principal_law": "litigation/wordpress/principal_law.json",
    "non_us_principal_law": "litigation/wordpress/non_us_principal_law.json",
}
TAXONOMY_WORDPRESS_LISTS = {
    "principal_law": "US Principal Law",
    "non_us_principal_law": "Non-US Principal Law",
}
CASE_KEYS = {
    "case": "litigation/wordpress/case.json",
    "non_us_case": "litigation/wordpress/non_us_case.json",
}
DELETIONS_KEY = "litigation/state/deletions.json"
DOCUMENTS_KEY = "pipelines/data-in-pipeline/navigator_family/documents-latest.jsonl"
FAMILIES_API = "https://api.climatepolicyradar.org/families"
WORDPRESS_BASE_URL = "https://admin.climatecasechart.com/wp-json/wp/v2"

PARAMETER_WORDPRESS_USER_NAME = "/Litigation/WordPress/User"
PARAMETER_WORDPRESS_APP_PASSWORD_NAME = (
    "/Litigation/WordPress/AppPassword"  # nosec: B105
)


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------


def cmd_fetch(args: argparse.Namespace) -> None:
    cache_dir = DEFAULT_CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    session = boto3.Session(profile_name=args.profile)
    client = session.client("s3", region_name="eu-west-1")

    for name, key in TAXONOMY_KEYS.items():
        print(f"Downloading taxonomy: {name}")
        obj = client.get_object(Bucket=S3_BUCKET, Key=key)
        (cache_dir / f"{name}.json").write_bytes(obj["Body"].read())

    if args.refresh_wp_data:
        for name, key in CASE_KEYS.items():
            print(f"Downloading raw case data: {name} (large)")
            client.download_file(S3_BUCKET, key, str(cache_dir / f"{name}.json"))

    print("Downloading deletions.json")
    obj = client.get_object(Bucket=S3_BUCKET, Key=DELETIONS_KEY)
    (cache_dir / "deletions.json").write_bytes(obj["Body"].read())

    if args.refresh_dip_data:
        print(
            "Downloading documents-latest.jsonl (~700MB, a few cents of S3 egress)..."
        )
        client.download_file(
            S3_BUCKET, DOCUMENTS_KEY, str(cache_dir / "documents-latest.jsonl")
        )
    else:
        print("Skipping documents-latest.jsonl (pass --refresh-dip-data to download)")

    if args.refresh_ldm_data:
        print(
            "Regenerating output.json via a live litigation_data_mapper run "
            "(hits WordPress live, can take several minutes)..."
        )
        env = {**__import__("os").environ, "AWS_PROFILE": args.profile}
        subprocess.run(  # nosec: B603
            [str(REPO_ROOT / ".venv" / "bin" / "litigation_data_mapper")],
            cwd=REPO_ROOT,
            env=env,
            check=True,
        )
        shutil.copy(REPO_ROOT / "output.json", cache_dir / "output.json")
    elif (REPO_ROOT / "output.json").exists():
        shutil.copy(REPO_ROOT / "output.json", cache_dir / "output.json")
        print(f"Copied existing {REPO_ROOT / 'output.json'} into cache")
    else:
        print(
            "No output.json found and --refresh-ldm-data not passed; "
            "`check` will skip LDM-stage checks."
        )

    print(f"\nDone. Caches in {cache_dir}")


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


def load_json(path: Path):
    return json.loads(path.read_text())


def require_cache_file(path: Path, refresh_args: str, errors: list[str]) -> bool:
    """Return True if `path` exists; otherwise record/print an error naming the fetch command to run."""
    if path.exists():
        return True
    command = f"python scripts/label_debugger.py fetch {refresh_args}".rstrip()
    msg = f"Missing cache file {path.name} - run `{command}`."
    print(f"  ERROR: {msg}")
    errors.append(msg)
    return False


def build_taxonomy_index(cache_dir: Path):
    """Index every taxonomy term by (taxonomy, id) and by bare name."""
    by_id: dict[tuple[str, int], dict] = {}
    by_name: dict[str, list[dict]] = defaultdict(list)
    for taxonomy in TAXONOMY_KEYS:
        path = cache_dir / f"{taxonomy}.json"
        if not path.exists():
            continue
        for item in load_json(path):
            entry = {
                "id": item["id"],
                "name": item["name"],
                "parent": item["parent"],
                "taxonomy": taxonomy,
            }
            by_id[(taxonomy, item["id"])] = entry
            by_name[item["name"]].append(entry)
    return by_id, by_name


def parent_chain(by_id, taxonomy: str, term_id: int):
    """Walk the parent chain. Returns (names_from_leaf_to_root, dangling_parent_id|None)."""
    chain: list[str] = []
    seen: set[int] = set()
    current_id = term_id
    while current_id and current_id != 0 and current_id not in seen:
        seen.add(current_id)
        entry = by_id.get((taxonomy, current_id))
        if entry is None:
            return chain, current_id
        chain.append(entry["name"])
        current_id = entry["parent"]
    return chain, None


def get_wordpress_auth(profile: str) -> HTTPBasicAuth:
    session = boto3.Session(profile_name=profile)
    ssm = session.client("ssm", region_name="eu-west-1")
    user = ssm.get_parameter(Name=PARAMETER_WORDPRESS_USER_NAME, WithDecryption=True)[
        "Parameter"
    ]["Value"]
    password = ssm.get_parameter(
        Name=PARAMETER_WORDPRESS_APP_PASSWORD_NAME, WithDecryption=True
    )["Parameter"]["Value"]
    return HTTPBasicAuth(user, password)


def verify_term_live(taxonomy: str, term_id: int, auth: HTTPBasicAuth) -> str:
    resp = requests.get(
        f"{WORDPRESS_BASE_URL}/{taxonomy}/{term_id}", auth=auth, timeout=10
    )
    if resp.status_code == 200:
        return f"EXISTS live on WordPress (name={resp.json().get('name')!r}) - missing from cache is a fetch/pagination bug, not a real deletion."
    return f"HTTP {resp.status_code} from WordPress - term genuinely gone/inaccessible."


def check_output_json(cache_dir: Path, bare_name: str, errors: list[str]):
    print("\n=== output.json (litigation-data-mapper stage) ===")
    output_json_path = cache_dir / "output.json"
    if not require_cache_file(output_json_path, "--refresh-ldm-data", errors):
        return

    deletions: set[str] = set()
    deletions_path = cache_dir / "deletions.json"
    if require_cache_file(deletions_path, "", errors):
        deletions = set(load_json(deletions_path))

    data = load_json(output_json_path)
    family_rows = []
    subconcept_groups: dict[tuple, list[str]] = defaultdict(list)

    for f in data["families"]:
        tagged_names = {
            c["preferred_label"]
            for c in f.get("concepts", [])
            if c.get("relation") == "principal_law"
        }
        for c in f.get("concepts", []):
            if (
                c.get("preferred_label") != bare_name
                or c.get("relation") != "principal_law"
            ):
                continue
            subs = tuple(c.get("subconcept_of_labels") or [])
            orphaned = f["import_id"] in deletions
            missing_cotag = [p for p in subs if p not in tagged_names]
            family_rows.append((f["import_id"], subs, orphaned, missing_cotag))
            subconcept_groups[subs].append(f["import_id"])

    if not family_rows:
        print("  No families reference this label.")
        return

    print(f"  {len(family_rows)} families reference this label.")
    for subs, ids in subconcept_groups.items():
        label_str = " -> ".join(subs) if subs else "(no parent)"
        print(f"    {len(ids):>4} families resolve to: {label_str}  e.g. {ids[0]}")

    if len(subconcept_groups) > 1:
        msg = (
            "ERROR: inconsistent subconcept_of_labels across families: "
            f"{ {k: len(v) for k, v in subconcept_groups.items()} }"
        )
        print(f"  {msg}")
        errors.append(msg)

    for fid, _, orphaned, missing_cotag in family_rows:
        flags = []
        if orphaned:
            flags.append("ORPHANED (deleted from WordPress, stale in RDS)")
        if missing_cotag:
            flags.append(
                f"parent(s) {missing_cotag} declared but not co-tagged on this family"
            )
        if flags:
            print(f"    - {fid}: {', '.join(flags)}")


def check_documents_latest(
    cache_dir: Path, bare_name: str, full_id: str, errors: list[str]
):
    print("\n=== documents-latest.jsonl (data-in-pipeline stage) + simulated merge ===")
    docs_path = cache_dir / "documents-latest.jsonl"
    if not require_cache_file(docs_path, "--refresh-dip-data", errors):
        return
    per_doc: list[tuple[str, list[str]]] = []
    with open(docs_path) as f:
        for line in f:
            if bare_name not in line:
                continue
            doc = json.loads(line)
            for lr in doc.get("labels", []):
                v = lr["value"]
                if v["id"] != full_id:
                    continue
                parents = [
                    label_ref["value"]["id"]
                    for label_ref in v.get("labels", [])
                    if label_ref["type"] == "subconcept_of"
                ]
                per_doc.append((doc.get("id"), parents))

    if not per_doc:
        print("  No documents reference this label.")
        return

    print(f"  {len(per_doc)} documents reference this label.")
    distinct_parent_sets: dict[tuple, list[str]] = defaultdict(list)
    for doc_id, parents in per_doc:
        distinct_parent_sets[tuple(sorted(parents))].append(doc_id)
    for parents, ids in distinct_parent_sets.items():
        print(f"    {len(ids):>4} docs -> parents {parents or '(none)'}  e.g. {ids[0]}")

    merged_parents = sorted({p for _, parents in per_doc for p in parents})
    print(
        f"\n  SIMULATED MATERIALIZER MERGE (plain union, current behaviour): {merged_parents}"
    )
    if len(merged_parents) > 1:
        msg = (
            f"ERROR: merged label would carry {len(merged_parents)} distinct "
            f"subconcept_of parents: {merged_parents} - this is the duplicate-in-tree bug."
        )
        print(f"  {msg}")
        errors.append(msg)


def check_taxonomy(
    cache_dir: Path, bare_name: str, errors: list[str], verify_live: bool, profile: str
):
    print(f"=== Taxonomy lookup: {bare_name!r} ===")
    missing = [
        taxonomy
        for taxonomy in TAXONOMY_KEYS
        if not require_cache_file(cache_dir / f"{taxonomy}.json", "", errors)
    ]
    if missing:
        return

    by_id, by_name = build_taxonomy_index(cache_dir)
    matches = by_name.get(bare_name, [])

    if not matches:
        print("  NOT FOUND in taxonomy cache.")
        errors.append(
            f"Label {bare_name!r} not found in taxonomy cache (check spelling)."
        )
        return

    auth = None
    parents_seen = set()
    for m in matches:
        chain, missing = parent_chain(by_id, m["taxonomy"], m["id"])
        parents_seen.add(m["parent"])
        chain_str = " -> ".join(reversed(chain)) if chain else "(no ancestors)"
        print(
            f"  [{m['taxonomy']}] id={m['id']} parent_id={m['parent']} chain: {chain_str}"
        )
        if missing is not None:
            msg = (
                f"ERROR: parent id {missing} referenced by id={m['id']} not found in "
                "taxonomy cache (possible fetch/pagination drift)."
            )
            print(f"  {msg}")
            errors.append(msg)
            if verify_live:
                if auth is None:
                    auth = get_wordpress_auth(profile)
                print(
                    f"    live check: {verify_term_live(m['taxonomy'], missing, auth)}"
                )

    if len(matches) > 1:
        print(f"  NOTE: {len(matches)} distinct taxonomy terms share this name.")
        if len(parents_seen) > 1 and 0 in parents_seen:
            parentless = [
                f"{m['taxonomy']}/{m['id']}" for m in matches if m["parent"] == 0
            ]
            parented = [
                f"{m['taxonomy']}/{m['id']}" for m in matches if m["parent"] != 0
            ]
            lists_affected = sorted(
                {TAXONOMY_WORDPRESS_LISTS[m["taxonomy"]] for m in matches}
            )
            remediation = " / ".join(
                f'search WordPress for "{bare_name}" in the {wp_list} list'
                for wp_list in lists_affected
            )
            msg = (
                f"ERROR: duplicate term - WordPress id(s) {parentless} are parentless while "
                f"id(s) {parented} have a real parent. Any family using the parentless "
                "WordPress term will render directly under category::Litigation. "
                f"Remediation: {remediation}, then merge/delete the parentless duplicate."
            )
            print(f"  {msg}")
            errors.append(msg)


def scan_taxonomy(
    cache_dir: Path, errors: list[str], verify_live: bool, profile: str
) -> None:
    """Scan every cached taxonomy term for dangling parents and duplicate terms."""
    missing = [
        taxonomy
        for taxonomy in TAXONOMY_KEYS
        if not require_cache_file(cache_dir / f"{taxonomy}.json", "", errors)
    ]
    if missing:
        return

    by_id, by_name = build_taxonomy_index(cache_dir)
    auth = None

    for entry in by_id.values():
        parent_id = entry["parent"]
        if parent_id and (entry["taxonomy"], parent_id) not in by_id:
            msg = (
                f"ERROR: parent id {parent_id} referenced by {entry['taxonomy']}/{entry['id']} "
                f"({entry['name']!r}) not found in taxonomy cache (possible fetch/pagination drift)."
            )
            print(f"  {msg}")
            errors.append(msg)
            if verify_live:
                if auth is None:
                    auth = get_wordpress_auth(profile)
                print(
                    f"    live check: {verify_term_live(entry['taxonomy'], parent_id, auth)}"
                )

    for name, matches in by_name.items():
        parents_seen = {m["parent"] for m in matches}
        if len(matches) > 1 and len(parents_seen) > 1 and 0 in parents_seen:
            parentless = [
                f"{m['taxonomy']}/{m['id']}" for m in matches if m["parent"] == 0
            ]
            parented = [
                f"{m['taxonomy']}/{m['id']}" for m in matches if m["parent"] != 0
            ]
            lists_affected = sorted(
                {TAXONOMY_WORDPRESS_LISTS[m["taxonomy"]] for m in matches}
            )
            remediation = " / ".join(
                f'search WordPress for "{name}" in the {wp_list} list'
                for wp_list in lists_affected
            )
            msg = (
                f"ERROR: duplicate term {name!r} - WordPress id(s) {parentless} are "
                f"parentless while id(s) {parented} have a real parent. Any family using "
                "the parentless WordPress term will render directly under "
                f"category::Litigation. Remediation: {remediation}, then merge/delete the "
                "parentless duplicate."
            )
            print(f"  {msg}")
            errors.append(msg)


def cmd_scan(args: argparse.Namespace) -> None:
    cache_dir = DEFAULT_CACHE_DIR
    errors: list[str] = []

    print(
        "=== Scanning WordPress taxonomy cache for dangling parents & duplicate terms ==="
    )
    scan_taxonomy(cache_dir, errors, args.verify_live, args.profile)

    print("\n=== Summary ===")
    if errors:
        print(f"  {len(errors)} issue(s) found:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("  No issues detected.")


def cmd_check(args: argparse.Namespace) -> None:
    cache_dir = DEFAULT_CACHE_DIR
    label = args.label
    bare_name = label.split("::", 1)[1] if "::" in label else label
    full_id = label if "::" in label else f"principal_law::{label}"

    errors: list[str] = []
    check_taxonomy(cache_dir, bare_name, errors, args.verify_live, args.profile)
    check_output_json(cache_dir, bare_name, errors)
    check_documents_latest(cache_dir, bare_name, full_id, errors)

    print("\n=== Summary ===")
    if errors:
        for e in errors:
            print(f"  - {e}")
    else:
        print("  No issues detected.")


# ---------------------------------------------------------------------------
# entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_p = sub.add_parser("fetch", help="Download/refresh local debug caches")
    fetch_p.add_argument("--profile", default="production", help="AWS profile to use")
    fetch_p.add_argument(
        "--refresh-wp-data",
        action="store_true",
        help="Download raw case.json/non_us_case.json from WordPress's S3 cache (large; needed to inspect raw per-case WordPress tag IDs)",
    )
    fetch_p.add_argument(
        "--refresh-ldm-data",
        action="store_true",
        help="Run a live litigation_data_mapper pull to regenerate output.json (slow, hits WordPress)",
    )
    fetch_p.add_argument(
        "--refresh-dip-data",
        action="store_true",
        help="Download documents-latest.jsonl from data-in-pipeline's S3 cache (~700MB, a few cents of S3 egress)",
    )
    fetch_p.set_defaults(func=cmd_fetch)

    check_p = sub.add_parser(
        "check", help="Check a label/concept for pipeline inconsistencies"
    )
    check_p.add_argument(
        "label", help="Concept name, e.g. 'Directives' or 'principal_law::Directives'"
    )
    check_p.add_argument(
        "--profile", default="production", help="AWS profile to use for --verify-live"
    )
    check_p.add_argument(
        "--verify-live",
        action="store_true",
        help="For any dangling taxonomy parent reference, confirm live against WordPress (needs SSM access)",
    )
    check_p.set_defaults(func=cmd_check)

    scan_p = sub.add_parser(
        "scan",
        help="Scan the whole WordPress taxonomy cache for duplicate terms and dangling parents",
    )
    scan_p.add_argument(
        "--profile", default="production", help="AWS profile to use for --verify-live"
    )
    scan_p.add_argument(
        "--verify-live",
        action="store_true",
        help="For any dangling taxonomy parent reference, confirm live against WordPress (needs SSM access)",
    )
    scan_p.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
