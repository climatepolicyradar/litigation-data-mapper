from typing import Any, Optional, Union

import click

from litigation_data_mapper.parsers.helpers import initialise_counter


def get_document_headline(document, case_type, case_title) -> Optional[str]:
    """Extracts the headline or title of the document based on case type.

    :param dict document: The document data, which may contain various attributes, including the title or content.
    :param str case_type: The type of case (e.g., "us (case)", "global (non_us_case)") used to determine how the document should be processed.
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
    document_family_counter: dict[str, int],
) -> dict[str, str]:
    """Maps the document data to the internal data structure.

    This function transforms the document data into our internal data modelling structure.
    It returns a mapped document as a dictionary matching the required schema for the litigation case documents.

    :param dict[str, Union[str, int]] doc: The document data, including document attributes such as title, ID, etc.
    :param int case_id: The unique identifier for the case, used to associate the document with the correct case.
    :param str case_title: The title of the case.
    :param str case_type: The type of case (e.g., "us (case)", "global (non_us_case)") used to determine how the document should be processed.
    :param str document_source_url: The URL of the document source, typically the location of the PDF or other related media.
    :param dict[str, int] document_family_counter: A dictionary that tracks the count of document types for each family or case.
    :param str document_id: The file id of the document.
    :return dict[str, str]: A dictionary representing the mapped document, or None if the document is invalid or cannot be processed.
    """
    document_title = get_document_headline(doc, case_type, case_title)

    family_import_id = f"Litigation.family.{case_id}.0"
    document_import_id = (
        f"GEF.document.{case_id}.n{document_family_counter[family_import_id]:04}"
    )

    mapped_document = {
        "import_id": document_import_id,
        "family_import_id": family_import_id,
        "metadata": {"id": [document_id]},
        "title": document_title,
        "source_url": document_source_url,
        "variant_name": "",
    }

    return mapped_document


def process_family_documents(
    family: dict,
    case_id: int,
    document_pdf_urls: dict[str, str],
    document_family_counter: dict[str, int],
) -> Optional[list[dict[str, Any]]]:
    """Processes the family-related case documents and maps them to the internal data structure.

    This function transforms family case document data, including associated document PDFs,
    into our internal data modelling structure. It returns a list of mapped family documents,
    each represented as a dictionary matching the required schema.

    :param dict family: The family case related data, including family details and related documents.
    :param int case_id: The unique identifier for the case, used to link documents to the correct case.
    :param dict[str, str] document_pdf_urls: A dictionary containing URLs to the document PDFs that need to be processed.
    :param dict[str, int] document_family_counter: A dictionary that tracks the count of document types for each family case.
    :return Optional[list[dict[str, Any]]]: A list of mapped family case documents in the 'destination' format described in the Litigation Data Mapper Google Sheet, or None if no documents are found.
    """

    case_type = family.get("type")
    case_title = family.get("title", {}).get("rendered")

    if not case_type or not case_title:
        click.echo(
            f"🛑 Skipping document as family with {case_id} is missing case type/title key "
        )
        return None

    documents_key = (
        "ccl_case_documents" if case_type == "case" else "ccl_nonus_case_documents"
    )
    documents = family.get("acf", {}).get(documents_key, [])

    if not documents:
        click.echo(
            f"🛑 Skipping document as family ({case_type}) with case_id:{case_id} is missing case documents"
        )
        return None

    family_documents = []
    family_import_id = f"Litigation.family.{case_id}.0"
    initialise_counter(document_family_counter, family_import_id)

    for doc in documents:
        document_id_key = "ccl_file" if case_type == "case" else "ccl_nonus_file"
        document_id = doc.get(document_id_key)
        document_source_url = (
            document_pdf_urls.get(document_id) if document_id else None
        )

        if not document_id or not document_source_url:
            click.echo(
                f"🛑 Skipping document (id: {document_id}) ({case_type} : {case_id}):"
                f"{'the document ID is missing' if not document_id else 'the document is missing a source URL'}."
            )
            continue

        document_data = map_document(
            doc,
            case_id,
            case_title,
            case_type,
            document_id,
            document_source_url,
            document_family_counter,
        )

        if not document_data:
            continue

        document_family_counter[family_import_id] += 1
        family_documents.append(document_data)

    return family_documents


def map_documents(documents_data: dict[str, Any], debug: bool) -> list[dict[str, Any]]:
    """Maps the litigation case document information to the internal data structure.

    This function transforms document data, which the Sabin Centre refers to as
    case documents, into our internal data modelling structure. It returns a list of
    mapped documents, each represented as a dictionary matching the required schema.

    :parm dict[str, Any] documents_data: The case related data, structured as global cases,
        us cases and document media information, notably source urls for document pdfs.
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

    if not global_cases or not us_cases:
        missing_dataset = "global" if not global_cases else "US"
        click.echo(
            f"🛑 No {missing_dataset} cases found in the data. Skipping document litigation."
        )
        return []

    if not document_media:
        click.echo(
            "🛑 No document media provided in the data. Skipping document litigation."
        )

    document_pdf_urls = {
        document["id"]: document["source_url"]
        for document in document_media
        if "id" in document and "source_url" in document
    }

    families = global_cases + us_cases

    document_family_counter = {}
    mapped_documents = []

    for index, family in enumerate(families):
        case_id = family.get("id")
        if not case_id:
            click.echo(
                f"🛑 Skipping mapping documents without case id at index {index}"
            )
            continue

        result = process_family_documents(
            family, case_id, document_pdf_urls, document_family_counter
        )

        if result:
            mapped_documents.extend(result)

    return mapped_documents
