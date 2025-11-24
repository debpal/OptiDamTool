import geopandas
import pandas
import scipy
import numpy
import platypus
import functools
import inspect
import typing
import os
import time
import datetime
import concurrent.futures
from .network import Network
from . import utility


class SystemDesign:

    '''
    Provide functionality to optimize dam systems by evolutionary computing framework
    `platypus-opt <https://github.com/Project-Platypus/Platypus>`_.
    '''

    def __init__(
        self
    ) -> None:

        '''
        Initialize the class instance with a default attribute ``lifespan_epsilon`` to :math:`10^{-6}`.
        This value serves as a lower bound for dam lifespans (in years) when calculating the
        summation of logarithms of lifespans. It prevents undefined behavior from computing :math:`\\log(0)`
        and ensures that the logarithmic penalty correctly applies to dams with zero or negligible lifespans.
        '''

        self.lifespan_epsilon = pow(10, - 6)

    def _validate_preliminary_config(
        self,
        stream_file: str,
        dam_number: int,
        storage_bounds: tuple[int, int],
        storage_multiplier: float,
        seeds: int
    ) -> list[int]:

        '''
        Validate the input configuration of dams and their storage volumes.
        '''

        # check that storage_bounds has exactly two elements
        if len(storage_bounds) != 2:
            raise ValueError(
                f'storage_bounds must contain exactly 2 integers, but received {len(storage_bounds)} elements'
            )

        # check that each element is a positive integer
        for i in storage_bounds:
            if not isinstance(i, int):
                raise TypeError(
                    f'Each value in storage_bounds must be an integer, but got {i} of type "{type(i).__name__}"'
                )
            if i < 1:
                raise ValueError(
                    f'Each value in storage_bounds must be greater than or equal to 1, but received {i}'
                )

        # Check that the lower bound is strictly less than the upper bound
        if storage_bounds[0] >= storage_bounds[1]:
            raise ValueError(
                f'The lower bound {storage_bounds[0]} must be strictly less than the upper bound {storage_bounds[1]} in storage_bounds'
            )

        # check that storage_multiplier is greater than 0
        if storage_multiplier <= 0:
            raise ValueError(
                f'storage_multiplier must be greater than 0, but received {storage_multiplier}'
            )

        # stream GeoDataFrame
        stream_gdf = geopandas.read_file(
            filename=stream_file
        )

        # list of stream identifiers for dams
        stream_ids = list(stream_gdf['ws_id'])

        # check that dam number is less than length of stream identifiers
        if dam_number >= len(stream_ids):
            raise ValueError(
                f'dam_number {dam_number} is out of range; expected 1 <= dam_number < {len(stream_ids)}'
            )

        # check validity of seeds number
        if seeds <= 0:
            raise ValueError(
                f'Input seeds must be greater than or equal to 1, but received {seeds}'
            )

        return stream_ids

    def _validate_stodym_kwargs(
        self,
        stodym_config: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:

        '''
        Validate the input configuration for the method :meth:`OptiDamTool.Network.stodym_plus`.
        '''

        # dictionary of valid keys
        vars_valid = [
            'sediment_density',
            'year_limit',
            'trap_equation',
            'trap_threshold',
            'brown_d',
            'trap_constant',
            'release_threshold'
        ]

        # check validty of key names and their value types
        for m_key, m_val in stodym_config.items():
            if not isinstance(m_key, str):
                raise TypeError(
                    f'Key "{m_key}" in stodym_config must be a string, but got type "{type(m_key).__name__}"'
                )
            if m_key not in vars_valid:
                raise NameError(
                    f'Invalid key "{m_key}" in stodym_config; valid names are {vars_valid}'
                )

        # check required keys
        required_keys = [
            'sediment_density',
            'year_limit'
        ]
        for r_key in required_keys:
            if r_key not in stodym_config:
                raise KeyError(
                    f'Required key "{r_key}" is missing from stodym_config'
                )

        # add config_validation key to speed up computation
        stodym_config['config_validation'] = False

        return stodym_config

    def _validate_algorithm_config(
        self,
        algorithm_name: str,
        algorithm_config: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:

        '''
        Validate the genetic algorithm configuration.
        '''

        # dictionary mapping between required key and algorithms
        alg_rk = {
            'population_size': [
                'EpsNSGAII',
                'EpsMOEA',
                'IBEA',
                'MOEAD',
                'NSGAII',
                'PESA2',
                'SPEA2'
            ],
            'epsilons': [
                'EpsMOEA',
                'EpsNSGAII'
            ],
            'divisions_outer': [
                'NSGAIII'
            ]

        }

        # supported algorithms
        alg_support = sorted(set(j for i in alg_rk.values() for j in i))

        # check valid algorithm_name
        if algorithm_name not in alg_support:
            raise NameError(
                f'Invalid algorithm name "{algorithm_name}"; valid names are {alg_support}'
            )

        # list of valid input arguments name
        alg_args = []
        args_types = inspect.signature(getattr(platypus, algorithm_name))
        for param_name in args_types.parameters.keys():
            if param_name in ['problem', 'kwargs']:
                continue
            else:
                alg_args.append(param_name)

        # add special argument if any
        special_args = {
            'MOEAD': ['population_size']
        }
        if algorithm_name in special_args:
            alg_args.extend(special_args[algorithm_name])

        # check input keyword in algorithm_config
        for a_arg in algorithm_config:
            if a_arg not in alg_args:
                raise NameError(
                    f'Invalid key "{a_arg}" in algorithm_config; valid names are {alg_args}'
                )

        # check required key in algorithm_config
        for req_key in alg_rk:
            if algorithm_name in alg_rk[req_key]:
                if req_key not in algorithm_config:
                    raise KeyError(
                        f'Missing required key "{req_key}" in algorithm_config'
                    )

        # check required_key value in algorithm_config
        for req_key in alg_rk:
            if req_key in algorithm_config:
                if req_key != 'epsilons':
                    if not isinstance(algorithm_config[req_key], int):
                        raise TypeError(
                            f'Value for "{req_key}" must be an integer, but got type "{type(algorithm_config[req_key]).__name__}"'
                        )
                else:
                    if not 0 < algorithm_config[req_key] < 1:
                        raise ValueError(
                            f'Value for "{req_key}" must be between 0 and 1, but got "{algorithm_config[req_key]}"'
                        )

        # default mixed variator will be added in algorithm_kwargs
        if 'variator' not in algorithm_config:
            default_variator = platypus.CompoundOperator(
                platypus.SSX(),
                platypus.Replace(),
                platypus.HUX(),
                platypus.BitFlip(),
            )
            algorithm_config['variator'] = default_variator

        return algorithm_config

    def _validate_objectives(
        self,
        objectives: list[str],
        objs_dirs: dict[str, str]
    ) -> list[str]:

        '''
        Validate the list of objectives.
        '''

        # check validity of objective names
        for obj in objectives:
            if obj not in objs_dirs:
                raise ValueError(
                    f'Invalid objective "{obj}"; valid names are {list(objs_dirs.keys())}'
                )

        # check non-empty objective list
        if len(objectives) == 0:
            raise ValueError(
                '"objectives" cannot be an empty list'
            )

        # check objective names cannot be repeated in the list
        if len(objectives) != len(set(objectives)):
            raise ValueError(
                f'Duplicate names found in objective list: {objectives}'
            )

        return objectives

    def _validate_constraints(
        self,
        constraints: dict[str, float],
        constrs_ops: dict[str, str]
    ) -> dict[str, float]:

        '''
        Validate the constratint dictionary.
        '''

        # check non-empty dictionary
        if len(constraints) == 0:
            raise ValueError(
                '"constraints" cannot be an empty dictionary'
            )

        # check validity of constraint key and and their value type
        for constr, value in constraints.items():
            if constr not in constrs_ops:
                raise NameError(
                    f'Invalid constraint "{constr}"; valid names are {list(constrs_ops.keys())}'
                )
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f'Value of key "{constr}" in "constraints" must be numeric, but got type "{type(value).__name__}"'
                )

        return constraints

    def _scenario_nondominated(
        self,
        scenario: platypus.Solution,
        dam_number: int,
        storage_vars: platypus.Integer,
        storage_multiplier: float,
        objectives: list[str],
        constraints: dict[str, float],
        stream_file: str,
        stodym_config: dict[str, typing.Any],
        objs_bounds: dict[str, list[float]],
        objs_dirs: dict[str, str],
        constrs_ops: dict[str, str]
    ) -> pandas.DataFrame:

        '''
        Simulate a non-dominated scenario obtained using :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.
        '''

        # Empty dictionary to store output of non-dominated scenario simulation
        scen_out = {}

        # scenario dam locations and storage volumes
        dam_ids = scenario.variables[0]
        dam_storage = [
            storage_vars.decode(i) * storage_multiplier for i in scenario.variables[1:]
        ]
        dam_sort = sorted(
            zip(dam_ids, dam_storage), key=lambda x: x[0]
        )

        # store dam locations
        for i in range(dam_number):
            scen_out[f'd_{i + 1}'] = dam_sort[i][0]

        # store dam storage volumes
        for i in range(dam_number):
            scen_out[f'sv_{i + 1}'] = dam_sort[i][1]

        # scenario storage dynamics simulation
        scenario_stodym = Network().stodym_plus(
            stream_file=stream_file,
            storage_dict=dict(dam_sort),
            **stodym_config
        )

        # store dam lifespan
        for i in range(dam_number):
            scen_out[f'ls_{i + 1}'] = scenario_stodym['dam_lifespan']['life_year'].iloc[i]

        # objective lower bounds
        objs_lb = [
            objs_bounds[obj][0] for obj in objectives
        ]

        # objective upper bounds
        objs_ub = [
            objs_bounds[obj][1] for obj in objectives
        ]

        # normalized objective values
        objs_normalize = [
            val if objs_dirs[obj] == 'min' else - val for obj, val in zip(objectives, scenario.objectives)
        ]

        # store objectives
        for i, obj in enumerate(objectives):
            actual_val = objs_normalize[i] * (objs_ub[i] - objs_lb[i]) + objs_lb[i]
            scen_out[f'{obj}({objs_dirs[obj]})'] = actual_val

        # store constraints
        for constr, val in zip(constraints, scenario.constraints):
            scen_out[f'{constr}{constrs_ops[constr]}{constraints[constr]}'] = val

        # store normalized objective list
        scen_out['obj_normalize'] = objs_normalize

        return scen_out

    def _cpu_number(
        self,
        processes: typing.Optional[int]
    ) -> int:

        '''
        Determine the number of CPUs to use for computation.
        '''

        cpu_num = os.cpu_count()
        if processes is None:
            if cpu_num is None:
                raise OSError(
                    'Provide an integer value of "processes" as "os.cpu_count()" returned None'
                )
        else:
            cpu_num = processes

        return cpu_num

    def compute_curve_pairwise_deviation(
        self,
        df: pandas.DataFrame
    ) -> float:

        '''
        Compute a scalar metric representing the pairwise variability among
        annual remaining storage percentage curves of dams.

        The method processes the input DataFrame as follows:

        - Selects the columns containing remaining storage percentages of dams.
        - Replaces NaN and negative values with 0.
        - Normalizes percentages to the [0, 1] range by dividing by 100.
        - Computes pairwise Euclidean distances between the normalized curves.
        - Returns the standard deviation of these pairwise distances.

        Parameters
        ----------
        df : DataFrame
            DataFrame corresponding to the ``dam_remaining_storage`` key from the output dictionary
            generated by :meth:`OptiDamTool.Network.stodym_plus`.

        Returns
        -------
        float
            Standard deviation of the normalized pairwise Euclidean distances between dam storage curves.
            A smaller value indicates that dams follow more similar patterns in their remaining storage dynamics.
        '''

        # conside the positive values only
        df = df.where(
            cond=df > 0,
            other=0
        )

        # transpose DataFrame and divide by 100
        t_df = df.iloc[:, 1:].T / 100
        t_arr = t_df.values.astype(float)

        # pairwise Euclidean distances
        pairwise_dist = scipy.spatial.distance.pdist(
            X=t_arr,
            metric='euclidean'
        )

        # normalized pairwise distances
        norm_dist = pairwise_dist / pow(t_df.shape[1], 0.5)

        # standard deviation of Euclidean distances
        std_dist = float(norm_dist.std())

        return std_dist

    def compute_curve_mean_deviation(
        self,
        df: pandas.DataFrame
    ) -> float:

        '''
        Compute a scalar metric representing the maximum deviation of annual
        remaining storage percentage curves of dams from their mean curve.

        The method processes the input DataFrame as follows:

        - Selects columns containing the remaining storage percentages of dams.
        - Replaces NaN and negative values with 0.
        - Normalizes percentages to the [0, 1] range by dividing by 100.
        - Computes the mean curve across all dams.
        - Calculates Euclidean distances between each normalized curve and the mean curve.
        - Returns the maximum of these normalized Euclidean distances.

        Parameters
        ----------
        df : DataFrame
            DataFrame corresponding to the ``dam_remaining_storage`` key from the output dictionary
            generated by :meth:`OptiDamTool.Network.stodym_plus`.

        Returns
        -------
        float
            Maximum normalized Euclidean distance between annual remaining storage percentage curves of dams
            and their mean curve. A smaller value indicates that dams follow more similar patterns relative
            to the mean remaining storage dynamics.
        '''

        # conside the positive values only
        df = df.where(
            cond=df > 0,
            other=0
        )

        # transpose DataFrame and divide by 100
        t_df = df.iloc[:, 1:].T / 100
        t_arr = t_df.values.astype(float)

        # mean of rows
        mean_row = t_arr.mean(
            axis=0
        )

        # Euclidean distances from mean row
        euclidean_dist = numpy.linalg.norm(
            x=t_arr - mean_row,
            axis=1
        )

        # normalized Euclidean distances
        norm_dist = euclidean_dist / pow(t_df.shape[1], 0.5)

        # maximum normalized Euclidean distances
        max_dist = float(norm_dist.max())

        return max_dist

    def _objective_bounds(
        self,
        dam_number: int,
        storage_vars: platypus.Integer,
        storage_multiplier: float,
        objectives: list[str],
        stodym_config: dict[str, typing.Any]
    ) -> dict[str, list[float]]:

        '''
        Construct a dictionary where each key is an objective name from
        :attr:`OptiDamTool.SystemDesign.mapping_objective_direction`, and each value
        is a two-element list representing the lower and upper bounds.
        '''

        # objectives lower and upper bounds
        objs_bounds = {}
        for obj in objectives:
            if obj == 'lifespan':
                lb_val = dam_number * numpy.log(self.lifespan_epsilon)
                ub_val = dam_number * numpy.log(stodym_config['year_limit'])
            if obj == 'lifespan_std':
                lb_val = 0
                ub_val = stodym_config['year_limit'] / 2
            if obj == 'storage_sum':
                lb_val = dam_number * storage_vars.min_value * storage_multiplier
                ub_val = dam_number * storage_vars.max_value * storage_multiplier
            if obj == 'curve_pairwise_deviation':
                lb_val = 0
                ub_val = 0.5
            if obj == 'curve_mean_deviation':
                lb_val = 0
                ub_val = 1
            if obj in ['sediment_trapped_initial', 'sediment_released_median', 'drainage_area']:
                lb_val = 0
                ub_val = 100
            objs_bounds[obj] = [lb_val, ub_val]

        return objs_bounds

    def _scenario_sediment_control(
        self,
        variables: list[list[int] | int],
        storage_multiplier: float,
        stream_file: str,
        stodym_config: dict[str, typing.Any],
        objectives: list[str],
        objs_bounds: dict[str, list[float]],
        objs_dirs: dict[str, str],
        constraints: dict[str, float]
    ) -> tuple[list[float], list[float]]:

        '''
        Generate objective and constraint values for the scenario produced by
        :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.
        '''

        # selected list of dams
        selected_dam = typing.cast(list[int], variables[0])

        # selcted sotrage volumns
        selected_storage = typing.cast(list[int], variables[1:])
        storage_dict = {
            k: v * storage_multiplier for k, v in zip(selected_dam, selected_storage)
        }

        # storage dynamics simulation from selected dam and storage volumes
        vars_stodym = Network().stodym_plus(
            stream_file=stream_file,
            storage_dict=storage_dict.copy(),
            **stodym_config
        )

        # compute objective
        sim_objs = typing.cast(list[float], [])
        for obj in objectives:
            if obj == 'lifespan':
                # dam lifespan with small positive value s a lower bound to penalize low lifespans
                dam_lifespan = vars_stodym['dam_lifespan']['life_year'].clip(
                    lower=self.lifespan_epsilon
                )
                obj_val = sum(numpy.log(dam_lifespan))
            if obj == 'lifespan_std':
                lifespan_std = vars_stodym['dam_lifespan']['life_year'].std(
                    ddof=0
                )
                obj_val = float(lifespan_std)
            if obj == 'storage_sum':
                obj_val = sum(storage_dict.values())
            if obj == 'curve_pairwise_deviation':
                obj_val = self.compute_curve_pairwise_deviation(
                    df=vars_stodym['dam_remaining_storage']
                )
            if obj == 'curve_mean_deviation':
                obj_val = self.compute_curve_mean_deviation(
                    df=vars_stodym['dam_remaining_storage']
                )
            if obj == 'sediment_trapped_initial':
                sediment_trapped = vars_stodym['system_statistics']['sedtrap_%']
                obj_val = float(sediment_trapped.iloc[0])
            if obj == 'drainage_area':
                drainage_area = vars_stodym['system_statistics']['drainage_%']
                obj_val = float(drainage_area.iloc[0])
            if obj == 'sediment_released_median':
                sediment_released = vars_stodym['system_statistics']['sedrelease_%']
                median_year = len(sediment_released) // 2
                obj_val = float(sediment_released.iloc[median_year:].mean())
            # normalized objective
            obj_norm = (obj_val - objs_bounds[obj][0]) / (objs_bounds[obj][1] - objs_bounds[obj][0])
            # maximum to minimum conversion if any
            obj_min = obj_norm if objs_dirs[obj] == 'min' else - obj_norm
            # sim_objs.append(obj_norm)
            sim_objs.append(obj_min)

        # compute constraint values
        sim_constrs = typing.cast(list[float], [])
        for constr in constraints:
            if constr == 'lb_lifespan':
                constr_val = min(vars_stodym['dam_lifespan']['life_year'])
            if constr == 'ub_storage_sum':
                constr_val = sum(storage_dict.values())
            sim_constrs.append(constr_val)

        # scenario output
        scenario_output = (sim_objs, sim_constrs)

        return scenario_output

    @property
    def mapping_constraint_operator(
        self
    ) -> dict[str, str]:

        '''
        Provide a dictionary mapping optimization constraints
        to their corresponding operators. Each constraint is listed with its
        operator and an explanatory remark.

        - ``lb_lifespan``
            - **Operator**: ``>=``
            - **Remark**: Lower bound on dam lifespan, ensuring that each dam remains operates
              for at least the minimum required number of years.

        - ``ub_storage_sum``
            - **Operator**: ``<=``
            - **Remark**: Upper bound on the total storage volume across all dams, used to prevent
              unrealistic designs with excessively large reservoirs or prohibitively high deployment costs.
        '''

        constrs_ops = {
            'lb_lifespan': '>=',
            'ub_storage_sum': '<='
        }

        return constrs_ops

    @property
    def mapping_objective_direction(
        self
    ) -> dict[str, str]:

        '''
        Provide a dictionary mapping optimization objectives to their respective directions.
        Each objective is listed with its direction and an explanatory remark justifying the choice.

        - ``lifespan``
            - **Direction**: Maximize
            - **Remark**: Extend the functional lifespan of dams. The objective is computed as the summation
              of logarithms of lifespans, with :math:`10^{-6}` as a lower bound to avoid undefined behavior
              from computing :math:`\\log(0)`. This ensures that dams with zero lifespans are penalized appropriately.

        - ``lifespan_std``
            - **Direction**: Minimize
            - **Remark**: Reduce variability in dam lifespans so benefits are distributed more evenly across all dams.
              The objective is computed as the standard deviation of lifespans.

        - ``sediment_trapped_initial``
            - **Direction**: Maximize
            - **Remark**: Retain more sediment within the watershed during the initial year, when trapping is most effective.
              This supports dam performance early in the system’s lifespan, before sedimentation reduces trapping capacity.

        - ``sediment_released_median``
            - **Direction**: Minimize
            - **Remark**: Reduce the average sediment release from the median lifetime of the dam system onward to capture long-term effectiveness.
              For example, if the system has a 10–11 year lifespan, the average sediment release from year 6 to the end of operation is used as the metric.

        - ``storage_sum``
            - **Direction**: Minimize
            - **Remark**: Promote cost-efficient deployment by reducing the total storage volume of the dam system.

        - ``curve_pairwise_deviation``
            - **Direction**: Minimize
            - **Remark**: Limit variability among the annual remaining storage curves of individual dams, ensuring consistency
              in how dams respond to sediment inflow over time. Computed via :meth:`OptiDamTool.SystemDesign.compute_curve_pairwise_deviation`.

        - ``curve_mean_deviation``
            - **Direction**: Minimize
            - **Remark**: Reduce deviation of each dam’s annual remaining storage curve from the overall mean curve, promoting uniform
              storage behavior across the dam system. Computed via :meth:`OptiDamTool.SystemDesign.compute_curve_mean_deviation`.
        '''

        objs_dirs = {
            'lifespan': 'max',
            'lifespan_std': 'min',
            'sediment_trapped_initial': 'max',
            'sediment_released_median': 'min',
            'drainage_area': 'max',
            'storage_sum': 'min',
            'curve_pairwise_deviation': 'min',
            'curve_mean_deviation': 'min'
        }

        return objs_dirs

    def sediment_control_by_fixed_dams(
        self,
        dam_number: int,
        storage_bounds: tuple[int, int],
        storage_multiplier: int | float,
        stream_file: str,
        stodym_config: dict[str, typing.Any],
        objectives: list[str],
        algorithm_name: str,
        algorithm_config: dict[str, typing.Any],
        seeds: int,
        nfe: int,
        folder_path: str,
        constraints: dict[str, float] = {'lb_lifespan': 0},
        processes: typing.Optional[int] = None
    ) -> pandas.DataFrame:

        '''
        Optimize dam locations and storage volumes using a multi-objective evolutionary algorithm,
        based on annual sediment inflow to watershed drainage pathways.

        This function uses built-in `evolutionary algorithms <https://platypus.readthedocs.io/en/latest/api/platypus.algorithms.html>`_
        from the ``platypus-opt`` Python package. Users can perform multiple experiments for
        the same problem, with each run starting from a different initial population.

        The function returns a dictionary with two keys, where each value is a DataFrame.
        The DataFrames are also saved to the input directory as JSON files, with filenames
        corresponding to the dictionary keys.

        - ``solutions_nondominated``
            DataFrame of non-dominated solutions extracted from merged feasible solutions across
            multiple experiments. Columns include:

            - ``count``
                Sequential index (starting from 0) for solution numbering.

            - ``d_<i>``
                Stream identifiers for dams (``<i>`` ranges from 1 to ``dam_number``).

            - ``sv_<i>``
                Initial storage volume of dams in cubic meters (``<i>`` ranges from 1 to ``dam_number``).

            - ``ls_<i>``
                Lifespan of dams in years (``<i>`` ranges from 1 to ``dam_number``).

            - ``<obj>(<dir>)``
                Objective values, where ``<obj>`` is the objective name from the list of input ``objectives`` and
                ``<dir>`` is its direction (``min`` or ``max``).

            - ``<constr><op><val>``
                Constraint values, where ``<constr>`` is the constraint name from the dictionary of input ``constraints``,
                ``<op>`` is the operator, and ``<val>`` is the bound.

            - ``obj_normalize``
                List of normalized objective values, computed as ``(obj_val - obj_lb) / (obj_ub - obj_lb)``,
                where ``obj_val`` is the objective value, and ``obj_lb`` and ``obj_ub`` are the lower and upper bounds of the objectives.

            - ``metric_euclidean(<solution_ideal>)``
                Euclidean distance of normalized solutions to the ideal solution list ``<solution_ideal>``.

        - ``computation_statistics``
            DataFrame with two columns, ``feature`` and ``value``. The ``feature`` column includes:

            - ``total_execution_time (s)``: Total execution time in seconds.

            - ``total_execution_timedelta``: Total execution time in `datetime.timedelta <https://docs.python.org/3/library/datetime.html#timedelta-objects>`_
              string format (HH:MM:SS).

            - ``CPU_number``: Number of CPU cores used for computation (either `processes` or `os.cpu_count()`).

            - ``experiment_number``: Number of experiments specified by the user.

            - ``batch_run_number``: Number of batch runs across CPUs, defined as the ceiling division of the experiment number by the CPU count.

            - ``experiment_time (s)``: Total experiment time in seconds.

            - ``experiment_timedelta``: Total experiment time in ``datetime.timedelta`` string format (HH:MM:SS).

            - ``average_experiment_time (s)``: Average execution time per experiment in seconds.

            - ``average_experiment_timedelta``: Average execution time per experiment in ``datetime.timedelta`` string format (HH:MM:SS).

            - ``total_function_evaluations``: Total function evaluations, calculated as the product of the number of experiments and the function evaluations per experiment,
              both specified by the user.

            - ``total_nondominated_solutions``: Number of solutions in the ``solutions_nondominated`` DataFrame.

        Parameters
        ----------
        dam_number : int
            Number of dams to deploy in the watershed area.

        storage_bounds : tuple[int, int]
            Tuple of two integers specifying the lower and upper bounds of storage volumes.
            Both values must be greater than 0.

        storage_multiplier : float
            Multiplier applied to the values within the storage bounds to obtain the actual storage volumes in cubic meters.
            For example, if ``storage_bounds = (1, 5)`` and ``storage_multiplier = 1000``,
            the resulting storage volumes for the dams will be [1000, 2000, 3000, 4000, 5000].

        stream_file : str
            Path to the input stream GeoJSON file, generated by
            :meth:`OptiDamTool.Analysis.sediment_delivery_to_stream_geojson`.

        stodym_config : dict
            Dictionary specifying input variable configurations for :meth:`OptiDamTool.Network.stodym_plus`.
            Each key corresponds to the name of an input variable, and the value is the parameter supplied to the method.

            - **Required keys**: ``sediment_density`` and ``year_limit``.
            - **Optional keys**: ``trap_equation``,  ``trap_threshold``, ``brown_d``, ``trap_constant``, and ``release_threshold``.

            Example
            -------
            .. code-block:: python

                # for dynamic sediment trapping efficiency of dams
                stodym_config = {
                    'sediment_density': 1300,
                    'year_limit': 100,
                    'trap_threshold': 0.05,
                    'brown_d': 1,
                    'release_threshold': 0.9
                }

                # for constant sediment trapping efficiency of dams
                stodym_config = {
                    'sediment_density': 1300,
                    'year_limit': 100,
                    'trap_equation': False,
                    'trap_constant': 0.8,
                    'release_threshold': 0.9
                }

        objectives : list
            List of valid objective names, which can be obtained from the keys of the output dictionary
            defined in the attribute :attr:`OptiDamTool.SystemDesign.mapping_objective_direction`.

        algorithm_name : str
            Name of the evolutionary algorithm to use. Supported options:

            - ``PESA2``: Pareto Envelope-based Selection Algorithm that divides the objective space into regions and
              maintains diversity by regulating density across those regions.

            - ``SPEA2``: Strength Pareto Evolutionary Algorithm that assigns fitness based on
              dominance strength and incorporates density estimation for better selection pressure.

            - ``IBEA``: Indicator-Based Evolutionary Algorithm that uses a ``Hypervolume`` indicator
              to guide the search toward well-distributed Pareto-optimal solutions.

            - ``MOEAD``: Multi-Objective Evolutionary Algorithm with Decomposition, which transforms a multi-objective
              problem into multiple scalar subproblems and solves them cooperatively.

            - ``NSGAII``: Classic Non-dominated Sorting Genetic Algorithm (NSGA-II) that ensures convergence toward the Pareto
              front while maintaining diversity using crowding distance.

            - ``NSGAIII``: Extension of NSGA-II designed for many-objective problems, using a set of reference directions
              to maintain diversity across high-dimensional objective spaces.

            - ``EpsMOEA``: ε-dominance Multi-Objective Evolutionary Algorithm that employs an ε-box archive to
              control archive size and promote solution diversity.

            - ``EpsNSGAII``: Variant of NSGA-II that integrates ε-dominance into selection to maintain a bounded,
              diverse set of non-dominated solutions.

            .. note::

                - ``MOEAD`` and ``NSGAIII`` are particularly suited for many-objective optimization problems
                  (more than three objectives). For problems with fewer objectives, ``EpsNSGAII`` is widely adopted.

                - The mapping of required keys to algorithms is as follows:

                .. code-block:: python

                    {
                        'population_size': ['EpsNSGAII', 'EpsMOEA', 'IBEA', 'MOEAD', 'NSGAII', 'PESA2', 'SPEA2'],
                        'epsilons': ['EpsMOEA', 'EpsNSGAII'],
                        'divisions_outer': ['NSGAIII']
                    }

                - The required key ``epsilons`` must be set between 0 and 1, consistent with the assumption
                  that all objective values are normalized to the [0, 1] range.

                - For ``NSGAIII``, the required key ``divisions_outer`` determines the number of reference
                  directions and implicitly controls the population size. The population size is calculated
                  as the combination ``C(O + D - 1, D)``, where ``O`` is the number of objectives and ``D`` is ``divisions_outer``.

        algorithm_config : dict
            Dictionary of algorithm parameters. Must include ``population_size`` along with
            other valid keyword arguments supported by the chosen algorithm.

            Example
            -------
            .. code-block:: python

                algorithm_config={
                    'population_size': 10
                }

        seeds : int
            Number of independent experiments for the same problem,
            with each run starting from a different initial population.

        nfe : int
            Maximum number of function evaluations per experiment. This parameter controls how many generations
            the algorithm will execute. For example, if ``nfe`` is set to 1000 and the population size is 100,
            the algorithm will run for at least ``1000 // 100 = 10`` generations. For best results,
            ``nfe`` should be a positive integer multiple of the population size,ensuring a more consistent
            and effective optimization process.

        folder_path : str
            Path to the folder where the JSON files will be saved.

        constraints : dict, optional
            Dictionary containing valid constraint names as keys and their corresponding values.
            The valid names can be obtained from the keys of the output dictionary defined in the
            attribute :attr:`OptiDamTool.SystemDesign.mapping_constraint_operator`. The default value is
            ``{'lb_lifespan': 0}``, which is used to run the algorithm but has no effect on the optimization.

            Example
            -------
            .. code-block:: python

                constraints={
                    'lb_lifespan': 1
                }

        processes : int, optional
            Number of logical CPUs to use for running ``seeds`` in parallel. Defaults to all available CPUs.

        Returns
        -------
        dict
            Dictionary with two keys:

            - ``solutions_nondominated``: DataFrame of non-dominated solutions.
            - ``computation_statistics``: DataFrame of computation statistics.
        '''

        # time start form entire execution
        excecution_start = time.time()

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.sediment_control_by_fixed_dams
            ),
            vars_values=locals()
        )

        # check the vailidity of folder_path
        utility._validate_folder_path(
            folder_path=folder_path
        )

        # check the folder_path is empty
        utility._validate_empty_folder(
            folder_path=folder_path
        )

        # check validity of variable configuration for optimization
        stream_ids = self._validate_preliminary_config(
            stream_file=stream_file,
            dam_number=dam_number,
            storage_bounds=storage_bounds,
            storage_multiplier=storage_multiplier,
            seeds=seeds
        )

        # check keyword validity of stodym_plus input arguments
        self._validate_stodym_kwargs(
            stodym_config=stodym_config
        )

        # check genetic algorithm name and keywords
        algorithm_kwargs = self._validate_algorithm_config(
            algorithm_name=algorithm_name,
            algorithm_config=algorithm_config
        )

        # mapping between objectives and their directions
        objs_dirs = self.mapping_objective_direction

        # mapping between constraints and their operators
        constrs_ops = self.mapping_constraint_operator

        # check validity of objectives
        self._validate_objectives(
            objectives=objectives,
            objs_dirs=objs_dirs
        )

        # check validity of constraints
        self._validate_constraints(
            constraints=constraints,
            constrs_ops=constrs_ops
        )

        # location variables of dams
        location_vars = platypus.Subset(
            elements=stream_ids,
            size=dam_number
        )

        # storage variables of dams
        storage_vars = platypus.Integer(
            min_value=storage_bounds[0],
            max_value=storage_bounds[1]
        )

        # objective bounds
        objs_bounds = self._objective_bounds(
            dam_number=dam_number,
            storage_vars=storage_vars,
            storage_multiplier=storage_multiplier,
            objectives=objectives,
            stodym_config=stodym_config
        )

        # problem definition
        problem = platypus.Problem(
            nvars=dam_number + 1,
            nobjs=len(objectives),
            nconstrs=len(constraints)
        )

        # problem variable types
        problem.types[0] = location_vars
        problem.types[1:] = storage_vars

        # problem objective directions
        problem.directions[:] = platypus.Problem.MINIMIZE

        # problem constraints
        for idx, constr in enumerate(constraints):
            problem.constraints[idx] = platypus.Constraint(
                op=constrs_ops[constr],
                value=constraints[constr]
            )

        # problem function
        problem.function = functools.partial(
            self._scenario_sediment_control,
            storage_multiplier=storage_multiplier,
            stream_file=stream_file,
            stodym_config=stodym_config,
            objectives=objectives,
            objs_bounds=objs_bounds,
            objs_dirs=objs_dirs,
            constraints=constraints
        )

        # number of batch run from seeds and CPUs
        cpu_num = self._cpu_number(
            processes=processes
        )
        batch_number = seeds // cpu_num if seeds % cpu_num == 0 else seeds // cpu_num + 1

        # time start for simulating the problem by multiple experiment
        experiment_start = time.time()

        # run algorithm with parallel computing support
        with platypus.ProcessPoolEvaluator(processes=cpu_num) as evaluator:
            simulation = platypus.experiment(
                algorithms=[
                    (getattr(platypus, algorithm_name), algorithm_kwargs)
                ],
                problems=[problem],
                seeds=seeds,
                nfe=nfe,
                evaluator=evaluator,
                display_stats=True
            )

        # time for experiment
        time_experiment = round(time.time() - experiment_start)

        # average time to run per seed
        time_seed = round(time_experiment / batch_number)

        # merge fesible scenario from seeds
        scenario_seed = []
        for s_key in simulation.keys():
            for p_key in simulation[s_key].keys():
                for seed_solution in simulation[s_key][p_key]:
                    seed_feasible = [
                        fs for fs in seed_solution if fs.feasible
                    ]
                    scenario_seed.extend(seed_feasible)

        # non-dominated scenarios
        scenario_nd = platypus.nondominated(
            solutions=scenario_seed
        )

        # simulation of individual non-ominated scenario in separate CPU
        cpu_sim = functools.partial(
            self._scenario_nondominated,
            dam_number=dam_number,
            storage_vars=storage_vars,
            storage_multiplier=storage_multiplier,
            objectives=objectives,
            constraints=constraints,
            stream_file=stream_file,
            stodym_config=stodym_config,
            objs_bounds=objs_bounds,
            objs_dirs=objs_dirs,
            constrs_ops=constrs_ops
        )

        # save CPU simulation output in a list
        cpu_list = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_num) as executor:
            # Multicore simulation
            futures = [
                executor.submit(cpu_sim, sol) for sol in scenario_nd
            ]
            for future in concurrent.futures.as_completed(futures):
                cpu_list.append(future.result())

        # DataFrame from non-dominated solutions
        solution_df = pandas.DataFrame.from_records(
            data=cpu_list
        )
        df_columns = list(solution_df.columns)

        # remove duplicate rows from DataFrame
        solution_df = solution_df.drop_duplicates(
            subset=df_columns[-1],
            ignore_index=True
        )

        # Ideal utopian objective array
        objs_utopian = []
        for obj in objectives:
            utopian_val = 0 if objs_dirs[obj] == 'min' else 1
            objs_utopian.append(utopian_val)
        utopian_array = numpy.array([objs_utopian])

        # array from normalized solutions
        normalized_array = numpy.array(
            solution_df[df_columns[-1]].values.tolist(),
            dtype=float
        )

        # Eucliean distance from normalized solutions to utopian point
        solution_df[f'metric_euclidean({objs_utopian})'] = numpy.linalg.norm(
            x=normalized_array - numpy.array(objs_utopian),
            axis=1
        )

        # insert 'count' column to the DataFrame
        solution_df = solution_df.reset_index(
            names=['count']
        )

        # save the DataFrame of non-dominated solutions
        solution_df.to_json(
            path_or_buf=os.path.join(folder_path, 'solutions_nondominated.json'),
            orient='records',
            indent=4
        )

        # total time for execution
        time_excecution = round(time.time() - excecution_start)

        # statistic of computation
        computation_stats = {
            'total_execution_time (s)': time_excecution,
            'total_execution_timedelta': f'{datetime.timedelta(seconds=time_excecution)}',
            'CPU_number': cpu_num,
            'experiment_number': seeds,
            'batch_run_number': batch_number,
            'experiment_time (s)': time_experiment,
            'experiment_timedelta': f'{datetime.timedelta(seconds=time_experiment)}',
            'average_experiment_time (s)': time_seed,
            'average_experiment_timedelta': f'{datetime.timedelta(seconds=time_seed)}',
            'algorithm_name': algorithm_name,
            'total_function_evaluations': seeds * nfe,
            'total_nondominated_solutions': len(solution_df)
        }

        # DataFrame of computation statistics
        computation_df = pandas.DataFrame()
        for k, v in computation_stats.items():
            computation_df.loc['value', k] = v

        # save computation statistics DataFrame
        computation_df.to_json(
            path_or_buf=os.path.join(folder_path, 'computation_statistics.json'),
            orient='records',
            indent=4
        )

        # output dictionary
        output = {
            'solutions_nondominated': solution_df,
            'computation_statistics': computation_df.T.reset_index(
                names=['feature']
            )
        }

        return output

    def _storage_dict_from_solution_file(
        self,
        solution_file: str,
        count: int
    ) -> dict[int, float]:
        '''
        Get storage dictionary for a specific solution scenario obtained via
        :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.
        '''

        # DataFrame of non-dominated solutions
        df = pandas.read_json(
            path_or_buf=solution_file,
            orient='records'
        )

        # scenario from count
        scenario = df.iloc[count]

        # number of dams
        dam_number = len(
            [i for i in scenario.index if i.startswith('d_')]
        )

        # storage dictionary
        storage_dict = {}
        for i in range(1, dam_number + 1):
            storage_dict[int(scenario[f'd_{i}'])] = float(scenario[f'sv_{i}'])

        return storage_dict

    def scenario_stodym_plus(
        self,
        solution_file: str,
        count: int,
        stream_file: str,
        stodym_config: dict[str, typing.Any]
    ) -> dict[str, pandas.DataFrame]:

        '''
        Retrieve detailed simulation outputs from :meth:`OptiDamTool.Network.stodym_plus`
        for a specific solution scenario obtained via :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.

        Parameters
        ----------
        solution_file : str
            Path to the ``solutions_nondominated.json`` file generated by :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`,
            containing non-dominated solution scenarios.

        count : int
            Integer value of ```count`` key of the selected scenario in ``solutions_nondominated.json`` for which detailed simulation
            results are to be retrieved.

        stream_file : str
            Path to the input stream GeoJSON file passed to :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.

        stodym_config : dict
            Same dictionary passed to :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.
            To store the results, include an additional key ``folder_path`` specifying the output directory where JSON files will be saved.

            .. warning::

                If the ``stream_file`` or the ``stodym_config`` dictionary does not match the input used in
                :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`, the retrieved
                output parameter values will not correspond to those in ``solutions_nondominated.json``.

        Returns
        -------
        dict
            Dictionary produced by :meth:`OptiDamTool.Network.stodym_plus`,
            containing detailed simulation results for the selected solution scenario.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.scenario_stodym_plus
            ),
            vars_values=locals()
        )

        # storage dictionary
        storage_dict = self._storage_dict_from_solution_file(
            solution_file=solution_file,
            count=count
        )

        # scenario storage dynamics simulation
        scenario_stodym = Network().stodym_plus(
            stream_file=stream_file,
            storage_dict=storage_dict,
            **stodym_config
        )

        return scenario_stodym

    def scenario_stodym_plus_drainage_response(
        self,
        solution_file: str,
        count: int,
        stream_file: str,
        flwdir_file: str,
        folder_path: str,
        stodym_config: dict[str, typing.Any]
    ) -> pandas.DataFrame:

        '''
        Retrieve detailed simulation outputs from :meth:`OptiDamTool.Network.stodym_plus_drainage_response`
        for a specific solution scenario obtained via :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.

        Parameters
        ----------
        solution_file : str
            Path to the ``solutions_nondominated.json`` file generated by :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`,
            containing non-dominated solution scenarios.

        count : int
            Integer value of ```count`` key of the selected scenario in ``solutions_nondominated.json`` for which detailed simulation
            results are to be retrieved.

        stream_file : str
            Path to the input stream GeoJSON file passed to :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`.

        flwdir_file : str
            Path to the input flow direction raster file ``flowdir.tif``, generated by :meth:`OptiDamTool.WatemSedem.dem_to_stream`
            during the creation of ``stream_file``.

        folder_path : str
            Path to the folder where JSON and GeoJSON files will be saved.

        stodym_config : dict
            Dictionary of input configuration parameters passed to :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`
            to obtain the solution scenario.

            .. warning::

                If the ``stream_file``, ``flwdir_file``, or the ``stodym_config`` dictionary does not match the input used in
                :meth:`OptiDamTool.SystemDesign.sediment_control_by_fixed_dams`, the retrieved
                output parameter values will not correspond to those in ``solutions_nondominated.json``.

        Returns
        -------
        DataFrame
            Dataframe produced by :meth:`OptiDamTool.Network.stodym_plus_drainage_response`,
            containing detailed information on the generated GeoJSON files.
        '''

        # check static type of input variable origin
        utility._validate_variable_origin_static_type(
            vars_types=typing.get_type_hints(
                obj=self.scenario_stodym_plus_drainage_response
            ),
            vars_values=locals()
        )

        # storage dictionary
        storage_dict = self._storage_dict_from_solution_file(
            solution_file=solution_file,
            count=count
        )

        # scenario storage dynamics simulation
        scenario_stodym = Network().stodym_plus_drainage_response(
            stream_file=stream_file,
            flwdir_file=flwdir_file,
            storage_dict=storage_dict,
            folder_path=folder_path,
            **stodym_config
        )

        return scenario_stodym
