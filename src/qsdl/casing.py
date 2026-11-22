# Copyright 2026 henn1001
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

"""Case conversion and template filters."""

import re


def pluralize(word: str) -> str:
    """Return the plural form by adding an s if necessary."""
    return word + "s" if not word.endswith("s") else word


def raw_camelcase(word: str) -> str:
    """Convert to camel case without normalizing existing capitals."""
    word = re.sub(r"\w[\s\W]+\w", "", str(word))
    if not word:
        return word
    return word[0].lower() + re.sub(r"[\-_\.\s]([a-z])", lambda m: m.group(1).upper(), word[1:])


def camelcase(word: str) -> str:
    """Convert to camel case after normalizing to snake case."""
    return raw_camelcase(snakecase(word))


def capitalcase(word: str) -> str:
    """Capitalize the first character."""
    word = str(word)
    return word[0].upper() + word[1:] if word else word


def lowercase(word: str) -> str:
    """Convert to lowercase."""
    return str(word).lower()


def pascalcase(word: str) -> str:
    """Convert to Pascal case."""
    return capitalcase(raw_camelcase(word))


def sentencecase(word: str) -> str:
    """Convert to sentence case."""
    word = re.sub(r"[\-_\.\s]", " ", str(word))
    if not word:
        return word
    return capitalcase(re.sub(r"[A-Z]", lambda m: " " + m.group(0).lower(), word).strip())


def snakecase(word: str) -> str:
    """Convert to snake case."""
    word = re.sub(r"[\-\.\s]", "_", str(word))
    if not word:
        return word
    return word[0].lower() + re.sub(r"[A-Z]", lambda m: "_" + m.group(0).lower(), word[1:])


def spinalcase(word: str) -> str:
    """Convert to spinal case."""
    return re.sub(r"_", "-", snakecase(word))


def regex_replace(txt: str, find: str, replace: str) -> str:
    """Apply a regular expression replacement."""
    return re.sub(find, replace, txt)
