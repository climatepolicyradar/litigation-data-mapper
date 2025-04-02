import os
from typing import Any, Optional, Union

import click

SUPPORTED_FILE_EXTENSIONS = [".pdf", ".html"]


def get_document_headline(
    document: dict[str, Any], case_type: str, case_title: str
) -> Optional[str]:
    """Extracts the headline or title of the document based on case type.

    :param dict document: The document data, which may contain various attributes, including the title or content.
    :param str case_type: The type of case (e.g., "us (case)", "global (non_us_case)") used to determine how the document should be processed.
    :param str case_title: The title of the case
    :return Optional[str]: The extracted document title, or None if no valid headline can be generated.
    """
    if case_type == "case":
        document_headline = document.get("ccl_document_headline")
        if not document_headline:
            return f"{case_title} - {document['ccl_document_type']}"

        return document_headline

    return f"{case_title} - {document['ccl_nonus_document_type']}"


def map_document(
    doc: dict[str, Union[str, int]],
    case_id: int,
    case_title: str,
    case_type: str,
    document_id: int,
    document_source_url: str,
) -> dict[str, str]:
    """Maps the document data to the internal data structure.

    This function transforms the document data into our internal data modelling structure.
    It returns a mapped document as a dictionary matching the required schema for the litigation case documents.

    :param dict[str, Union[str, int]] doc: The document data, including document attributes such as title, ID, etc.
    :param int case_id: The unique identifier for the case, used to associate the document with the correct case.
    :param str case_title: The title of the case.
    :param str case_type: The type of case (e.g., "us (case)", "global (non_us_case)") used to determine how the document should be processed.
    :param str document_source_url: The URL of the document source, typically the location of the PDF or other related media.
    :param str document_id: The file id of the document.
    :return dict[str, str]: A dictionary representing the mapped document, or None if the document is invalid or cannot be processed.
    """
    document_title = get_document_headline(doc, case_type, case_title)

    family_import_id = f"Sabin.family.{case_id}.0"
    document_import_id = f"Sabin.document.{case_id}.{document_id}"

    mapped_document = {
        "import_id": document_import_id,
        "family_import_id": family_import_id,
        "metadata": {"id": [str(document_id)]},
        "title": document_title,
        "source_url": document_source_url,
        "variant_name": "Original Language",
    }

    return mapped_document


def _dummy_document(case_id: int) -> dict[str, Any]:
    """
    Creates a dummy empty document. This is a temporary solution added as part of APP-449
    in order to allow families without documents to be ingested by Vespa.
    To be removed once the permanent solution is implemented.

    :param int case_id: The id of the case the document should be linked to.
    :return dict[str, Any]: A dictionary representing the mapped document, or None if the document is invalid or cannot be processed.
    """
    return {
        "import_id": f"Sabin.document.{case_id}.dummy",
        "family_import_id": f"Sabin.family.{case_id}.0",
        "metadata": {"id": ["dummy"]},
        "title": "",
        "source_url": None,
        "variant_name": None,
    }


def process_family_documents(
    family: dict,
    case_id: int,
    document_pdf_urls: dict[int, str],
    context: dict[str, Any],
) -> list[dict[str, Any]] | None:
    """Processes the family-related case documents and maps them to the internal data structure.

    This function transforms family case document data, including associated document PDFs,
    into our internal data modelling structure. It returns a list of mapped family documents,
    each represented as a dictionary matching the required schema.

    :param dict family: The family case related data, including family details and related documents.
    :param int case_id: The unique identifier for the case, used to link documents to the correct case.
    :param dict[int, str] document_pdf_urls: A dictionary containing URLs to the document PDFs that need to be processed.
    :param dict[str, Any] context: The context of the litigation project import.
    :return list[dict[str, Any]] | None: A list of mapped family case documents in the 'destination' format described in the Litigation Data Mapper Google Sheet, or None if no documents are found.
    """

    case_type = family.get("type")
    case_title = family.get("title", {}).get("rendered")

    if not case_type or not case_title:
        click.echo(
            f"🛑 Skipping document as family with case_id {case_id} is missing case type/title key."
        )
        context["skipped_families"].append(case_id)
        return None

    documents_key = (
        "ccl_case_documents" if case_type == "case" else "ccl_nonus_case_documents"
    )
    documents = family.get("acf", {}).get(documents_key, [])

    family_documents = []

    family_documents.append(_dummy_document(case_id))

    for doc in documents:
        document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
        document_id = doc.get(
            document_id_key,
        )

        if document_id is None or not isinstance(document_id, int):
            click.echo(
                f"🛑 Skipping document in {case_type}({case_id}): "
                f"{'the document ID is missing' if document_id is None else 'the document id is an empty string, assuming no associated files'}."
            )
            continue

        document_source_url = document_pdf_urls.get(document_id)

        if not document_source_url:
            click.echo(
                f"🛑 Skipping document in {case_type} ({case_id}): "
                f"the document ({document_id}) is missing a source URL."
            )

            context["skipped_documents"].append(document_id)
            continue

        _, ext = os.path.splitext(document_source_url)
        if ext.lower() not in SUPPORTED_FILE_EXTENSIONS:
            click.echo(
                f"🛑 Skipping document as [{ext}] is not a valid file ext. document_id: {document_id}"
            )
            context["skipped_documents"].append(document_id)
            continue

        document_data = map_document(
            doc,
            case_id,
            case_title,
            case_type,
            document_id,
            document_source_url,
        )

        if not document_data:
            continue

        family_documents.append(document_data)

    return family_documents


def validate_data(
    global_cases: list[dict[str, Any]],
    us_cases: list[dict[str, Any]],
    document_media: list[dict[str, Any]],
) -> bool:
    """Validate that all required datasets are present.
    :param list[dict[str, Any]] global_cases: A list of global case data dictionaries.
    :param list[dict[str, Any]] us_cases: A list of US case data dictionaries.
    :param list[dict[str, Any]] jurisdictions: A list of jurisdiction data dictionaries.
    :return bool: True if all required datasets are present, otherwise False.
    """

    if not global_cases or not us_cases:
        missing_dataset = "global" if not global_cases else "US"
        click.echo(
            f"🛑 No {missing_dataset} cases found in the data. Skipping document litigation."
        )
        return False

    if not document_media:
        click.echo(
            "🛑 No document media provided in the data. Skipping document litigation."
        )
        return False

    return True


def map_documents(
    documents_data: dict[str, Any], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Maps the litigation case document information to the internal data structure.

    This function transforms document data, which the Sabin Centre refers to as
    case documents, into our internal data modelling structure. It returns a list of
    mapped documents, each represented as a dictionary matching the required schema.

    :parm dict[str, Any] documents_data: The case related data, structured as global cases,
        us cases and document media information, notably source urls for document pdfs.
    :param  dict[str, Any] context: The context of the litigation project import.
    :return list[dict[str, Any]]: A list of litigation case documents in
        the 'destination' format described in the Litigation Data Mapper Google
        Sheet.
    """
    if context["debug"]:
        click.echo("📝 No Litigation document data to wrangle.")

    global_cases = documents_data.get("families", {}).get("global_cases", [])
    us_cases = documents_data.get("families", {}).get("us_cases", [])
    document_media = documents_data.get("documents", [])

    if not validate_data(global_cases, us_cases, document_media):
        return []

    document_pdf_urls = {
        document["id"]: document["source_url"]
        for document in document_media
        if "id" in document and "source_url" in document
    }

    families = global_cases + us_cases

    mapped_documents = []
    context["skipped_documents"] = []

    for index, family in enumerate(families):
        case_id = family.get("id")
        if not isinstance(case_id, int):
            click.echo(f"🛑 Skipping documents: missing case id at index {index}.")
            continue

        if case_id in context["skipped_families"]:
            click.echo(
                f"🛑 Skipping documents in case ({case_id}): case in skipped families context."
            )
            continue

        result = process_family_documents(family, case_id, document_pdf_urls, context)

        if result:
            mapped_documents.extend(result)

    return mapped_documents
