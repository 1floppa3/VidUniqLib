from functools import wraps
from pathlib import Path


def convert_string_to_path(args_list):
    """Converts path string to pathlib.Path object"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i, arg in enumerate(args):
                if i < len(args_list) and args_list[i] in kwargs and isinstance(kwargs[args_list[i]], str):
                    kwargs[args_list[i]] = Path(kwargs[args_list[i]])
                elif isinstance(arg, str):
                    args = list(args)
                    args[i] = Path(arg)
            return func(*args, **kwargs)

        return wrapper

    return decorator
