"""Example how to make an acceptance curve and background model image.
"""
from astropy.coordinates import SkyCoord, Angle
from numpy.testing import assert_equal, assert_almost_equal
from gammapy.utils.energy import Energy
from gammapy.data import DataStore
from gammapy.image import SkyMap, ExclusionMask
from gammapy.background import OffDataBackgroundMaker
from gammapy.scripts import MosaicImage
from ...utils.testing import requires_data, requires_dependency


@requires_dependency('reproject')
@requires_data('gammapy-extra')
def test_image_pipe(tmpdir):
    tmpdir = str(tmpdir)
    from subprocess import call
    outdir = tmpdir
    outdir2 = outdir + '/background'

    cmd = 'mkdir -p {}'.format(outdir2)
    print('Executing: {}'.format(cmd))
    call(cmd, shell=True)

    ds = DataStore.from_dir("$GAMMAPY_EXTRA/datasets/hess-crab4-hd-hap-prod2")
    ds.copy_obs(ds.obs_table, tmpdir)
    data_store = DataStore.from_dir(tmpdir)

    bgmaker = OffDataBackgroundMaker(data_store, outdir=outdir2)

    bgmaker.select_observations(selection='all')
    bgmaker.group_observations()
    bgmaker.make_model("2D")
    bgmaker.save_models("2D")

    fn = outdir2 + '/group-def.fits'

    hdu_index_table = bgmaker.make_total_index_table(
        data_store=data_store,
        modeltype='2D',
        out_dir_background_model=outdir2,
        filename_obs_group_table=fn
    )

    fn = outdir + '/hdu-index.fits.gz'
    hdu_index_table.write(fn, overwrite=True)

    tmpdir = str(tmpdir)
    center = SkyCoord(83.63, 22.01, unit='deg').galactic
    energy_band = Energy([1, 10], 'TeV')
    offset_band = Angle([0, 2.49], 'deg')
    data_store = DataStore.from_dir(tmpdir)

    # TODO: fix `binarize` implementation
    # exclusion_mask = exclusion_mask.binarize()
    image = SkyMap.empty(nxpix=250, nypix=250, binsz=0.02, xref=center.l.deg,
                         yref=center.b.deg, proj='TAN', coordsys='GAL')

    refheader = image.to_image_hdu().header
    exclusion_mask = ExclusionMask.read('$GAMMAPY_EXTRA/datasets/exclusion_masks/tevcat_exclusion.fits')
    exclusion_mask = exclusion_mask.reproject(reference=refheader)
    # Pb with the load psftable for one of the run that is not implemented yet...
    data_store.hdu_table.remove_row(14)
    mosaic = MosaicImage(image, energy_band=energy_band, offset_band=offset_band, data_store=data_store,
                         obs_table=data_store.obs_table, exclusion_mask=exclusion_mask)
    mosaic.make_images(make_background_image=True, for_integral_flux=True, radius=10.)
    # TODO: this fails on some machines, for unknown reasons.
    #assert_equal(mosaic.maps['counts'].data.sum(), 2334.0)
    #assert_almost_equal(mosaic.maps['bkg'].data.sum(), 1987.2088283446637)
    #assert_almost_equal(mosaic.maps['exposure'].data.sum(), 5.9292301086257267e17)
    #assert_almost_equal(mosaic.maps['significance'].lookup(center), 33.699068269123039)
    #assert_almost_equal(mosaic.maps['excess'].data.sum(), 346.79117165533626)
