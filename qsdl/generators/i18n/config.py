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

"""Generator Configuration"""

from dataclasses import dataclass

from qsdl.generators.base_config import BaseConfig


@dataclass
class Config(BaseConfig):
    """A configuration class that holds relevant data for the generator"""

    locale: str = "en"
    extra_locales: str = ""
    subfolder: str = ""
    enum: bool = True
    base: bool = True
    object: bool = True
    split_files: bool = False
    single_file: bool = True
    single_file_name: str = "domain"
    single_file_enum_name: str = "constant"
    flatten: bool = False
    file_extension: str = "yaml"
    remove_unused_keys: bool = False
