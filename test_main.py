"""
Unit Test Suite for FFmpeg/HandBrake Video Processing Tool

This test suite provides unit tests for isolated function testing:
- dir_no_subs: Directory traversal logic
- check_c, check_d, check_f: Confirmation prompt logic
- validate_tools: Tool validation logic

For integration and E2E tests, see test_e2e.py
"""

import tempfile
from pathlib import Path

import pytest

from main import (
    dir_no_subs,
    check_c,
    check_d,
    check_f,
    validate_tools,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_args():
    """Factory fixture to create mock args objects"""
    class MockArgs:
        def __init__(self, d=False, c=False, j=None, y=True, f=None):
            self.d = d
            self.c = c
            self.j = j
            self.y = y
            self.f = f
    
    return MockArgs


# =============================================================================
# Unit Tests - dir_no_subs
# =============================================================================

def test_dir_no_subs1():
    """Test dir_no_subs with simple folder structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "folder1").mkdir()
        (temp_path / "folder2").mkdir()
        (temp_path / "folder3" / "subfolder1").mkdir(parents=True)

        test_nsub_list = dir_no_subs(temp_path)

        assert test_nsub_list == [
            temp_path / "folder1",
            temp_path / "folder2",
            temp_path / "folder3" / "subfolder1",
        ]


def test_dir_no_subs2():
    """Test dir_no_subs with multiple nested subdirectories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()
        (temp_path / "dir2" / "subdir1").mkdir(parents=True)
        (temp_path / "dir2" / "subdir2").mkdir()
        (temp_path / "dir3").mkdir()

        test_nsub_list = dir_no_subs(temp_path)

        assert test_nsub_list == [
            temp_path / "dir1",
            temp_path / "dir2" / "subdir1",
            temp_path / "dir2" / "subdir2",
            temp_path / "dir3",
        ]


def test_dir_no_subs3():
    """Test dir_no_subs with single directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()

        test_nsub_list = dir_no_subs(temp_path)

        assert test_nsub_list == [temp_path / "dir1"]


def test_dir_no_subs4():
    """Test dir_no_subs ignores files, only returns directories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()
        (temp_path / "dir2" / "subdir1").mkdir(parents=True)
        (temp_path / "dir1" / "file1.txt").touch()

        test_nsub_list = dir_no_subs(temp_path)

        assert test_nsub_list == [
            temp_path / "dir1",
            temp_path / "dir2" / "subdir1",
        ]


# =============================================================================
# Unit Tests - Tool Validation
# =============================================================================

class TestToolValidation:
    """Tests for tool validation and error handling"""
    
    def test_validate_tools_success(self, mock_args):
        """Test tool validation when tools are present"""
        args = mock_args()
        # Should not raise if ffmpeg/ffprobe are installed
        try:
            validate_tools(args)
        except RuntimeError as e:
            if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
                pytest.skip("ffmpeg/ffprobe not installed")
            raise


# =============================================================================
# Unit Tests - Confirmation Prompts
# =============================================================================

class TestConfirmationPrompts:
    """Tests for user confirmation prompts with -y flag"""
    
    def test_check_c_skips_with_yes_flag(self, mock_args, caplog):
        """Test check_c skips prompt when -y flag is set"""
        args = mock_args(c=True, y=True)
        
        # Should not raise or prompt
        check_c(args)
        
        # Verify it logged the skip
        assert "confirmed via -y flag" in caplog.text.lower()
    
    def test_check_d_skips_with_yes_flag(self, mock_args, caplog):
        """Test check_d skips prompt when -y flag is set"""
        args = mock_args(d=True, y=True)
        
        # Should not raise or prompt
        check_d(args)
        
        # Verify it logged the skip
        assert "confirmed via -y flag" in caplog.text.lower()
    
    def test_check_f_skips_with_yes_flag(self, mock_args, caplog):
        """Test check_f skips prompt when -y flag is set"""
        args = mock_args(y=True)
        
        # Should not raise or prompt
        check_f("test_folder", args)
        
        # Verify it logged the skip
        assert "confirmed via -y flag" in caplog.text.lower()
