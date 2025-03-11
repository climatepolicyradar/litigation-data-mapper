from typing import Any, Optional

import click

from litigation_data_mapper.parsers.helpers import initialise_counter


def get_document_headline(document, family_type):
    if family_type == "us_case":
        return document.get(
            "ccl_document_headline"
        )  # should we handle instances where this is none, say grab the document type

    return document.get("ccl_nonus_document_type")


def process_family_documents(
    family: dict,
    case_id: int,
    document_pdf_urls: dict[str, str],
    document_family_counter: dict[str, int],
) -> Optional[list[dict[str, Any]]]:
    family_type = family.get("type")

    # TODO : add check that ccl_file id exists

    if family_type == "us_case":
        documents = family.get("acf", {}).get("ccl_case_documents", [])
    else:
        documents = family.get("acf", {}).get("ccl_nonus_case_documents", [])

    if not documents:
        click.echo(
            f"🛑 Skipping {family_type} case_id {case_id}, missing case documents"
        )
        return None

    family_documents = []
    family_import_id = f"Litigation.family.{case_id}.0"
    document_import_id = ""

    initialise_counter(document_family_counter, family_import_id)

    for doc in documents:
        document_id = doc.get("ccl_file")
        document_pdf_url = document_pdf_urls.get(document_id)
        document_data = {
            "import_id": document_import_id,
            "family_import_id": family_import_id,
            "metadata": {},
            "title": get_document_headline(doc, family_type),
            "source_url": document_pdf_url,
            "variant_name": "",
        }

        document_family_counter[family_import_id] += 1
        family_documents.append(document_data)

    return family_documents


def map_documents(documents_data: dict[str, Any], debug: bool) -> list[dict[str, Any]]:
    """Maps the litigation case document information to the internal data structure.

    This function transforms document data, which the Sabin Centre refers to as
    case documents, into our internal data modelling structure. It returns a list of
    mapped documents, each represented as a dictionary matching the required schema.

    :param bool debug: Flag indicating whether to enable debug mode. When enabled, debug
        messages are logged for troubleshooting..
    :return list[dict[str, Any]]: A list of litigation case documents in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if debug:
        click.echo("📝 No Litigation document data to wrangle.")

    global_cases = documents_data.get("families", {}).get("global_cases", [])
    us_cases = documents_data.get("families", {}).get("us_cases", [])
    document_media = documents_data.get("documents", [])

    document_pdf_urls = {
        document["id"]: document["source_url"]
        for document in document_media
        if "id" in document and "source_url" in document
    }

    families = global_cases.extend(us_cases)

    document_family_counter = {}

    mapped_documents = []

    for family in families:
        case_id = family.get("id")
        if not case_id:
            click.echo("Skipping family ")
            continue
        process_family_documents(
            family, case_id, document_pdf_urls, document_family_counter
        )

    return mapped_documents
