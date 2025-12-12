import sys, os, inspect, importlib, types, builtins, pkgutil, importlib.util, importlib.machinery, importlib.abc, importlib.metadata

class Dynamics:
    @staticmethod
    def get_dynamic_type(py_obj):
        """Get the dynamic type of a Python object"""
        if isinstance(py_obj, bool):
            return 'bool'
        elif isinstance(py_obj, int):
            return 'int'
        elif isinstance(py_obj, float):
            return 'float'
        elif isinstance(py_obj, str):
            return 'str'
        elif py_obj is None:
            return 'NoneType'
        else:
            return type(py_obj).__name__
    @staticmethod
    def is_instance_of(py_obj, type_name):
        """Check if a Python object is an instance of a given type name"""
        dynamic_type = Dynamics.get_dynamic_type(py_obj)
        return dynamic_type == type_name
    @staticmethod
    def get_funcs_from_class(cls):
        """Get all functions from a given class"""
        return [member for member in inspect.getmembers(cls, predicate=inspect.isfunction)]
    @staticmethod
    def get_classes_from_module(module):
        """Get all classes from a given module"""
        return [member for member in inspect.getmembers(module, predicate=inspect.isclass)]