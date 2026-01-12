# Copyright 2025 henn1001
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entity post-processor"""

from qsdl import dsl

from ..util import description_wrapper


def schema_processor(entity: dsl.Schema) -> None:
    """The schema post-processor.

    Args:
        entity (Schema): The schema object.
    """

    entity.description = description_wrapper(entity.description)
    entity.servers = ["/api/v1"] if not entity.servers else entity.servers


def scalar_processor(entity: dsl.Scalar) -> None:
    """The scalar post-processor.

    Args:
        entity (Scalar): The scalar object.
    """
    _ = entity


def enum_processor(entity: dsl.Enum) -> None:
    """The enum post-processor.

    Args:
        entity (Enum): The enum object.
    """

    entity.description = description_wrapper(entity.description)


def base_processor(entity: dsl.Base) -> None:
    """The base post-processor.

    Args:
        entity (Base): The base object.
    """

    entity.description = description_wrapper(entity.description)


def object_processor(entity: dsl.Object) -> None:
    """The object post-processor.

    Args:
        entity (Object): The object object.
    """

    entity.description = description_wrapper(entity.description)


def field_processor(entity: dsl.Field) -> None:
    """The field post-processor.

    Args:
        entity (Field): The field object.
    """

    entity.description = description_wrapper(entity.description)
    entity.is_relation = entity.is_composition or entity.is_aggregation


def api_processor(entity: dsl.Api) -> None:
    """The api post-processor.

    Args:
        entity (Api): The api object.
    """

    entity.description = description_wrapper(entity.description)


def operation_processor(entity: dsl.Operation) -> None:
    """The operation post-processor.

    Args:
        entity (Api): The operation object.
    """

    entity.description = description_wrapper(entity.description)


def argument_processor(entity: dsl.Argument) -> None:
    """The parameter post-processor.

    Args:
        entity (Argument): The argument object.
    """
    _ = entity


def directive_processor(entity: dsl.Directive) -> None:
    """The directive post-processor.

    Args:
        entity (Directive): The directive object.
    """
    _ = entity


obj_processors = {
    "Schema": schema_processor,
    "Scalar": scalar_processor,
    "Enum": enum_processor,
    "Base": base_processor,
    "Api": api_processor,
    "Operation": operation_processor,
    "Object": object_processor,
    "Field": field_processor,
    "Argument": argument_processor,
    "Directive": directive_processor,
}
