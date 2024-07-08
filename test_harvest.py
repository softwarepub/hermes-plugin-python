import pytest
from hermes_toml import harvest

@pytest.mark.parametrize("input, output", [
    ({"givenName": "Tom"}, {"givenName": "Tom"}), ({"a": "b"}, {}), 
    ({"givenName": "Tom","a": "b"}, {"givenName": "Tom"}), ({}, {})
])
def test_remove_forbidden_keys(input, output):
    assert harvest.remove_forbidden_keys(input) == output

@pytest.mark.parametrize("input, output", [
    ({"givenName": "Tom"}, {"givenName": "Tom"}), ({"a": "b"}, {}), 
    ({"givenName": "Tom","a": "b"}, {"givenName": "Tom"}), ({}, {}),
    ([{"givenName": "Tom"}], [{"givenName": "Tom"}]), 
    ([{"givenName": "Tom"}, {"a": "b"}], [{"givenName": "Tom"}]),
    ([{}, {"givenName": "Tom"}, {"a": "b"}], [{"givenName": "Tom"}]),
    ([{}], []), ([{"b":"c"}], []), ([], [])
])
def test_handle_person(input, output):
    assert harvest.handle_person_in_unknown_format(input) == output

@pytest.mark.parametrize("input", [
    (("a")), ("a"), (15), ([{}, ("a")]), (["a"])
])
def test_handle_person_with_error(input):
    with pytest.raises(ValueError):
        harvest.handle_person_in_unknown_format(input)