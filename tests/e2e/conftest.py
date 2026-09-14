"""Pytest configuration for end-to-end tests."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "e2e: full system tests (slowest, comprehensive)")


def pytest_collection_modifyitems(session, config, items):
    """Automatically apply @pytest.mark.e2e to all tests in this directory."""
    for item in items:
        if "tests/e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
