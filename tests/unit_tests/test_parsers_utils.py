from litigation_data_mapper.parsers.utils import convert_to_dmy


def test_convert_to_dmy_handles_only_year_provided():
    assert convert_to_dmy("2001") == "2001-01-01"


def test_convert_to_dmy_returns_none_on_error():
    assert convert_to_dmy("") is None


def test_convert_to_dmy_handles_full_date():
    assert convert_to_dmy("20010101") == "2001-01-01"
