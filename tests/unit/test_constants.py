"""Tests for malta.constants path validation."""

from malta.constants import CONFIG_DIR, EXAMPLES_DIR, MALTA_ROOT, REPO_ROOT


class TestConstantsValidation:
    """Verify all constants are valid paths."""

    def test_repo_root_exists(self):
        """REPO_ROOT should exist and be a directory."""
        assert REPO_ROOT.exists()
        assert REPO_ROOT.is_dir()

    def test_malta_root_exists(self):
        """MALTA_ROOT should exist and be a directory."""
        assert MALTA_ROOT.exists()
        assert MALTA_ROOT.is_dir()

    def test_config_dir_exists(self):
        """CONFIG_DIR should exist and contain simulation configs."""
        assert CONFIG_DIR.exists()
        assert CONFIG_DIR.is_dir()
        configs = list(CONFIG_DIR.glob("*.json"))
        assert len(configs) > 0, "CONFIG_DIR should contain at least one .json config"

    def test_examples_dir_exists(self):
        """EXAMPLES_DIR should exist and contain examples."""
        assert EXAMPLES_DIR.exists()
        assert EXAMPLES_DIR.is_dir()

    def test_malta_root_is_subdir_of_repo_root(self):
        """MALTA_ROOT should be a subdirectory of REPO_ROOT."""
        assert MALTA_ROOT.parent == REPO_ROOT
