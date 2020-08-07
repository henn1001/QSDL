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

"""Object pre-processor"""


def namespace_processor(entity: object):
    """The namespace pre-processor.

    Args:
        entity (object): The namespace object.
    """
    _ = entity


def scalar_processor(entity: object):
    """The scalar pre-processor.

    Args:
        entity (object): The scalar object.
    """
    _ = entity


def enum_processor(entity: object):
    """The enum pre-processor.

    Args:
        entity (object): The enum object.
    """
    _ = entity


def interface_processor(entity: object):
    """The interface pre-processor.

    Args:
        entity (object): The interface object.
    """
    _ = entity


def input_processor(entity: object):
    """The input pre-processor.

    Args:
        entity (object): The input object.
    """
    _ = entity


def query_processor(entity: object):
    """The query pre-processor.

    Args:
        entity (object): The query object.
    """
    _ = entity


def mutation_processor(entity: object):
    """The mutation pre-processor.

    Args:
        entity (object): The mutation object.
    """
    _ = entity


def object_processor(entity: object):
    """The object pre-processor.

    Args:
        entity (object): The object object.
    """
    _ = entity


def field_processor(entity: object):
    """The field pre-processor.

    Args:
        entity (object): The field object.
    """
    _ = entity


def parameter_processor(entity: object):
    """The parameter pre-processor.

    Args:
        entity (object): The parameter object.
    """
    _ = entity


def directive_processor(entity: object):
    """The directive pre-processor.

    Args:
        entity (object): The directive object.
    """
    _ = entity


obj_processors = {
    "NameSpace": namespace_processor,
    "Scalar": scalar_processor,
    "Enum": enum_processor,
    "Interface": interface_processor,
    "Input": input_processor,
    "Query": query_processor,
    "Mutation": mutation_processor,
    "Object": object_processor,
    "Field": field_processor,
    "Parameter": parameter_processor,
    "Directive": directive_processor,
}
