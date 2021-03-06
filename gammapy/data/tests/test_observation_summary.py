# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
from numpy.testing import assert_allclose
from astropy.tests.helper import pytest
from astropy.coordinates import SkyCoord
from ...data import DataStore, ObservationTableSummary
from ...utils.testing import requires_data, requires_dependency


@requires_data('gammapy-extra')
@pytest.fixture
def summary():
    data_store = DataStore.from_dir('$GAMMAPY_EXTRA/datasets/hess-crab4-hd-hap-prod2/')
    target_pos = SkyCoord(83.633083, 22.0145, unit='deg')
    return ObservationTableSummary(data_store.obs_table, target_pos)


@requires_data('gammapy-extra')
def test_str(summary):
    text = str(summary)
    assert ('Observation summary' in text)


@requires_data('gammapy-extra')
def test_offset(summary):
    offset = summary.offset
    assert_allclose(offset.degree.mean(), 1., rtol=1.e-2)
    assert_allclose(offset.degree.std(), 0.5, rtol=1.e-2)


@requires_data('gammapy-extra')
@requires_dependency('matplotlib')
def test_plot_zenith(summary):
    summary.plot_zenith_distribution()


@requires_data('gammapy-extra')
@requires_dependency('matplotlib')
def test_plot_offset(summary):
    summary.plot_offset_distribution()
