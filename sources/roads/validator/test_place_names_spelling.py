"""
This test verifies common lexicographic errors in roads list.
"""
import re
from thefuzz import process

import pandas
import pytest

from core.roads.parser import parse

from helpers import iterrecords
from sources.roads.validator.conftest import get_roads_df


@pytest.hookimpl
def pytest_generate_tests(metafunc):
    dataframe = get_roads_df()
    metafunc.parametrize(
        ("metadata",), [(record,) for record in iterrecords(dataframe)]
    )


def test_parse_road_name(metadata: dict, koatotg: pandas.DataFrame, roads_df: pandas.DataFrame):
    """
    This test is triky. It splits the road name into parts and tries to verify each of those.

    - part which references to the other road must keep reference valid, so
      the referenced road must exist in the lists
    - part which references to the locality must be in koatotg list

    fixme: koatotg search must include administrative name and not only locality name
    """

    # todo: lot of roads still have different tricky names that parser does not understand
    excludes = re.compile(
        '(.*держкордон.*)|'
        '(.*ід’їзд.*)|'
        '(.*Об’їзд.*)|'
        '(.*станція.*)|'
        '(.*Станція.*)'
        '(.*межа району.*)|'
        '(.*дитячий табір.*)|'
        '(.*на м.*)|'
        '(.*через .*)|'
        '(.*завод .*)|'
        '(.*онтрольно-пропускний пункт.*)|'
        '(.*з під’їздом до.*)'
        '(.*з під\'їзд.*)'
    )

    for token in parse(metadata['name']):
        if token['type'] == 'ref':
            assert not roads_df[roads_df['ref'] == token['value']].empty, (
                    "Referenced road ref=%s must be present in the lists" % token['value'])
        elif token['type'] == 'place':
            if excludes.match(token['value']):
                continue

            closest_results = process.extract(token['value'], list(koatotg.index.to_list()), limit=2)
            if not closest_results:
                assert False, "Place reference '%s' must be in koatotg" % token['value']

            closest, rate = closest_results[0]
            if rate == 100:
                assert True, "Place reference '%s' match koatotg record '%s'" % (
                    token['value'], closest)
            else:
                assert False, "Place reference '%s' does not have koatotg record, closest match(es): '%s'" % (
                    token['value'], ','.join((name for name, _ in closest_results)))
