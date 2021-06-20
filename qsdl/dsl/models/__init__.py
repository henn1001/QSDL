"""Model Definitions"""
from .argument import Argument
from .base import Base
from .directive import Directive
from .enum import Enum
from .field import Field
from .object import Object
from .api import Api
from .scalar import Scalar
from .schema import Schema


def all_dsl_models():
    """Returns all DSL classes.

    Returns:
        list: List of DSL classes.
    """
    return [Argument, Base, Directive, Enum, Field, Object, Api, Scalar, Schema]
