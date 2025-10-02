import typing
import types
import os


def _validate_variable_origin_static_type(
    vars_types: dict[str, typing.Any],
    vars_values: dict[str, typing.Any]
) -> None:

    '''
    Validate input variables against their expected types.
    '''

    # iterate name and type of method variables
    for v_name, v_type in vars_types.items():
        # continute if varibale name is return
        if v_name == 'return':
            continue
        # get origin type and value of the variable
        type_origin = typing.get_origin(v_type)
        type_value = vars_values[v_name]
        # if origin type in None
        if type_origin is None:
            if not isinstance(type_value, v_type):
                raise TypeError(
                    f'Expected "{v_name}" to be "{v_type.__name__}", but got type "{type(type_value).__name__}"'
                )
        # if origin type in not None
        else:
            # if origin type is a Union
            if type_origin in (typing.Union, types.UnionType):
                # get argument types
                type_args = tuple(
                    typing.get_origin(arg) or arg for arg in typing.get_args(v_type)
                )
                if not isinstance(type_value, type_args):
                    type_expect = [t.__name__ for t in type_args]
                    raise TypeError(
                        f'Expected "{v_name}" to be one of {type_expect}, but got type "{type(type_value).__name__}"'
                    )
            # if origin type in not a Union
            else:
                if not isinstance(type_value, type_origin):
                    raise TypeError(
                        f'Expected "{v_name}" to be "{type_origin.__name__}", but got type "{type(type_value).__name__}"'
                    )

    return None


def _validate_json_extension(
    json_file: str,
) -> None:

    '''
    Validate that the file has a JSON extension.
    '''

    if not json_file.lower().endswith('.json'):
        raise TypeError(
            'Output "json_file" path must have a valid JSON file extension'
        )

    return None


def _validate_folder_path(
    folder_path: str,
) -> None:

    '''
    Validate that the given path is a valid directory.
    '''

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(
            'Input folder_path is not valid'
        )

    return None


def _validate_empty_folder(
    folder_path: str,
) -> None:

    '''
    Validate that the given folder path points to an empty directory.
    '''

    if len(os.listdir(folder_path)) > 0:
        raise ValueError(
            'Specified folder_path must point to an empty directory'
        )

    return None
