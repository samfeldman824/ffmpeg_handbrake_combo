# import pytest
import os
import tempfile
import warnings

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
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size


def test_dir_no_subs1():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        test_files_path = temp_dir
        os.makedirs(os.path.join(temp_dir, "folder1"))
        os.makedirs(os.path.join(temp_dir, "folder2"))
        os.makedirs(os.path.join(temp_dir, "folder3", "subfolder1"))

        # Call the function to be tested
        test_nsub_list = dir_no_subs(test_files_path)

        # Assert that the expected paths are present in the test_nsub_list
        assert os.path.join(test_files_path, "folder1") in test_nsub_list
        assert os.path.join(test_files_path, "folder2") in test_nsub_list
        assert os.path.join(test_files_path, "folder3/subfolder1") in test_nsub_list


def test_dir_no_subs2():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        os.makedirs(os.path.join(temp_dir, "dir1"))
        os.makedirs(os.path.join(temp_dir, "dir2", "subdir1"))
        os.makedirs(os.path.join(temp_dir, "dir2", "subdir2"))
        os.makedirs(os.path.join(temp_dir, "dir3"))

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_dir)

        # Assert that the expected paths are present in the test_nsub_list
        assert os.path.join(temp_dir, "dir1") in test_nsub_list
        assert os.path.join(temp_dir, "dir2/subdir1") in test_nsub_list
        assert os.path.join(temp_dir, "dir2/subdir2") in test_nsub_list
        assert os.path.join(temp_dir, "dir3") in test_nsub_list


def test_dir_no_subs3():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        os.makedirs(os.path.join(temp_dir, "dir1"))

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_dir)

        # Assert that the expected paths are present in the test_nsub_list
        assert os.path.join(temp_dir, "dir1") in test_nsub_list


def test_dir_no_subs4():
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Populate the temporary directory with test data (folders and subfolders)
        os.makedirs(os.path.join(temp_dir, "dir1"))
        os.makedirs(os.path.join(temp_dir, "dir2", "subdir1"))
        with open(f"{temp_dir}/dir1/file1.txt", "w") as file:
            pass

        # Call the function to be tested
        test_nsub_list = dir_no_subs(temp_dir)

        # Assert that the expected paths are present in the test_nsub_list
        assert os.path.join(temp_dir, "dir2/subdir1") in test_nsub_list


class MockArgs:
    def __init__(self, d=False, c=False, j=None):
        self.d = d
        self.c = c
        self.j = j


def test_ffmpeg_concat1():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)

        args = MockArgs(d=False, c=False)
        ffmpeg_concat(temp_dir, temp_dir, args)
        end_file_name = f"{os.path.basename(temp_dir)}.MP4"
        assert os.path.exists(end_file_name)
        assert os.path.exists("files to delete")
        print(os.path.getsize(end_file_name))


def test_ffmpeg_concat2():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)
        args = MockArgs(d=True, c=False)
        ffmpeg_concat(temp_dir, temp_dir, args)
        end_file_name = f"{os.path.basename(temp_dir)}.MP4"
        print(os.listdir(temp_dir))
        assert os.path.exists(end_file_name)


def test_ffmpeg_concat3():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        for i in range(3):
            create_video_file(f"video{i + 1}", 200)
        folder_size = get_directory_size(temp_dir)
        args = MockArgs(d=True, c=True)
        ffmpeg_concat(temp_dir, temp_dir, args)
        end_file_name = f"{os.path.basename(temp_dir)}.MP4"
        concat_size = os.path.getsize(end_file_name)
        print(os.listdir(temp_dir))
        assert os.path.exists(end_file_name)
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
