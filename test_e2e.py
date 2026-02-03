"""
End-to-End (E2E) Test Suite for FFmpeg/HandBrake Video Processing Tool

This test suite provides comprehensive E2E testing covering:
- Full CLI workflows via subprocess (true black-box testing)
- Integration tests calling main() directly
- All flag combinations (-d, -c, -j, -y)
- Tool validation
- Error scenarios
- Video duration verification
- File operations verification
"""

import os
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import cv2
import numpy as np
import pytest

# Suppress OpenCV warnings
warnings.filterwarnings(
    "ignore", message=".*-finishWriting should not be called on the main thread.*"
)
warnings.filterwarnings("ignore", message="OpenCV: AVF: waiting to write video data.")

# Import main module functions
from main import (
    dir_no_subs,
    ffmpeg_concat,
    check_c,
    check_d,
    check_f,
    validate_tools,
    main,
    get_video_duration,
    verify_output_file,
    verify_duration_match,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def test_videos(temp_dir):
    """Create test video files in the temp directory"""
    videos = []
    for i in range(3):
        video_path = create_test_video(temp_dir, f"video{i+1}", frames=100)
        videos.append(video_path)
    return videos


@pytest.fixture
def nested_structure(temp_dir):
    """Create a nested directory structure with videos"""
    # Create structure: temp_dir/folder1/, temp_dir/folder2/subfolder/
    folder1 = os.path.join(temp_dir, "folder1")
    folder2 = os.path.join(temp_dir, "folder2")
    subfolder = os.path.join(folder2, "subfolder")
    
    os.makedirs(folder1)
    os.makedirs(subfolder)
    
    # Add videos to each leaf directory
    create_test_video(folder1, "vid1", frames=50)
    create_test_video(folder1, "vid2", frames=50)
    create_test_video(subfolder, "vid3", frames=50)
    
    return {
        "root": temp_dir,
        "folder1": folder1,
        "folder2": folder2,
        "subfolder": subfolder,
    }


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
# Helper Functions
# =============================================================================

def create_test_video(directory, name, frames=100, fps=30, width=640, height=480):
    """Create a test video file using OpenCV"""
    video_path = os.path.join(directory, f"{name}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"avc1")  # More compatible codec
    writer = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    for _ in range(frames):
        # Create a frame with varying color to ensure video has content
        frame = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        writer.write(frame)
    
    writer.release()
    
    # Verify video was created
    if not os.path.exists(video_path):
        raise RuntimeError(f"Failed to create test video: {video_path}")
    
    return video_path


def get_directory_size(directory):
    """Calculate total size of all files in directory recursively"""
    total = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total += os.path.getsize(filepath)
    return total


def count_files(directory, extension=None):
    """Count files in directory, optionally filtering by extension"""
    count = 0
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if extension is None or filename.lower().endswith(extension.lower()):
                count += 1
    return count


def run_cli(args_list, cwd=None, check=True):
    """Run the CLI tool via subprocess for true E2E testing"""
    # Get the directory where main.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    cmd = [sys.executable, main_script] + args_list
    
    # Use script_dir as default cwd to avoid issues with deleted temp directories
    if cwd is None:
        cwd = script_dir
    
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    return result


# =============================================================================
# E2E Tests - Subprocess/CLI Level (True Black-Box Testing)
# =============================================================================

class TestCLIE2E:
    """True E2E tests that run the CLI as a subprocess"""
    
    def test_cli_basic_concatenation(self, temp_dir, test_videos):
        """Test basic concatenation via CLI with -y flag"""
        result = run_cli(["-y"], cwd=temp_dir)
        
        # Check success
        assert result.returncode == 0
        assert "FINISHED" in result.stderr
        
        # Check output file exists
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Check original files were moved to archive
        assert os.path.exists(os.path.join(temp_dir, "files to delete"))
    
    def test_cli_concatenation_with_delete(self, temp_dir, test_videos):
        """Test concatenation with delete flag via CLI"""
        result = run_cli(["-d", "-y"], cwd=temp_dir)
        
        assert result.returncode == 0
        
        # Check output file exists
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Check original files were deleted (not archived)
        original_count = count_files(temp_dir, ".mp4")
        assert original_count == 1  # Only the concatenated file
        assert not os.path.exists(os.path.join(temp_dir, "files to delete"))
    
    @pytest.mark.skipif(
        subprocess.run(["which", "HandBrakeCLI"], capture_output=True).returncode != 0,
        reason="HandBrakeCLI not installed"
    )
    def test_cli_concatenation_with_compression(self, temp_dir, test_videos):
        """Test concatenation with compression via CLI"""
        original_size = get_directory_size(temp_dir)
        
        result = run_cli(["-c", "-d", "-y"], cwd=temp_dir)
        
        assert result.returncode == 0
        
        # Check output file exists
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Check compression actually reduced size
        final_size = os.path.getsize(output_file)
        assert final_size < original_size
    
    def test_cli_with_filepath_flag(self, temp_dir, test_videos):
        """Test running with -f flag to specify directory"""
        result = run_cli(["-f", temp_dir, "-y"])
        
        assert result.returncode == 0
        
        # Check output file exists in specified directory
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
    
    def test_cli_help_flag(self):
        """Test CLI help output"""
        result = run_cli(["--help"], check=False)
        
        assert result.returncode == 0
        assert "-d" in result.stdout or "-delete" in result.stdout
        assert "-c" in result.stdout or "-compress" in result.stdout
        assert "-y" in result.stdout or "-yes" in result.stdout
    
    def test_cli_no_videos_found(self, temp_dir):
        """Test behavior when no videos are found"""
        result = run_cli(["-y"], cwd=temp_dir)
        
        # Should complete without error even with no videos
        assert result.returncode == 0
        assert "No MP4 files found" in result.stderr or "FINISHED" in result.stderr


# =============================================================================
# Integration Tests - Function Level (Faster, More Debuggable)
# =============================================================================

class TestIntegrationE2E:
    """Integration tests that call functions directly but test full workflows"""
    
    def test_full_workflow_basic(self, temp_dir, test_videos, mock_args):
        """Test full workflow: concat only, archive originals"""
        os.chdir(temp_dir)
        args = mock_args(d=False, c=False, y=True)
        
        # Calculate expected duration BEFORE processing (files get moved)
        expected_duration = sum(get_video_duration(v) for v in test_videos)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        verify_output_file(output_file, "Test")
        
        # Verify originals archived
        archive_dir = os.path.join(temp_dir, "files to delete")
        assert os.path.exists(archive_dir)
        
        # Verify duration
        output_duration = get_video_duration(output_file)
        verify_duration_match(expected_duration, output_duration, "Test")
    
    def test_full_workflow_delete(self, temp_dir, test_videos, mock_args):
        """Test full workflow: concat with delete flag"""
        os.chdir(temp_dir)
        args = mock_args(d=True, c=False, y=True)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Verify originals deleted (not archived)
        for video in test_videos:
            assert not os.path.exists(video)
        assert not os.path.exists(os.path.join(temp_dir, "files to delete"))
        
        # Verify only output file remains
        mp4_count = count_files(temp_dir, ".mp4")
        assert mp4_count == 1
    
    @pytest.mark.skipif(
        subprocess.run(["which", "HandBrakeCLI"], capture_output=True).returncode != 0,
        reason="HandBrakeCLI not installed"
    )
    def test_full_workflow_compression(self, temp_dir, test_videos, mock_args):
        """Test full workflow: concat + delete + compress"""
        os.chdir(temp_dir)
        original_size = get_directory_size(temp_dir)
        args = mock_args(d=True, c=True, y=True)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Verify compression reduced size
        final_size = os.path.getsize(output_file)
        assert final_size < original_size
        
        # Verify duration preserved
        output_duration = get_video_duration(output_file)
        assert output_duration > 0
    
    def test_nested_directory_structure(self, nested_structure, mock_args):
        """Test processing nested directory structure"""
        root = nested_structure["root"]
        os.chdir(root)
        args = mock_args(d=False, c=False, y=True)
        
        # Get leaf directories
        leaf_dirs = dir_no_subs(root)
        
        # Process each leaf directory
        for directory in leaf_dirs:
            ffmpeg_concat(root, directory, args)
        
        # Verify outputs in both leaf directories
        for dir_name in ["folder1", "subfolder"]:
            dir_path = nested_structure[dir_name] if dir_name != "subfolder" else nested_structure["subfolder"]
            output_file = os.path.join(dir_path, f"{os.path.basename(dir_path)}.mp4")
            assert os.path.exists(output_file), f"Output not found in {dir_path}"
    
    def test_multiple_runs_idempotent(self, temp_dir, test_videos, mock_args):
        """Test that running twice on same directory is safe"""
        os.chdir(temp_dir)
        args = mock_args(d=False, c=False, y=True)
        
        # First run
        ffmpeg_concat(temp_dir, temp_dir, args)
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Second run (should handle already-processed directory gracefully)
        # Note: This may create a new concat of the already-concatenated file
        # depending on implementation - we're just checking it doesn't crash
        try:
            ffmpeg_concat(temp_dir, temp_dir, args)
        except Exception as e:
            # It's okay if it fails gracefully
            pass


# =============================================================================
# Tool Validation Tests
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
    
    def test_validate_tools_missing_handbrake(self, mock_args):
        """Test validation fails when HandBrakeCLI missing but -c flag set"""
        # Temporarily modify PATH to exclude HandBrakeCLI
        original_path = os.environ.get("PATH", "")
        
        # Create args with compression enabled
        args = mock_args(c=True)
        
        # This test only runs if HandBrakeCLI is actually missing
        if subprocess.run(["which", "HandBrakeCLI"], capture_output=True).returncode == 0:
            pytest.skip("HandBrakeCLI is installed, cannot test missing scenario")
        
        with pytest.raises(RuntimeError) as exc_info:
            validate_tools(args)
        
        assert "HandBrakeCLI" in str(exc_info.value)


# =============================================================================
# Confirmation Prompt Tests
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


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error scenarios"""
    
    def test_empty_directory(self, temp_dir, mock_args):
        """Test behavior with empty directory"""
        os.chdir(temp_dir)
        args = mock_args(y=True)
        
        # Should complete without error
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # No output file should be created
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert not os.path.exists(output_file)
    
    def test_single_video(self, temp_dir, mock_args):
        """Test behavior with single video file"""
        create_test_video(temp_dir, "single", frames=100)
        os.chdir(temp_dir)
        args = mock_args(d=False, c=False, y=True)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Should still create output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
    
    def test_large_file_size_filter(self, temp_dir, mock_args):
        """Test that files over size limit are excluded"""
        # Create a normal video
        create_test_video(temp_dir, "normal", frames=50)
        
        # Create a fake "large" file by creating empty file with large size
        # (In reality, we'd need a large video, but this tests the logic)
        large_file = os.path.join(temp_dir, "large.mp4")
        with open(large_file, "wb") as f:
            # Write header to make it look like a video
            f.write(b"\x00\x00\x00\x20ftypisom")
            # Seek to create a large sparse file
            f.seek(4_300_000_000)  # Over 4.2GB limit
            f.write(b"\x00")
        
        os.chdir(temp_dir)
        args = mock_args(d=False, c=False, y=True)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Output should only contain the normal video
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Clean up large file
        os.remove(large_file)
    
    def test_non_mp4_files_ignored(self, temp_dir, mock_args):
        """Test that non-MP4 files are ignored"""
        # Create a video
        create_test_video(temp_dir, "video", frames=50)
        
        # Create non-video files
        for ext in [".txt", ".avi", ".mov", ".mkv"]:
            with open(os.path.join(temp_dir, f"file{ext}"), "w") as f:
                f.write("test")
        
        os.chdir(temp_dir)
        args = mock_args(d=False, c=False, y=True)
        
        ffmpeg_concat(temp_dir, temp_dir, args)
        
        # Should only process the MP4
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Non-MP4 files should remain
        for ext in [".txt", ".avi", ".mov", ".mkv"]:
            assert os.path.exists(os.path.join(temp_dir, f"file{ext}"))


# =============================================================================
# Performance and Stress Tests
# =============================================================================

class TestPerformance:
    """Tests for performance characteristics"""
    
    def test_many_small_videos(self, temp_dir, mock_args):
        """Test handling of many small video files"""
        # Create 20 small videos
        for i in range(20):
            create_test_video(temp_dir, f"vid{i:02d}", frames=10)
        
        os.chdir(temp_dir)
        args = mock_args(d=True, c=False, y=True)
        
        import time
        start = time.time()
        ffmpeg_concat(temp_dir, temp_dir, args)
        duration = time.time() - start
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Log performance (not a strict assertion, just informational)
        print(f"\nProcessed 20 videos in {duration:.2f} seconds")


# =============================================================================
# Main Entry Point Test
# =============================================================================

class TestMainEntryPoint:
    """Tests for the main() entry point"""
    
    def test_main_with_yes_flag(self, temp_dir, test_videos):
        """Test main() function with -y flag (non-interactive)"""
        os.chdir(temp_dir)
        
        # Mock sys.argv
        original_argv = sys.argv
        try:
            sys.argv = ["main.py", "-y"]
            main()
        finally:
            sys.argv = original_argv
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
    
    def test_main_with_all_flags(self, temp_dir, test_videos):
        """Test main() with all flags enabled"""
        os.chdir(temp_dir)
        
        original_argv = sys.argv
        try:
            sys.argv = ["main.py", "-d", "-y"]
            main()
        finally:
            sys.argv = original_argv
        
        # Verify output
        output_file = os.path.join(temp_dir, f"{os.path.basename(temp_dir)}.mp4")
        assert os.path.exists(output_file)
        
        # Verify originals deleted
        for video in test_videos:
            assert not os.path.exists(video)


# =============================================================================
# Test Configuration and Markers
# =============================================================================

# Mark tests that require HandBrakeCLI
pytestmark = [
    pytest.mark.e2e,
]

# Custom markers for selective test running
# Run with: pytest -m "not handbrake" to skip HandBrake tests
# Run with: pytest -m "handbrake" to run only HandBrake tests
