"""
This test verifies common typing errors in roads list.
"""
import re

import pytest

from helpers import iterrecords
from sources.roads.validator.conftest import get_roads_df


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    dataframe = get_roads_df()
    metafunc.parametrize(
        ("metadata",), [(record, ) for record in iterrecords(dataframe)]
    )


def test_proper_delimited_names(metadata: dict):
    """
    Road name must be a string with zero or more destinations
    delimited by the '–' character surrounded with two spaces one on each side.

    This test makes sure that both spaces are there and users did not forget whitespace.
    """

    not_surrounded_dash = re.search(r'([^\s]–)|(–[^\s])', metadata['name'])

    assert not_surrounded_dash is None, (
            "Dash in the name %s must be surrounded by spaces." % repr(metadata['name']))


def test_hyphen_delimiter(metadata: dict):
    """
    Unlike dash, hyphen is used inside the locality names like "Білгород-Дністровський"
    and so should not be surronded with whitespace
    """
    surrounded_hypten = re.search(r'(\s-)|(-\s)', metadata['name'])
    assert surrounded_hypten is None, (
            "Hyphens in the name %s must NOT be surrounded by whitespace" % repr(metadata['name']))


def test_ref_first_letter(metadata: dict):
    """
    People are lazy and sometimes they use "C" instead of "С" (first one is english one)
    but programs know the difference between those too.

    This test makes sure that first letters of the road ref are correct.
    """
    assert metadata['ref'][0] in [
        "М", "Н", "Р", "Т", "О", "С"
    ], "ref must start with the cyrillic letter within explicit list"


def test_distance_float(metadata: dict):
    """
    Simply check that the distance tag is correct float number and not something weird.
    """

    def is_float(value):
        try:
            float(value)
        except ValueError:
            return False
        return True

    assert is_float(metadata['distance']), \
        f"Distance {metadata['distance']} must be a valid float number"


def test_nbsp(metadata: dict):
    """
    Non-breaking-space is the same as regular one except that it is a different char code.
    """
    assert '\xa0' not in metadata['name'], \
        "nbsp usage in name tag is prohibited"


def test_double_space(metadata: dict):
    """
    Double space is a common mistake.
    """
    assert re.search(r'\s\s', metadata['name']) is None, \
        "double space usage in name tag is prohibited"


def test_road_references_old_format(metadata: dict):
    """
    With new OSM guidelines we propose people use
    М-06 and not /М-06/ as reference to the other road.

    todo: would be great to also handle other formats like (М-06)
    """
    name = metadata['name'].replace('а/д', '')
    assert '/' not in name, "road references must use format X-YY and not /X-YY/"
