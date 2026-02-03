# import pytest
import os
import tempfile
import warnings
from pathlib import Path

import cv2
import numpy as np

from main import *

# Suppress the warning related to -finishWriting
warnings.filterwarnings(
    "ignore", message=".*-finishWriting should not be called on the main thread.*"
)
warnings.filterwarnings("ignore", message="OpenCV: AVF: waiting to write video data.")


# temp_directory = tempfile.mkdtemp()


def generate_random_frame(width, height):
    return np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)


def create_video_file(
    file_name, frame_count, frame_width=1980, frame_height=1080, fps=60
):
    # Create a VideoWriter object to save the video
    fourcc = cv2.VideoWriter_fourcc(
        *"H264"
    )  # Codec for the output video (H.264 format)
    output_video_path = file_name + ".MP4"
    video_writer = cv2.VideoWriter(
        output_video_path, fourcc, fps, (frame_width, frame_height)
    )

    # Generate frames and save them to the video file
    for _ in range(frame_count):
        frame = generate_random_frame(frame_width, frame_height)
        video_writer.write(frame)

        # Release the VideoWriter and close the video file
        video_writer.release()

    print("Video created and saved as:", output_video_path)


# Function to calculate the size of a directory and its subdirectories
def get_directory_size(directory):
    total_size = 0
    dir_path = Path(directory)
    for filepath in dir_path.rglob("*"):
        if filepath.is_file():
            total_size += filepath.stat().st_size
    return total_size


def test_dir_no_subs1():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        test_files_path = Path(temp_dir)
        (test_files_path / "folder1").mkdir()
        (test_files_path / "folder2").mkdir()
        (test_files_path / "folder3" / "subfolder1").mkdir(parents=True)

        # Call the function to be tested
        test_nsub_list = dir_no_subs(test_files_path)

        # Assert that the expected paths are present in the correct order
        assert test_nsub_list == [
            test_files_path / "folder1",
            test_files_path / "folder2",
            test_files_path / "folder3" / "subfolder1",
        ]


def test_dir_no_subs2():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()
        (temp_path / "dir2" / "subdir1").mkdir(parents=True)
        (temp_path / "dir2" / "subdir2").mkdir()
        (temp_path / "dir3").mkdir()

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_path)

        # Assert that the expected paths are present in the correct order
        assert test_nsub_list == [
            temp_path / "dir1",
            temp_path / "dir2" / "subdir1",
            temp_path / "dir2" / "subdir2",
            temp_path / "dir3",
        ]


def test_dir_no_subs3():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_path)

        # Assert that the expected paths are present in the correct order
        assert test_nsub_list == [temp_path / "dir1"]


def test_dir_no_subs4():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        temp_path = Path(temp_dir)
        (temp_path / "dir1").mkdir()
        (temp_path / "dir2" / "subdir1").mkdir(parents=True)
        (temp_path / "dir1" / "file1.txt").touch()

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_path)

        # Assert that the expected paths are present in the correct order
        assert test_nsub_list == [
            temp_path / "dir1",
            temp_path / "dir2" / "subdir1",
        ]


class MockArgs:
    def __init__(self, d=False, c=False, j=None, f=None, y=True):
        self.d = d
        self.c = c
        self.j = j
        self.f = f
        self.y = y


def test_ffmpeg_concat1():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)

        args = MockArgs(d=False, c=False)
        ffmpeg_concat(temp_path, temp_path, args)
        end_file = temp_path / f"{temp_path.name}.MP4"
        assert end_file.exists()
        assert (temp_path / "files to delete").exists()
        print(end_file.stat().st_size)


def test_ffmpeg_concat2():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)
        args = MockArgs(d=True, c=False)
        ffmpeg_concat(temp_path, temp_path, args)
        end_file = temp_path / f"{temp_path.name}.MP4"
        print(list(temp_path.iterdir()))
        assert end_file.exists()


def test_ffmpeg_concat3():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        os.chdir(temp_path)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)
        folder_size = get_directory_size(temp_path)
        args = MockArgs(d=True, c=True)
        ffmpeg_concat(temp_path, temp_path, args)
        end_file = temp_path / f"{temp_path.name}.MP4"
        concat_size = end_file.stat().st_size
        print(list(temp_path.iterdir()))
        assert end_file.exists()
        assert folder_size > concat_size


# print("main folder: ", temp_directory)

# # List all files in the temporary directory
# files_in_temp_directory = os.listdir(temp_directory)
# print("Files in temporary directory:")
# for file_name in files_in_temp_directory:
#     tempabp = os.path.join(temp_directory, file_name)
#     print(file_name, os.path.getsize(tempabp))

# os.chdir(temp_directory)
# ffmpeg_concat()


# files_in_temp_directory = os.listdir(temp_directory)
# print("Files in temporary directory:")
# for file_name in files_in_temp_directory:
#     tempabp = os.path.join(temp_directory, file_name)
#     print(file_name, os.path.getsize(tempabp))


"""
Things to Test:åœ
ffmpeg_concat:
dir_no_subs
check_c
check_d
check_f
main

"""
