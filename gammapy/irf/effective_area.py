# Licensed under a 3-clause BSD style license - see LICENSE.rst

from __future__ import absolute_import, division, print_function, unicode_literals
from ..utils.nddata import NDDataArray, DataAxis, BinnedDataAxis
import numpy as np
import astropy.units as u
from astropy.table import Table

__all__ = [
    'EffectiveAreaTable',
    'EffectiveAreaTable2D',
    'abramowski_effective_area',
]

class EffectiveAreaTable(NDDataArray):
    """Effective Area Table
    
    **Disclaimer**: This is an experimental class to test the usage of the
    `~gammapy.utils.nddata.NDDataArray` base class. It is meant to replace
    `~gammapy.irf.EffectiveAreaTable` in the future but is currently not used
    anywhere in gammapy.

    Parameters
    -----------
    energy : `~astropy.units.Quantity`, `~gammapy.utils.nddata.BinnedDataAxis`
        Bin edges of energy axis
    data : `~astropy.units.Quantity`
        Effective area
    meta : dict
        Optional meta information,
        supported: ``low_threshold``, ``high_threshold``
    """
    energy = BinnedDataAxis(interpolation_mode='log')
    """Energy Axis"""
    axis_names = ['energy']

    @property
    def low_threshold(self):

        """Low energy threshold"""
        return self.meta.LO_THRES * u.TeV

    @property
    def high_threshold(self):
        """High energy threshold"""
        return self.meta.HI_THRES * u.TeV

    def plot(self, ax=None, energy=None, show_threshold=False, **kwargs):
        """Plot effective area

        Parameters
        ----------
        ax : `~matplolib.axes`, optional
            Axis
        energy : `~astropy.units.Quantity`
            Energy nodes 
        show_safe_energy : bool
            Show safe energy range on the plot

        Returns
        -------
        ax : `~matplolib.axes`
            Axis

        """
        import matplotlib.pyplot as plt
        ax = plt.gca() if ax is None else ax

        kwargs.setdefault('lw', 2)

        if energy is None:
            energy = self.energy.nodes
        eff_area = self.evaluate(energy=energy)

        ax.plot(energy, eff_area, **kwargs)
        if show_threshold:
            ymin, ymax = ax.get_ylim()
            line_kwargs = dict(lw=2, color='black')
            ax.vlines(self.energy_thresh_lo.value, ymin, ymax, linestyle='dashed',
                      label='Low energy threshold {:.2f}'.format(self.energy_thresh_lo),
                      **line_kwargs)
            ax.vlines(self.energy_thresh_hi.value, ymin, ymax, linestyle='dotted',
                      label='High energy threshold {:.2f}'.format(self.energy_thresh_hi),
                      **line_kwargs)
            ax.legend(loc='upper left')

        ax.set_xscale('log')
        ax.set_xlabel('Energy [{}]'.format(self.energy.unit))
        ax.set_ylabel('Effective Area [{}]'.format(self.data.unit))

        return ax
    
    @classmethod
    def from_table(cls, table):
        """ARF reader"""
        energy_col = 'ENERG'
        data_col = 'SPECRESP'

        energy_lo = table['{}_LO'.format(energy_col)].quantity
        energy_hi = table['{}_HI'.format(energy_col)].quantity
        energy = np.append(energy_lo.value, energy_hi[-1].value) * energy_lo.unit
        data = table['{}'.format(data_col)].quantity
        return cls(energy=energy, data=data)

    def to_table(self):
        """Convert to `~astropy.table.Table`

        http://gamma-astro-data-formats.readthedocs.io/en/latest/ogip/index.html#arf-file 
        """
        ener_lo = self.energy.data[:-1]
        ener_hi = self.energy.data[1:]
        names = ['ENERG_LO', 'ENERG_HI', 'SPECRESP']
        meta = dict(name='SPECRESP', hduclass='OGIP', hduclas1='RESPONSE',
                    hduclas2='SPECRESP')
        meta.update(LO_THRES=self.low_threshold.to('TeV').value)
        meta.update(HI_THRES=self.high_threshold.to('TeV').value)
        return Table([ener_lo, ener_hi, self.data], names=names, meta=meta)


class EffectiveAreaTable2D(NDDataArray):
    """2D Effective Area Table

    **Disclaimer**: This is an experimental class to test the usage of the
    `~gammapy.utils.nddata.NDDataArray` base class. It is meant to replace
    `~gammapy.irf.EffectiveAreaTable2D` in the future but is currently not used
    anywhere in gammapy.

    Parameters
    -----------
    energy : `~astropy.units.Quantity`, `~gammapy.utils.nddata.BinnedDataAxis`
        Bin edges of energy axis
    offset : `~astropy.units.Quantity`, `~gammapy.utils.nddata.DataAxis`
        Nodes of Offset axis

    data : `~astropy.units.Quantity`
        Effective area

    meta : dict
        Optional meta information,
        supported: ``low_threshold``, ``high_threshold``

    Examples
    --------
    Create `~gammapy.irf.EffectiveAreaTable2D` from scratch

    >>> from gammapy.irf import EffectiveAreaTable2D
    >>> import astropy.units as u
    >>> import numpy as np
    >>> energy = np.logspace(0,1,11) * u.TeV
    >>> offset = np.linspace(0,1,4) * u.deg
    >>> data = np.ones(shape=(10,4)) * u.cm * u.cm
    >>> eff_area = EffectiveAreaTable2D(energy=energy, offset=offset, data= data)
    >>> print(eff_area)
    Data array summary info
    energy         : size =    11, min =  1.000 TeV, max = 10.000 TeV
    offset         : size =     4, min =  0.000 deg, max =  1.000 deg
    Data           : size =    40, min =  1.000 cm2, max =  1.000 cm2
    """

    energy = BinnedDataAxis(interpolation_mode='log')
    """Primary axis: Energy"""
    offset = DataAxis()
    """Secondary axis: Offset from pointing position"""
    axis_names = ['energy', 'offset']

    @property
    def low_threshold(self):

        """Low energy threshold"""
        return self.meta.LO_THRES * u.TeV

    @property
    def high_threshold(self):
        """High energy threshold"""
        return self.meta.HI_THRES * u.TeV

    @classmethod
    def from_table(cls, table):
        """This is a reader for the format specified at
        http://gamma-astro-data-formats.readthedocs.io/en/latest/irfs/effective_area/index.html#aeff-2d-format
        """
        energy_col = 'ENERG'
        offset_col = 'THETA'
        data_col = 'EFFAREA'

        energy_lo = table['{}_LO'.format(energy_col)].quantity[0]
        energy_hi = table['{}_HI'.format(energy_col)].quantity[0]
        energy = np.append(energy_lo.value, energy_hi[-1].value) * energy_lo.unit
        offset = table['{}_HI'.format(offset_col)].quantity[0]
        # see https://github.com/gammasky/hess-host-analyses/issues/32
        data = table['{}'.format(data_col)].quantity[0].transpose()
        return cls(offset=offset, energy=energy, data=data, meta=table.meta)

    def to_effective_area_table(self, offset, energy=None):
        """Evaluate at a given offset and return `~gammapy.irf.EffectiveAreaTable` 

        Parameters
        ----------
        offset : `~astropy.coordinates.Angle`
            Offset
        energy : `~astropy.units.Quantity`
            Energy axis bin edges
        """
        if energy is None:
            energy = self.energy
        else:
            energy = BinnedDataAxis(data=energy, interpolation_mode='log')

        area = self.evaluate(offset=offset, energy=energy.nodes)
        copy_keys = ['LO_THRES', 'HI_THRES']
        meta = dict((key, self.meta[key]) for key in copy_keys)
        return EffectiveAreaTable(energy=energy.data, data=area, meta=meta)

    def plot_energy_dependence(self, ax=None, offset=None, energy=None, **kwargs):
        """Plot effective area versus energy for a given offset.

        Parameters
        ----------
        ax : `~matplolib.axes`, optional
            Axis
        offset : `~astropy.coordinates.Angle`
            Offset
        energy : `~astropy.units.Quantity`
            Energy axis
        kwargs : dict
            Forwarded tp plt.plot()

        Returns
        -------
        ax : `~matplolib.axes`

            Axis
        """
        import matplotlib.pyplot as plt

        ax = plt.gca() if ax is None else ax

        if offset is None:
            off_min, off_max = self.offset.nodes[[0, -1]].value
            offset = np.linspace(off_min, off_max, 4) * self.offset.unit

        if energy is None:
            energy = self.energy.nodes

        for off in offset:
            area = self.evaluate(offset=off, energy=energy)
            label = 'offset = {:.1f}'.format(off)
            ax.plot(energy, area.value, label=label, **kwargs)

        ax.set_xscale('log')
        ax.set_xlabel('Energy [{0}]'.format(self.energy.unit))
        ax.set_ylabel('Effective Area [{0}]'.format(self.data.unit))
        ax.set_xlim(min(energy.value), max(energy.value))
        ax.legend(loc='upper left')

        return ax

    def plot_offset_dependence(self, ax=None, offset=None, energy=None, **kwargs):
        """Plot effective area versus offset for a given energy

        Parameters
        ----------
        ax : `~matplolib.axes`, optional
            Axis
        offset : `~astropy.coordinates.Angle`
            Offset axis
        energy : `~gammapy.utils.energy.Energy`
            Energy

        Returns
        -------
        ax : `~matplolib.axes`
            Axis
        """
        import matplotlib.pyplot as plt

        ax = plt.gca() if ax is None else ax

        if energy is None:
            e_min, e_max = np.log10(self.energy.nodes[[0, -1]].value)
            energy = np.logspace(e_min, e_max, 4) * self.energy.unit

        if offset is None:
            off_lo, off_hi = self.offset.nodes[[0, -1]].to('deg').value
            offset = np.linspace(off_lo, off_hi, 100) * u.deg

        for ee in energy:
            area = self.evaluate(offset=offset, energy=ee)
            area /= np.nanmax(area)
            if np.isnan(area).all():
                continue
            label = 'energy = {:.1f}'.format(ee)
            ax.plot(offset, area, label=label, **kwargs)

        ax.set_ylim(0, 1.1)
        ax.set_xlabel('Offset ({0})'.format(self.offset.unit))
        ax.set_ylabel('Relative Effective Area')
        ax.legend(loc='best')

        return ax

    def plot_image(self, ax=None, offset=None, energy=None, **kwargs):
        """Plot effective area image. 
        """
        import matplotlib.pyplot as plt

        kwargs.setdefault('cmap', 'afmhot')
        kwargs.setdefault('origin', 'bottom')
        kwargs.setdefault('interpolation', 'nearest')

        ax = plt.gca() if ax is None else ax

        if offset is None:
            vals = self.offset.nodes.value
            offset = np.linspace(vals.min(), vals.max(), 100)
            offset = offset * self.offset.unit

        if energy is None:
            vals = np.log10(self.energy.nodes.value)
            energy = np.logspace(vals.min(), vals.max(), 100) * self.energy.unit

        aeff = self.evaluate(offset=offset, energy=energy)
        extent = [
            offset.value.min(), offset.value.max(),
            energy.value.min(), energy.value.max(),
        ]
        ax.imshow(aeff.value, extent=extent, **kwargs)

        ax.set_yscale('log')
        ax.set_xlabel('Offset ({0})'.format(offset.unit))
        ax.set_ylabel('Energy ({0})'.format(energy.unit))

        ax.set_title('Effective Area ({0})'.format(aeff.unit))

        ax.legend()

        return ax

    def peek(self, figsize=(15, 5)):
        """Quick-look summary plots."""
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=figsize)
        self.plot_image(ax=axes[0])
        self.plot_energy_dependence(ax=axes[1])
        self.plot_offset_dependence(ax=axes[2])
        plt.tight_layout()
        plt.show()
        return fig


def abramowski_effective_area(energy, instrument='HESS'):
    """IACT effective area parametrization

    Parametrizations of the effective areas of different Cherenkov telescopes
    taken from Appendix B of Abramowski et al. (2010), see
    http://adsabs.harvard.edu/abs/2010MNRAS.402.1342A .

    .. math::
        A_{eff}(E) = g_1 \\left(\\frac{E}{\\mathrm{MeV}}\\right)^{-g_2}\\exp{\\left(-\\frac{g_3}{E}\\right)}

    Parameters
    ----------
    energy : `~astropy.units.Quantity`
        Energy
    instrument : {'HESS', 'HESS2', 'CTA'}
        Instrument name

    Returns
    -------
    effective_area : `~astropy.units.Quantity`
        Effective area in cm^2
    """
    # Put the parameters g in a dictionary.
    # Units: g1 (cm^2), g2 (), g3 (MeV)
    # Note that whereas in the paper the parameter index is 1-based,
    # here it is 0-based
    pars = {'HESS': [6.85e9, 0.0891, 5e5],
            'HESS2': [2.05e9, 0.0891, 1e5],
            'CTA': [1.71e11, 0.0891, 1e5]}

    energy = energy.to('MeV').value

    if instrument not in pars.keys():
        ss = 'Unknown instrument: {0}\n'.format(instrument)
        ss += 'Valid instruments: HESS, HESS2, CTA'
        raise ValueError(ss)

    g1 = pars[instrument][0]
    g2 = pars[instrument][1]
    g3 = -pars[instrument][2]
    value = g1 * energy ** (-g2) * np.exp(g3 / energy)
    return value * u.cm * u.cm
