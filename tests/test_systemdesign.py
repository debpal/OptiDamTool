import OptiDamTool
import pytest
import tempfile
import os


@pytest.fixture(scope='class')
def system_design():

    yield OptiDamTool.SystemDesign()


def test_system_design(
    system_design
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        # pass test for dam location and storage volume optimization and sorting by objective directions
        output = system_design.solution_sedimentation_management_by_ga(
            dam_number=5,
            storage_bounds=(1, 50),
            storage_multiplier=50000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            model_config={
                'sediment_density': 1300,
                'year_limit': 100,
                'trap_threshold': 0.05,
                'brown_d': 1
            },
            objectives=[
                'lifespan',
                'storage_sum',
            ],
            algorithm_name='NSGAII',
            algorithm_config={
                'population_size': 5
            },
            seeds=2,
            nfe=10,
            folder_path=tmp_dir,
            solution_sorting='by_objective_directions'
        )
        assert isinstance(output, dict)
        assert len(output) == 2
        assert 'solutions_nondominated' in output
        assert 'computation_statistics' in output
        assert len(output['solutions_nondominated']) <= 10
        assert output['solutions_nondominated'].shape[1] == 21
        assert len(output['computation_statistics']) == 9

        # pass test for dam location and storage volume optimization and sorting by dam identifiers
        output = system_design.solution_sedimentation_management_by_ga(
            dam_number=6,
            storage_bounds=(1, 50),
            storage_multiplier=50000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            model_config={
                'sediment_density': 1300,
                'year_limit': 100,
                'trap_threshold': 0.05,
                'brown_d': 1
            },
            objectives=[
                'lifespan',
                'storage_sum',
            ],
            algorithm_name='NSGAII',
            algorithm_config={
                'population_size': 5
            },
            seeds=2,
            nfe=10,
            folder_path=tmp_dir,
            solution_sorting='by_dam_idenfiers'
        )
        assert isinstance(output, dict)
        assert len(output) == 2
        assert 'solutions_nondominated' in output
        assert 'computation_statistics' in output
        assert len(output['solutions_nondominated']) <= 10
        assert output['solutions_nondominated'].shape[1] == 24
        assert len(output['computation_statistics']) == 9

        # pass test for dam location and storage volume optimization and sorting solutions by Euclidean metric
        output = system_design.solution_sedimentation_management_by_ga(
            dam_number=5,
            storage_bounds=(1, 50),
            storage_multiplier=50000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            model_config={
                'sediment_density': 1300,
                'year_limit': 100,
                'trap_threshold': 0.05,
                'brown_d': 1
            },
            objectives=[
                'lifespan',
                'lifespan_std',
                'sediment_trapped_initial',
                'storage_sum',
                'storage_variability',
                'sediment_released_median'
            ],
            algorithm_name='NSGAII',
            algorithm_config={
                'population_size': 10
            },
            seeds=2,
            nfe=30,
            folder_path=tmp_dir,
            solution_sorting='by_metric_euclidean'
        )
        assert isinstance(output, dict)
        assert len(output) == 2
        assert 'solutions_nondominated' in output
        assert 'computation_statistics' in output
        assert len(output['solutions_nondominated']) <= 20
        assert output['solutions_nondominated'].shape[1] == 25
        assert len(output['computation_statistics']) == 9
        assert os.path.exists(os.path.join(tmp_dir, 'solutions_nondominated.json'))
        assert os.path.exists(os.path.join(tmp_dir, 'computation_statistics.json'))

        # pass test for code coverage of scenario_sedimentation_management since it is wrapped by functools.partial
        output = system_design.scenario_sedimentation_management(
            variables=[[21, 5, 24, 27, 33], 150, 10, 6, 20, 100],
            storage_multiplier=10000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            model_config={
                'sediment_density': 1300,
                'year_limit': 15,
                'trap_threshold': 0.05
            },
            objectives=[
                'lifespan',
                'lifespan_std',
                'sediment_trapped_initial',
                'storage_sum',
                'storage_variability',
                'sediment_released_median'
            ],
            constraints={'lb_lifespan': 0}
        )
        assert isinstance(output, tuple)
        assert len(output) == 2
        assert isinstance(output[0], list)
        assert len(output[0]) == 6
        assert isinstance(output[1], list)
        assert len(output[1]) == 1
