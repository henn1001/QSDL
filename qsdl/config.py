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

"""Domain specific variables"""

# pylint: disable=C0103

# the python object graph.
model = None

# all possible endpoints/paths for OpenAPI.
domain_objects = []

# all global operations for OpenAPI.
operations = []

# used to identify if we need to derive operation names from
# their parents.
dupl_objects = set()

# used to flag paths as used in order to prevent path duplicates in
# OpenAPI
used_paths = []

# used to change the OpenAPI type for ID between "string" and "integer"
id_type = "string"
id_type_format = None
