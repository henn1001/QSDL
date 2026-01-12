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

from pathlib import Path

import pytest
from textx.exceptions import TextXSemanticError

from qsdl.core import generate


class TestCompositionDirective:
    """Tests for the @composition directive."""

    def test_valid_usage(self) -> None:
        """Test valid usage"""
        test_inputs = [
            """\
                type Metrics {
                  value: Float
                }
                type Service {
                  name: String!
                  metrics: [Metrics] @composition
                }
            """,
            """\
                type Metrics {
                  value: Float
                }
                type Service {
                  name: String!
                  metrics_one: Metrics
                  metrics_two: Metrics
                }
            """,
            """\
                type Metrics {
                  value: Float
                }
                type Service {
                  name: String!
                  metrics_one: [Metrics]
                  metrics_two: [Metrics]
                }
            """,
        ]

        for test_input in test_inputs:
            result = generate(Path("srcgen/"), generator_name="void", raw_schema=test_input)
            assert result is None

    def test_prevent_invalid(self) -> None:
        """Test prevent invalid usage"""
        test_inputs = [
            # prevent composition on non arrays
            """\
                type Metrics {
                  value: Float
                }
                type Service {
                  name: String!
                  metrics: Metrics @composition
                }
            """,
            # prevent duplication of composition relations
            """\
                type Metrics {
                  value: Float
                }
                type Service {
                  name: String!
                  metrics_one: [Metrics] @composition
                  metrics_two: [Metrics] @composition
                }
            """,
            # should we prevent circular relations too?
            # """\
            #     type Metrics {
            #       value: Float
            #       service: [Service] @composition
            #     }
            #     type Service {
            #       name: String!
            #       metrics: [Metrics] @composition
            #     }
            # """,
            # prevent self compositions
            """\
                type Service {
                  name: String!
                  metrics: [Service] @composition
                }
            """,
        ]

        for test_input in test_inputs:
            with pytest.raises(TextXSemanticError):
                generate(Path("srcgen/"), generator_name="void", raw_schema=test_input)
