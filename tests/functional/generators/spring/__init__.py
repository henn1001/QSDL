"""Functional tests and helpers for the Spring generator.

The existing Spring test modules remain in the parent package until WP-10.  The
export below provides the target-specific import path for new tests without
moving those files early.
"""

from ..spring_test_utils import SpringTestUtils

__all__ = ["SpringTestUtils"]
