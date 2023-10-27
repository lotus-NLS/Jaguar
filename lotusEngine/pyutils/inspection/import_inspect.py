import importlib
import pkgutil
import inspect


def check_subdir_namecollsions():
    call_stack = inspect.stack()[1]
    caller_source_file = inspect.getmodule(call_stack[0])
    package_path = caller_source_file.__path__
    package_name = caller_source_file.__name__

    imported_names = set()
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        module = importlib.import_module(f"{package_name}.{module_name}")

        dir_names = [name for name in dir(module) if not name.startswith('_')]
        selected_names = dir_names if not hasattr(module,'__all__') else module.__all__

        for name in selected_names:
            if name in imported_names:
                raise ImportError(f"Name collision detected: {name}")
            else:
                imported_names.add(name)