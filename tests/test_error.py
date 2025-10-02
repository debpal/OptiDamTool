import OptiDamTool
import pytest
import os


@pytest.fixture(scope='class')
def network():

    yield OptiDamTool.Network()


@pytest.fixture(scope='class')
def analysis():

    yield OptiDamTool.Analysis()


@pytest.fixture(scope='class')
def visual():

    yield OptiDamTool.Visual()


@pytest.fixture(scope='class')
def system_design():

    yield OptiDamTool.SystemDesign()


def test_error_netwrok(
    network
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # Error: invalid dam list type
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list={}
        )
    assert exc_info.value.args[0] == 'Expected "dam_list" to be "list", but got type "dict"'

    # Error: same stream identifiers in the input dam list
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_downstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 31, 17, 24, 27, 2, 13, 1]
        )
    assert exc_info.value.args[0] == 'Duplicate stream identifiers found in the input dam list'

    # Error: invalid stream identifier
    with pytest.raises(Exception) as exc_info:
        network.connectivity_adjacent_upstream_dam(
            stream_file=os.path.join(data_folder, 'stream_lines.shp'),
            dam_list=[21, 22, 5, 31, 17, 24, 27, 2, 13, 1, 34]
        )
    assert exc_info.value.args[0] == 'Invalid stream identifier 34 for a dam'

    # Error: mismatch of keys between storage and drainage area dictionaries
    with pytest.raises(Exception) as exc_info:
        network.trap_efficiency_brown(
            storage_dict={5: 1},
            area_dict={6: 1}
        )
    assert exc_info.value.args[0] == 'Mismatch of keys between storage and area dictionaries'

    # Error: invalid folder path for storage dynamics
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            folder_path='tmp_dir'
        )
    assert exc_info.value.args[0] == 'Input folder_path is not valid'

    # Error: invalid variable type which is not union
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=[]
        )
    assert exc_info.value.args[0] == 'Expected "trap_equation" to be "bool", but got type "list"'

    # Error: invalid vartiable type which is a unionfor storage dynamics detailed version
    typ_args = ['str', 'NoneType']
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            folder_path=1
        )
    assert exc_info.value.args[0] == f'Expected "folder_path" to be one of {typ_args}, but got type "int"'

    # Error: invalid storage volume value
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: -10},
            year_limit=15,
            sediment_density=1300
        )
    assert exc_info.value.args[0] == 'Invalid negative intial storage volume -10 for the dam identifier 15 was received'

    # Error: invalid year limit value
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=-1,
            sediment_density=1300
        )
    assert exc_info.value.args[0] == 'year_limit must be greater than 0, but received -1'

    # Error: invalid trap constant type when trap_equation=False
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False
        )
    assert exc_info.value.args[0] == 'trap_constant must be a numeric value when "trap_equation=False", but got type "NoneType"'

    # Error: invalid trap constant value
    with pytest.raises(Exception) as exc_info:
        network.stodym_plus(
            stream_file='stream_sediment_delivery.shp',
            storage_dict={15: 2000000},
            year_limit=15,
            sediment_density=1300,
            trap_equation=False,
            trap_constant=0.05
        )
    assert exc_info.value.args[0] == 'trap_constant 0.05 is invalid: must satisfy trap_threshold (0.1) < trap_constant <= 1'


def test_error_analysis(
    analysis
):

    # Error: JSON file extension
    with pytest.raises(Exception) as exc_info:
        analysis.sediment_delivery_to_stream_json(
            info_file='stream_information.txt',
            segsed_file='Total sediment segments.txt',
            cumsed_file='Cumulative sediment segments.txt',
            json_file='stream_sediment_delivery.txt'
        )
    assert exc_info.value.args[0] == 'Output "json_file" path must have a valid JSON file extension'

    # Error: GeoJSON file extension
    with pytest.raises(Exception) as exc_info:
        analysis.sediment_delivery_to_stream_geojson(
            stream_file='stream_lines.shp',
            sediment_file='stream_sediment_delivery.txt',
            geojson_file='stream_sediment_delivery.shp'
        )
    assert exc_info.value.args[0] == 'Output file path must have a valid GeoJSON file extension'

    # Error: invaid sorting option of non dominated solutions
    valid_options = [
        'dam_identifiers',
        'metric_euclidean',
        'objective_directions'
    ]
    with pytest.raises(Exception) as exc_info:
        analysis.nondominated_solution_sorting(
            input_file='input_json',
            sorting_by='non_existence_option',
            output_file='output.json'
        )
    assert exc_info.value.args[0] == f'Invalid solution_sorting name "non_existence_option"; valid names are {valid_options}'


def test_error_visual(
    visual
):

    # Error: invaid figure file extension
    with pytest.raises(Exception) as exc_info:
        visual.sediment_inflow_to_stream(
            stream_file='stream.geojson',
            figure_file='sediment_inflow_to_stream.pn'
        )
    assert exc_info.value.args[0] == 'Input figure_file extension ".pn" is not supported for saving the figure'

    # Error: all plot options are set to False for system statistics
    with pytest.raises(Exception) as exc_info:
        visual.system_statistics(
            json_file='system_statistics.json',
            figure_file='system_statistics.png',
            plot_storage=False,
            plot_trap=False,
            plot_release=False,
            plot_drainage=False
        )
    assert exc_info.value.args[0] == 'At least one plot type must be set to True'


def test_error_systemdesign(
    system_design
):

    # data folder
    data_folder = os.path.join(os.path.dirname(__file__), 'data')

    # stream file
    stream_file = os.path.join(data_folder, 'stream_with_sediment.geojson')

    # input varilables
    dam_number = 5
    storage_bounds = (1, 50)
    storage_multiplier = 50000
    algorithm_config = {
        'population_size': 10
    }
    seeds = 2
    objs_dirs = system_design.mapping_objective_direction
    constrs_ops = system_design.mapping_constraint_operator

    # Error: storage_bounds length greater than 2
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=(1, 50, 100),
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'storage_bounds must contain exactly 2 integers, but received 3 elements'

    # Error: invalid value type in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=(1.5, 50),
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'Each value in storage_bounds must be an integer, but got 1.5 of type "float"'

    # Error: value less than 1 in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=(0, 50),
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'Each value in storage_bounds must be greater than or equal to 1, but received 0'

    # Error: minimum is greater than maximum in storage_bounds
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=(10, 5),
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'The lower bound 10 must be strictly less than the upper bound 5 in storage_bounds'

    # Error: storage_multiplier less than 0
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=storage_bounds,
            storage_multiplier=-1000,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'storage_multiplier must be greater than 0, but received -1000'

    # Error: dam number cannot be exceeded stream segments
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=50,
            storage_bounds=storage_bounds,
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )
    assert exc_info.value.args[0] == 'dam_number 50 is out of range; expected 1 <= dam_number < 33'

    # Error: invaid seed number
    with pytest.raises(Exception) as exc_info:
        system_design._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=storage_bounds,
            storage_multiplier=storage_multiplier,
            seeds=-2
        )
    assert exc_info.value.args[0] == 'Input seeds must be greater than or equal to 1, but received -2'

    # Error: invalid stodym_config key type
    with pytest.raises(Exception) as exc_info:
        system_design._validate_stodym_kwargs(
            stodym_config={1: 5}
        )
    assert exc_info.value.args[0] == 'Key "1" in stodym_config must be a string, but got type "int"'

    # Error: invalid stodym_config key name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_stodym_kwargs(
            stodym_config={'invalid_key': 5}
        )
    assert 'Invalid key "invalid_key" in stodym_config' in exc_info.value.args[0]

    # Error: required key in stodym_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_stodym_kwargs(
            stodym_config={'year_limit': 5}
        )
    assert exc_info.value.args[0] == 'Required key "sediment_density" is missing from stodym_config'

    # Error: invalid genetic algorithm name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGA5',
            algorithm_config=algorithm_config
        )
    assert 'Invalid algorithm name "NSGA5"' in exc_info.value.args[0]

    # Error: invalid keyword in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGAII',
            algorithm_config={'invalid_key': 1}
        )
    assert 'Invalid key "invalid_key" in algorithm_config' in exc_info.value.args[0]

    # Error: required key in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='NSGAII',
            algorithm_config={'archive': []}
        )
    assert exc_info.value.args[0] == 'Missing required key "population_size" in algorithm_config'

    # Error: invalid value type of required key in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='MOEAD',
            algorithm_config={'population_size': '10'}
        )
    assert exc_info.value.args[0] == 'Value for "population_size" must be an integer, but got type "str"'

    # Error: invalid epsilons value in algorithm_config
    with pytest.raises(Exception) as exc_info:
        system_design._validate_algorithm_config(
            algorithm_name='EpsNSGAII',
            algorithm_config={
                'population_size': 10,
                'epsilons': 3
            }
        )
    assert exc_info.value.args[0] == 'Value for "epsilons" must be between 0 and 1, but got "3"'

    # Error: invalid objective name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_objectives(
            objectives=['no_lifespan'],
            objs_dirs=objs_dirs
        )
    assert 'Invalid objective "no_lifespan"' in exc_info.value.args[0]

    # Error: empty objective list
    with pytest.raises(Exception) as exc_info:
        system_design._validate_objectives(
            objectives=[],
            objs_dirs=objs_dirs
        )
    assert exc_info.value.args[0] == '"objectives" cannot be an empty list'

    # Error: duplicate name in objective list
    with pytest.raises(Exception) as exc_info:
        duplicate_objectives = ['lifespan'] * 2
        system_design._validate_objectives(
            objectives=duplicate_objectives,
            objs_dirs=objs_dirs
        )
    assert exc_info.value.args[0] == f'Duplicate names found in objective list: {duplicate_objectives}'

    # Error: empty constraint dictionary
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={},
            constrs_ops=constrs_ops
        )
    assert exc_info.value.args[0] == '"constraints" cannot be an empty dictionary'

    # Error: invalid contraint name
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={'invalid_constraint': 1},
            constrs_ops=constrs_ops
        )
    assert 'Invalid constraint "invalid_constraint"' in exc_info.value.args[0]

    # Error: invalid constraint dictionary value type
    with pytest.raises(Exception) as exc_info:
        system_design._validate_constraints(
            constraints={'lb_lifespan': '1'},
            constrs_ops=constrs_ops
        )
    assert exc_info.value.args[0] == 'Value of key "lb_lifespan" in "constraints" must be numeric, but got type "str"'
