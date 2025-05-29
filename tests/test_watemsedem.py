import pytest
import OptiDamTool


@pytest.fixture(scope='class')
def watemsedem():

    yield OptiDamTool.WatemSedem()


def test_dem_to_stream(
    watemsedem
):

    output = watemsedem.dem_to_stream(
        dem_file='dem.tif',
        folder_path='folder'
    )

    assert output == ['dem.tif', 'folder']


def test_github():

    assert str(1) == '1'
