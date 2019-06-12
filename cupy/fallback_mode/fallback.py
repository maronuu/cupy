"""
Main fallback class.
"""
import cupy as cp # NOQA
import numpy as np # NOQA


from cupy.fallback_mode.utils import FallbackUtil
from cupy.fallback_mode.utils import get_last_and_rest
from cupy.fallback_mode.utils import join_attrs
from cupy.fallback_mode.utils import call_cupy
from cupy.fallback_mode.utils import call_numpy
from cupy.fallback_mode.utils import get_path


class RecursiveAttr(FallbackUtil):
    """
    RecursiveAttr class to catch all attributes corresponding to numpy,
    when user calls fallback_mode. numpy is an instance of this class.
    """
    def __init__(self, name):
        self.name = name

    def notification_status(self):
        return super().notification_status()

    def set_notification_status(self, status):
        return super().set_notification_status(status)

    def __getattr__(self, attr):
        """
        Catches and appends attributes corresponding to numpy
        to attr_list.
        Runs recursively till attribute gets called by returning
        dummy object of this class.

        Args:
            attr (str): Attribute of RecursiveAttr class object.

        Returns:
            dummy : RecursiveAttr object.
        """
        if self.name == 'numpy':
            super().clear_attrs()
        super().add_attrs(attr)
        return dummy

    def __call__(self, *args, **kwargs):
        """
        Gets invoked when last dummy attribute gets called.

        Search for attributes from attr_list in cupy.
        If failed, search in numpy.
        If method is found, calls respective library
        Else, raise AttributeError.

        Args:
            args (tuple): Arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            (module, res, ndarray): Returns of call_cupy() or call_numpy
            Raise AttributeError: If cupy_func and numpy_func is not found.
        """
        attributes = super().get_attr_list_copy()
        sub_module, func_name = get_last_and_rest(attributes)

        # trying cupy
        try:
            cupy_path = get_path('cp', sub_module)
            cupy_func = getattr(eval(cupy_path), func_name)

            return call_cupy(cupy_func, args, kwargs)

        except AttributeError:
            # trying numpy
            if super().notification_status():
                if sub_module == "":
                    print("'{}' not found in cupy, falling back to numpy"
                          .format(func_name))
                else:
                    print("'{}.{}' not found in cupy, falling back to numpy"
                          .format(sub_module, func_name))

            numpy_path = get_path('np', sub_module)
            numpy_func = getattr(eval(numpy_path), func_name)

            return call_numpy(numpy_func, args, kwargs)

        except AttributeError:
            raise AttributeError("Attribute {} neither in cupy nor numpy"
                                 .format(join_attrs(attributes)))


numpy = RecursiveAttr('numpy')
dummy = RecursiveAttr('dummy')
