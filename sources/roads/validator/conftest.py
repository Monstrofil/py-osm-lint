import functools
import glob
import os

import numpy as np
import pandas
import pytest

from helpers import dataset

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _iterrecords(data: pandas.DataFrame) -> list:
    for index, row in data.iterrows():
        yield row


def _dataset(path) -> pandas.DataFrame:
    dataset = pandas.read_csv(
        path,
        converters={
            'district': lambda x: np.array(x.split(','), dtype='str'),
            'distance': lambda x: np.real(x),
            'uid': lambda x: np.uint64(x)
        })
    dataset['filename'] = os.path.basename(path)
    return dataset


def get_roads_df() -> pandas.DataFrame:
    return functools.reduce(
        lambda x, y: pandas.concat([x, y]),
        map(dataset, glob.glob(BASE_DIR + '/../csv/*.csv'))
    )


@pytest.fixture(scope='session')
def koatotg():
    yield dataset(
        os.path.join(BASE_DIR, 'static/koatotg.csv')
    ).set_index('name')


@pytest.fixture(scope='session')
def roads_df():
    yield get_roads_df()
