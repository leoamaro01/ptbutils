from typing import Callable


def _func_path_to_callable(path: str) -> Callable:
    import importlib

    module_name, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, func_name)
