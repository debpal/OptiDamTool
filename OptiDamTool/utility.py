import typing
import types
import pandas
import os


def _validate_method_variable_type(
    var_type: dict[str, typing.Any],
    var_value: dict[str, typing.Any]
) -> None:

    '''
    A private method that validates input variables against their expected types.
    '''

    # iterate name and type of method variables
    for name, typ in var_type.items():
        # continute if varibale name is return
        if name == 'return':
            continue
        # get original type, arguments, and value of the variable
        typ_origin = typing.get_origin(typ) or typ
        typ_args = typing.get_args(typ)
        typ_val = var_value[name]
        # if type is Union
        if typ_origin in (typing.Union, types.UnionType):
            if not isinstance(typ_val, typ_args):
                typ_expect = [t.__name__ for t in typ_args]
                raise TypeError(
                    f'Expected "{name}" to be one of {typ_expect}, but got type "{type(typ_val).__name__}"'
                )
        # if type is not Union
        else:
            if not isinstance(typ_val, typ_origin):
                raise TypeError(
                    f'Expected "{name}" to be "{typ.__name__}", but got type "{type(typ_val).__name__}"'
                )

    return None


def _network_storage_dynamics_config(
    storage_dict: dict[int, float],
    year_limit: int,
    trap_equation: bool,
    trap_threshold: float,
    trap_constant: typing.Optional[float],
    folder_path: typing.Optional[str]
) -> None:

    '''
    A private method that validates input variables configuration for
    the methods :meth:`OptiDamTool.Network.storage_dynamics_detailed`
    and :meth:`OptiDamTool.Network.storage_dynamics_lite`.
    '''

    # check validity of folder path
    if folder_path is not None and not os.path.isdir(folder_path):
        raise NotADirectoryError('Input folder_path is not valid')

    # check intial dam storage capacity cannot be negative
    for d_id in storage_dict:
        if storage_dict[d_id] < 0:
            raise ValueError(
                f'Invalid negative intial storage volume {storage_dict[d_id]} for the dam identifier {d_id} was received'
            )

    # check that year_limit value is greater than 0
    if year_limit <= 0:
        raise ValueError(
            f'year_limit must be greater than 0, but received {year_limit}'
        )

    # check trap_equation
    if not trap_equation:
        if trap_constant is None or not isinstance(trap_constant, (int, float)):
            raise TypeError(
                f'trap_constant must be a numeric value when "trap_equation=False", but got type "{type(trap_constant).__name__}"'
            )
        if not (trap_threshold < trap_constant <= 1):
            raise ValueError(
                f'trap_constant {trap_constant} is invalid: must satisfy trap_threshold ({trap_threshold}) < trap_constant <= 1'
            )

    return None


def _df_from_dict(
    input_dict: dict[str, dict[int, typing.Any]]
) -> pandas.DataFrame:

    '''
    A private method that converts a nested dictionary into a DataFrame.
    The outer dictionary's keys become the column names of the resulting DataFrame.
    Each value in the outer dictionary is a subdictionary with the same set of keys,
    which become the row indices. Each cell in the DataFrame contains
    the corresponding value from the subdictionary.
    '''

    series_dict = {
        key: pandas.Series(val) for key, val in input_dict.items()
    }

    df = pandas.DataFrame(
        data=series_dict
    )

    return df
