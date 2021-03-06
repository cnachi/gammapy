# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
from ...utils.testing import requires_data
from ..hess import SourceCatalogHGPS


@requires_data('hgps')
class TestSourceCatalogHGPS:
    def setup(self):
        self.cat = SourceCatalogHGPS()
        self.cat.hdu_list.info()

    def test_source_table(self):
        assert self.cat.name == 'hgps'
        assert len(self.cat.table) == 78

    def test_component_table(self):
        assert len(self.cat.components) == 98

    def test_associations_table(self):
        assert len(self.cat.associations) == 223


@requires_data('hgps')
class TestSourceCatalogObjectHGPS:
    def setup(self):
        self.cat = SourceCatalogHGPS()
        # Use HESS J1825-137 as a test source
        self.source_name = 'HESS J1825-137'
        self.source = self.cat[self.source_name]

    def test_single_gauss(self):
        source = self.cat['HESS J1930+188']
        assert source.data['Spatial_Model'] == 'Gaussian'
        assert 'Spatial components   : HGPSC 097' in str(source)

    def test_multi_gauss(self):
        source = self.cat['HESS J1825-137']
        assert source.data['Spatial_Model'] == '3-Gaussian'
        assert 'Spatial components   : HGPSC 065, HGPSC 066, HGPSC 067' in str(source)

    def test_snr(self):
        source = self.cat['HESS J1713-397']
        assert source.data['Spatial_Model'] == 'Shell'
        assert 'Source name          : HESS J1713-397' in str(source)

    def test_name(self):
        assert self.source.name == self.source_name

    def test_index(self):
        assert self.source.index == 54

    def test_data(self):
        data = self.source.data
        assert data['Source_Class'] == 'PWN'

    def test_pprint(self):
        self.source.pprint()

    def test_str(self):
        ss = self.source.__str__()
        assert 'Source name          : HESS J1825-137' in ss
        assert 'Component HGPSC 065:' in ss

    def test_spectrum(self):
        source = self.cat['HESS J1825-137']
        reference = ('Fit result info \n--------------- \nModel: PowerLaw'
                     ' \nParameters: \n\t index     : 2.38 +/- 0.03 \n\t norm'
                     '      : (17.17 +/- 0.57) x 1e-12 / (cm2 s TeV)\n\t reference'
                     ' : 1.16 +/- 0.00 TeV\n')

        assert str(source.spectrum) == reference
