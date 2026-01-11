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


class TestOpaqueDirective:
    """Tests for the opaque directive."""

    def test_opaque_directive_valid_usage(self) -> None:
        """Test valid usage of opaque directive on base types."""
        test_input = """\
            base BaseType  {
              likes: Int
            }
            base PerformanceMetrics {
              responseTime: Float
              errorRate: Float
              throughput: Int
              nestedA: BaseType
              nestedB: BaseType @opaque // opaque or not should be allowed here
            }

            type Service {
              name: String!
              metricsA: PerformanceMetrics @opaque
              metricsB: [PerformanceMetrics]
              metricsC: [PerformanceMetrics] @opaque
            }
        """
        # Should not raise any exceptions
        result = generate(Path("srcgen/"), generator_name="void", raw_schema=test_input)
        assert result is None

    def test_opaque_only_allowed_on_base_fields(self) -> None:
        """Test that opaque directive is only allowed on base type fields."""
        test_inputs = [
            # Opaque on type field
            """\
                type Metrics {
                  value: Float
                }

                type Service {
                  name: String!
                  metrics: Metrics @opaque
                }
            """,
            # Opaque on scalar field
            """\
                type Service {
                  name: String!
                  value: Float @opaque
                }
            """,
            # Opaque on enum field
            """\
                enum Status {
                  ACTIVE
                  INACTIVE
                }

                type Service {
                  name: String!
                  status: Status @opaque
                }
            """,
        ]

        for test_input in test_inputs:
            with pytest.raises(TextXSemanticError, match="declares opaque on a non Base value"):
                generate(Path("srcgen/"), generator_name="void", raw_schema=test_input)
