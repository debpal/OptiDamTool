import OptiDamTool
import platypus
import pytest
import tempfile
import os


@pytest.fixture(scope='class')
def system_design():

    yield OptiDamTool.SystemDesign()


@pytest.fixture(scope='class')
def analysis():

    yield OptiDamTool.Analysis()


def test_system_design(
    system_design,
    analysis
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:

        # StoDyM+ configuration
        stodym_config = {
            'sediment_density': 1300,
            'year_limit': 100,
            'trap_threshold': 0.05,
            'brown_d': 1
        }

        # objectives
        objectives = [
            'lifespan',
            'lifespan_std',
            'sediment_trapped_initial',
            'sediment_released_median',
            'storage_sum',
            'storage_variability'
        ]

        # constraints
        constraints = {
            'lb_lifespan': 0,
            'ub_storage_sum': 5000000
        }

        # Pass: dam location and storage volume optimization
        output = system_design.sediment_control_by_fixed_dams(
            dam_number=5,
            storage_bounds=(1, 50),
            storage_multiplier=50000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            stodym_config=stodym_config,
            objectives=objectives,
            algorithm_name='NSGAII',
            algorithm_config={
                'population_size': 10
            },
            seeds=2,
            nfe=30,
            folder_path=tmp_dir,
            constraints=constraints
        )
        assert isinstance(output, dict)
        assert len(output) == 2
        assert 'solutions_nondominated' in output
        assert 'computation_statistics' in output
        assert len(output['solutions_nondominated']) <= 20
        assert output['solutions_nondominated'].shape[1] == 26
        assert len(output['computation_statistics']) == 9

        # Pass: sort non-dominated solution by dam identifiers
        df = analysis.nondominated_solution_sorting(
            input_file=os.path.join(tmp_dir, 'solutions_nondominated.json'),
            sorting_by='dam_identifiers',
            output_file=os.path.join(tmp_dir, 'solutions_sorted.json')
        )
        sort_cols = [
            col for col in df.columns if col.startswith('d_')
        ]
        assert df.iloc[0, 1] == df[sort_cols].min().min()

        # Pass: sort non-dominated solution by Euclidean metric
        df = analysis.nondominated_solution_sorting(
            input_file=os.path.join(tmp_dir, 'solutions_nondominated.json'),
            sorting_by='metric_euclidean',
            output_file=os.path.join(tmp_dir, 'solutions_sorted.json')
        )
        sort_cols = [
            col for col in df.columns if col.startswith('metric_euclidean')
        ]
        assert df[sort_cols[0]].iloc[0] == df[sort_cols[0]].min()

        # Pass: sort non-dominated solution by objective directions
        df = analysis.nondominated_solution_sorting(
            input_file=os.path.join(tmp_dir, 'solutions_nondominated.json'),
            sorting_by='objective_directions',
            output_file=os.path.join(tmp_dir, 'solutions_sorted.json')
        )
        sort_cols = [
            col for col in df.columns if col.endswith(('(min)', '(max)'))
        ]
        assert df[sort_cols[0]].iloc[0] == df[sort_cols[0]].max()

        # Pass: code coverage of _scenario_sedimentation_management since it is wrapped by functools.partial
        objs_bounds = system_design._objective_bounds(
            dam_number=5,
            storage_vars=platypus.Integer(1, 50),
            storage_multiplier=10000,
            objectives=objectives,
            stodym_config=stodym_config
        )
        assert isinstance(objs_bounds, dict)
        assert len(objs_bounds) == 6
        assert objectives[0] in objs_bounds

        output = system_design._scenario_sediment_control(
            variables=[[21, 5, 24, 27, 33], 150, 10, 6, 20, 100],
            storage_multiplier=10000,
            stream_file=os.path.join(data_folder, 'stream_with_sediment.geojson'),
            stodym_config=stodym_config,
            objectives=objectives,
            objs_bounds=objs_bounds,
            objs_dirs=system_design.mapping_objective_direction,
            constraints=constraints
        )
        assert isinstance(output, tuple)
        assert len(output) == 2
        assert isinstance(output[0], list)
        assert len(output[0]) == 6
        assert isinstance(output[1], list)
        assert len(output[1]) == 2

        # Pass: CPU number
        output = system_design._cpu_number(
            processes=5
        )
        assert output == 5

        # Error: empty folder_path
        with pytest.raises(Exception) as exc_info:
            OptiDamTool.utility._validate_empty_folder(
                folder_path=tmp_dir
            )
        assert exc_info.value.args[0] == 'Specified folder_path must point to an empty directory'
