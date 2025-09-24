from litigation_data_mapper.parsers.helpers import sort_documents_by_file_id


def test_sorts_documents_by_file_id():
    docs = [
        {"ccl_file": 3, "title": "Doc 3"},
        {"ccl_file": 56, "title": "Doc None"},
        {"ccl_file": 1, "title": "Doc 1"},
        {"ccl_file": 7, "title": "Doc Empty"},
        {"ccl_file": 2, "title": "Doc 2"},
    ]
    sorted_docs = sort_documents_by_file_id(docs, case_type="case")
    sorted_ids = [doc["ccl_file"] for doc in sorted_docs]
    assert sorted_ids == [1, 2, 3, 7, 56]


def test_sorts_documents_with_missing_file_ids():
    docs = [
        {"ccl_file": None, "title": "Doc None"},
        {"ccl_file": 5, "title": "Doc 5"},
        {"ccl_file": "", "title": "Doc Empty"},
        {"ccl_file": 2, "title": "Doc 2"},
        {"ccl_file": 10, "title": "Doc 10"},
    ]
    sorted_docs = sort_documents_by_file_id(docs, case_type="case")
    sorted_ids = [doc["ccl_file"] for doc in sorted_docs]
    assert sorted_ids == [None, "", 2, 5, 10]


def test_sorts_documents_all_missing_file_ids():
    docs = [
        {"ccl_file": None, "title": "Doc None 1"},
        {"ccl_file": "", "title": "Doc Empty 1"},
        {"ccl_file": None, "title": "Doc None 2"},
        {"ccl_file": "", "title": "Doc Empty 2"},
    ]
    sorted_docs = sort_documents_by_file_id(docs, case_type="case")
    sorted_ids = [doc["ccl_file"] for doc in sorted_docs]
    assert sorted_ids == [None, "", None, ""]


def test_sorts_documents_for_non_us_case():
    docs = [
        {"ccl_nonus_file": 4, "title": "Doc 4"},
        {"ccl_nonus_file": 1, "title": "Doc 1"},
        {"ccl_nonus_file": None, "title": "Doc None"},
        {"ccl_nonus_file": 3, "title": "Doc 3"},
        {"ccl_nonus_file": "", "title": "Doc Empty"},
    ]
    sorted_docs = sort_documents_by_file_id(docs, case_type="non-case")
    sorted_ids = [doc["ccl_nonus_file"] for doc in sorted_docs]
    assert sorted_ids == [None, "", 1, 3, 4]
