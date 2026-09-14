"""Pytest configuration for unit tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: fast, isolated unit tests (default for this directory)")


def pytest_collection_modifyitems(session, config, items):
    """Automatically apply @pytest.mark.unit to all tests in this directory."""
    for item in items:
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
