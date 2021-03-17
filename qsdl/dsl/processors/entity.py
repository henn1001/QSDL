# Copyright (C) 2020 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entity post-processor"""

from qsdl.dsl.models import (
    Argument,
    Base,
    Directive,
    Enum,
    Field,
    Object,
    Operation,
    Scalar,
    Schema,
)


def schema_processor(entity: Schema):
    """The schema post-processor.

    Args:
        entity (Schema): The schema object.
    """
    _ = entity


def scalar_processor(entity: Scalar):
    """The scalar post-processor.

    Args:
        entity (Scalar): The scalar object.
    """
    _ = entity


def enum_processor(entity: Enum):
    """The enum post-processor.

    Args:
        entity (Enum): The enum object.
    """
    _ = entity


def base_processor(entity: Base):
    """The base post-processor.

    Args:
        entity (Base): The base object.
    """
    _ = entity


def operation_processor(entity: Operation):
    """The query post-processor.

    Args:
        entity (Operation): The query object.
    """
    _ = entity


def object_processor(entity: Object):
    """The object post-processor.

    Args:
        entity (Object): The object object.
    """
    _ = entity


def field_processor(entity: Field):
    """The field post-processor.

    Args:
        entity (Field): The field object.
    """
    _ = entity


def argument_processor(entity: Argument):
    """The parameter post-processor.

    Args:
        entity (Argument): The parameter object.
    """
    _ = entity


def directive_processor(entity: Directive):
    """The directive post-processor.

    Args:
        entity (Directive): The directive object.
    """
    _ = entity


entity_processors = {
    "Schema": schema_processor,
    "Scalar": scalar_processor,
    "Enum": enum_processor,
    "Base": base_processor,
    "Operation": operation_processor,
    "Object": object_processor,
    "Field": field_processor,
    "Argument": argument_processor,
    "Directive": directive_processor,
}
