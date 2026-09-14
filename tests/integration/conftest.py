"""Pytest configuration for integration tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: slower tests that check multiple components working together")


def pytest_collection_modifyitems(session, config, items):
    """Automatically apply @pytest.mark.integration to all tests in this directory."""
    for item in items:
        if "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
