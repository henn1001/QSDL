# Copyright (C) 2022 henn1001

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Filter functions"""

import re

import stringcase


def pluralize(word: str) -> str:
    """Returns the plural form of a word by simply adding a s if possible"""
    return word + "s" if not word.endswith("s") else word


def pascalcase(word: str) -> str:
    """Returns the PascalCase form of a word using stringcase"""
    return stringcase.pascalcase(word)


def camelcase(word: str) -> str:
    """Returns the camelCase form of a word using stringcase"""
    return stringcase.camelcase(word)


def spinalcase(word: str) -> str:
    """Returns the spinal-case form of a word using stringcase"""
    return stringcase.spinalcase(word)


def snakecase(word: str) -> str:
    """Returns the snake_case form of a word using stringcase"""
    return stringcase.snakecase(word)


def regex_replace(txt: str, find: str, replace: str) -> str:
    """Applies re.sub to a given string"""
    return re.sub(find, replace, txt)
