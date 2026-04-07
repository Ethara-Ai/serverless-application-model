"""
Compatibility methods to support Python 2.7 style hashing in Python 3.X+

This is designed for compatibility not performance.

"""

import ctypes
import math
from functools import lru_cache


def hash27(value):  # type: ignore[no-untyped-def]
    """
    Wrapper call to Hash.hash()

    Args:
        value: input value

    Returns:
        Python 2.7 hash
    """
    pass


class Hash:
    """
    Various hashing methods using Python 2.7's algorithms
    """

    _FLOAT_ZERO = 0.0

    @staticmethod
    @lru_cache(maxsize=2048)
    def hash(value):  # type: ignore[no-untyped-def]
        """
        Returns a Python 2.7 hash for a value.

        Args:
            value: input value

        Returns:
            Python 2.7 hash
        """
        pass

    @staticmethod
    def thash(value):  # type: ignore[no-untyped-def]
        """
        Returns a Python 2.7 hash for a tuple.

        Logic ported from the 2.7 Python branch: cpython/Objects/tupleobject.c
        Method: static long tuplehash(PyTupleObject *v)

        Args:
            value: input tuple

        Returns:
            Python 2.7 hash
        """
        pass

    @staticmethod
    def fhash(value):  # type: ignore[no-untyped-def]
        """
        Returns a Python 2.7 hash for a float.

        Logic ported from the 2.7 Python branch: cpython/Objects/object.c
        Method: long _Py_HashDouble(double v)

        Args:
            value: input float

        Returns:
            Python 2.7 hash
        """
        pass

    @staticmethod
    def shash(value):  # type: ignore[no-untyped-def]
        """
        Returns a Python 2.7 hash for a string.

        Logic ported from the 2.7 Python branch: cpython/Objects/stringobject.c
        Method: static long string_hash(PyStringObject *a)

        Args:
            value: input string

        Returns:
            Python 2.7 hash
        """
        pass

    @staticmethod
    def ordinal(value):  # type: ignore[no-untyped-def]
        """
        Converts value to an ordinal or returns the input value if it's an int.

        Args:
            value: input

        Returns:
            ordinal for value
        """
        pass
