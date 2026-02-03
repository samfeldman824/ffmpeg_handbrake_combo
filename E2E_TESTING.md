# End-to-End (E2E) Testing Guide

This document describes the comprehensive E2E test suite for the FFmpeg/HandBrake video processing tool.

## What Was Added

### 1. `-y` / `--yes` Flag (main.py)
Added a new command-line flag to skip all interactive confirmation prompts:
- `-y` or `--yes`: Automatically confirms all prompts (compression, deletion, folder execution)

This enables fully automated testing without user interaction.

### 2. E2E Test Suite (test_e2e.py)
Comprehensive test suite with **22+ tests** covering:

#### Test Categories

**CLI E2E Tests (TestCLIE2E)**
- `test_cli_basic_concatenation`: Full CLI workflow via subprocess
- `test_cli_concatenation_with_delete`: CLI with delete flag
- `test_cli_concatenation_with_compression`: CLI with compression (HandBrake)
- `test_cli_with_filepath_flag`: CLI with -f directory specification
- `test_cli_help_flag`: Help output verification
- `test_cli_no_videos_found`: Graceful handling of empty directories

**Integration E2E Tests (TestIntegrationE2E)**
- `test_full_workflow_basic`: Concatenation with archiving
- `test_full_workflow_delete`: Concatenation with deletion
- `test_full_workflow_compression`: Concatenation + compression + deletion
- `test_nested_directory_structure`: Processing nested folders
- `test_multiple_runs_idempotent`: Safety of multiple executions

**Tool Validation Tests (TestToolValidation)**
- `test_validate_tools_success`: Validation when tools are present
- `test_validate_tools_missing_handbrake`: Error handling for missing HandBrakeCLI

**Confirmation Prompt Tests (TestConfirmationPrompts)**
- Tests for `-y` flag behavior with all confirmation functions

**Edge Cases (TestEdgeCases)**
- `test_empty_directory`: Graceful handling of empty directories
- `test_single_video`: Processing single video files
- `test_large_file_size_filter`: Files over 4.2GB limit exclusion
- `test_non_mp4_files_ignored`: Non-MP4 file handling

**Performance Tests (TestPerformance)**
- `test_many_small_videos`: Handling many small files efficiently

**Main Entry Point Tests (TestMainEntryPoint)**
- `test_main_with_yes_flag`: Full main() execution with -y
- `test_main_with_all_flags`: Main() with multiple flags

### 3. pytest Configuration (pytest.ini)
Configured pytest with:
- Custom markers for selective test running
- Logging configuration
- Test discovery patterns

## How to Run Tests

### Run All Tests
```bash
pytest
```

### Run Only E2E Tests
```bash
pytest test_e2e.py
```

### Run Tests Without HandBrake (faster)
```bash
pytest -m "not handbrake"
```

### Run Only HandBrake Tests
```bash
pytest -m "handbrake"
```

### Run Specific Test Class
```bash
pytest test_e2e.py::TestCLIE2E
pytest test_e2e.py::TestIntegrationE2E
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Debug Logging
```bash
pytest --log-cli-level=DEBUG
```

## Test Markers

- `e2e`: All end-to-end tests
- `handbrake`: Tests requiring HandBrakeCLI
- `slow`: Longer-running tests
- `integration`: Integration tests

## Test Coverage

The E2E test suite covers:

✅ **All CLI flags**: -d, -c, -f, -j, -y  
✅ **All workflows**: concat only, concat+delete, concat+compress+delete  
✅ **Directory structures**: Flat and nested directories  
✅ **Tool validation**: ffmpeg, ffprobe, HandBrakeCLI  
✅ **Error scenarios**: Missing tools, empty directories, large files  
✅ **File operations**: Concatenation, compression, archiving, deletion  
✅ **Video verification**: Duration validation, file integrity  
✅ **Edge cases**: Single videos, non-MP4 files, size limits  

## Example Usage

### Basic Concatenation (Interactive)
```bash
python main.py
# Will prompt for confirmation
```

### Automated Concatenation with Deletion
```bash
python main.py -d -y
```

### Full Workflow with Compression
```bash
python main.py -c -d -y
```

### Process Specific Directory
```bash
python main.py -f /path/to/videos -d -y
```

### Custom HandBrake Preset
```bash
python main.py -c -j preset.json -d -y
```

## CI/CD Integration

For automated testing in CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run E2E Tests
  run: |
    pytest test_e2e.py -m "not handbrake" -v
```

The `-y` flag makes the tool fully automatable for CI/CD pipelines.
