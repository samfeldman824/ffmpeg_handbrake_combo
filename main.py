"""System module"""
import shutil
import argparse
import os
import platform
import subprocess
import logging
from natsort import natsorted

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Default file size limit in bytes (4.2 GB)
DEFAULT_SIZE_LIMIT = 4200000000

def run_command(cmd_list: list[str], error_message: str) -> None:
    """Helper function to run subprocess commands with error handling"""
    try:
        subprocess.run(cmd_list, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError(error_message)


def get_video_duration(file_path: str) -> float:
    """Get video duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", file_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.strip() if e.stderr else "No error output"
        raise RuntimeError(f"Failed to get duration for {file_path}: {stderr_msg}")
    except ValueError as e:
        raise RuntimeError(f"Failed to parse duration for {file_path}: {e}")


def verify_output_file(file_path: str, operation: str) -> None:
    """Verify that output file exists and has content"""
    if not os.path.exists(file_path):
        raise RuntimeError(f"{operation} failed: output file {file_path} does not exist")
    if os.path.getsize(file_path) == 0:
        raise RuntimeError(f"{operation} failed: output file {file_path} is empty")


def verify_duration_match(input_duration: float, output_duration: float, operation: str, tolerance: float = 1.0) -> None:
    """Verify that output duration matches input duration within tolerance"""
    logger.info("Input duration: %.3f seconds", input_duration)
    logger.info("Output duration: %.3f seconds", output_duration)
    
    if abs(output_duration - input_duration) > tolerance:
        raise RuntimeError(
            f"{operation} verification failed: output duration ({output_duration:.3f}s) "
            f"does not match input duration ({input_duration:.3f}s)"
        )
    
    logger.info("Duration verification passed")


def ffmpeg_concat(root: str, r_dir: str, args: argparse.Namespace) -> None:
    """finds and combines all MP4 files in folder"""
    
    # Use absolute paths to avoid directory changes
    current_path = r_dir
    title = os.path.basename(r_dir)
    
    # initialize empty list to store files that will be concatenated
    filelist = []

    # loop through each file in current directory
    for filename in os.listdir(current_path):
        # Checks that file ends with ".mp4" (case insensitive) and is smaller than size limit
        if filename.lower().endswith(".mp4") and os.path.getsize(os.path.join(current_path, filename)) < DEFAULT_SIZE_LIMIT:
            # adds filename to "filelist" if conditions are met
            filelist.append(filename)

    # sorts "filelist" using "natural sorting"
    filelist = natsorted(filelist)

    # Check if any MP4 files were found
    if not filelist:
        logger.warning("No MP4 files found in %s, skipping", current_path)
        return

    # initialize combined size all files in folder starting at 0
    folder_size = 0

    # build ffmpeg file list entries
    files_txt_entries = []
    for file in filelist:
        # Calculate size of all files in list
        folder_size += os.path.getsize(os.path.join(current_path, file))
        # build file entry formatted for ffmpeg
        files_txt_entries.append(f"file '{file}'\n")

    # write all entries to files.txt in one operation
    files_txt_path = os.path.join(current_path, "files.txt")
    with open(files_txt_path, "w", encoding="utf8") as f:
        f.writelines(files_txt_entries)

    # run ffmpeg command that concatenates all files into one bigger file
    output_file = os.path.join(current_path, f"{title}.mp4")
    run_command([
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", files_txt_path,
        "-c", "copy",
        output_file
    ], "FFmpeg concatenation failed")
    
    try:
        # === VERIFICATION: Check output file exists and has content ===
        verify_output_file(output_file, "Concatenation")
        
        # === VERIFICATION: Verify video duration matches sum of inputs ===
        total_input_duration = 0.0
        for file in filelist:
            file_path = os.path.join(current_path, file)
            duration = get_video_duration(file_path)
            total_input_duration += duration
            logger.debug("Input file %s duration: %.3f seconds", file, duration)
        
        output_duration = get_video_duration(output_file)
        verify_duration_match(total_input_duration, output_duration, "Concatenation")
    finally:
        # remove uneeded "files.txt" file after verification (even if it failed)
        os.remove(files_txt_path)
    
    # calculate size of the newly concatenated file
    concat_file = os.path.getsize(output_file)
    
    # log size of all smaller files and the concatenated file
    logger.info("Folder size: %d bytes", folder_size)
    logger.info("Concat size: %d bytes", concat_file)

    # if user did not add "-d" flag to save old files
    if not args.d:
        # create folder where old files from current directory will be moved to
        split_files_dir = os.path.join(current_path, f"{title} split files")
        os.makedirs(split_files_dir, exist_ok=True)
        
        # move each file to folder for old files
        for file in filelist:
            source = os.path.join(current_path, file)
            destination = os.path.join(split_files_dir, file)
            shutil.move(source, destination)
            
        # move current folder for old files to main folder for old files
        files_to_delete_path = os.path.join(root, "files to delete")
        os.makedirs(files_to_delete_path, exist_ok=True)
        split_destination = os.path.join(files_to_delete_path, f"{title} split files")
        shutil.move(split_files_dir, split_destination)

    # if user added "-c" flag to compress the concatenated file
    if args.c:
        # Build HandBrakeCLI command dynamically
        input_file = os.path.join(current_path, f"{title}.mp4")
        output_file = os.path.join(current_path, f"{title}(cp).mp4")
        
        cmd = ["HandBrakeCLI", "-i", input_file, "-o", output_file]
        
        # if user added "-j" flag to use customized json file for handbrake
        if args.j:
            cmd.extend(["--preset-import-file", args.j])
        else:
            # Add preset and common options
            cmd.extend([
                "--preset", "Very Fast 1080p30",
                "-r", "same as source",
                "--encoder-level", "auto"
            ])
            
            # if running on MacOS, use VideoToolBox which is more efficient
            if platform.system() == "Darwin":
                cmd.extend(["-e", "vt_h265", "-q", "30"])
            else:
                cmd.extend(["-e", "h265", "-q", "22"])
        
        run_command(cmd, "HandBrake compression failed")
        
        # === VERIFICATION: Check compressed file exists and has content ===
        verify_output_file(output_file, "Compression")
        
        # === VERIFICATION: Verify compressed file duration matches input ===
        input_duration = get_video_duration(input_file)
        output_duration = get_video_duration(output_file)
        verify_duration_match(input_duration, output_duration, "Compression")

    # if user added "-d" flag to delete old files
    if args.d:
        # loop through each file in sorted filelist and delete file
        for file in filelist:
            os.remove(os.path.join(current_path, file))
        # if user added "-c" flag to compress concatenated files
        if args.c:
            # remove non-compressed file and rename compressed file
            new = os.path.join(current_path, f"{title}.mp4")
            old = os.path.join(current_path, f"{title}(cp).mp4")
            os.remove(new)
            os.rename(old, new)


def dir_no_subs(directory_path: str) -> list[str]:
    """finds all directories with no subdirectories and returns their
    absolute paths as a list using iterative os.walk()"""

    has_subdirectories = set()
    all_directories = []
    nsub_list = []

    # Walk through all directories iteratively
    for dirpath, dirnames, _ in os.walk(directory_path):
        all_directories.append(dirpath)
        if dirnames:
            has_subdirectories.add(dirpath)

    # Find leaf directories (those with no subdirectories)
    for dirpath in all_directories:
        if dirpath not in has_subdirectories:
            nsub_list.append(dirpath)

    # If no leaf directories found, add the root directory
    if not nsub_list:
        nsub_list.append(directory_path)

    return nsub_list


def check_c(args: argparse.Namespace) -> None:
    """confirms user intends to compress their files"""
    # if user added "-c" flag to compress concatenated files
    if args.c:
        while True:
            # ask user to confirm
            answer = input(
                "Are you sure you want to compress all concatenated files? (y/n) ")
            # if user confirms, continue
            if answer.lower() == 'y':
                logger.info("Confirmed")
                break
            # if user does not confirm, exit program
            elif answer.lower() == 'n':
                logger.info("Exiting")
                exit()
            # if user response is not readable, ask question again
            else:
                logger.warning("Invalid response. Please type y or n")

def check_d(args: argparse.Namespace) -> None:
    """confirms user intends to delete leftover files"""
    # if user added "-d" flag to delete old files
    if args.d:
        while True:
            # ask user to confirm
            answer = input(
                "Are you sure you want to delete the leftover files? (y/n) ")
            # if user confirms, continue
            if answer.lower() == 'y':
                logger.info("Confirmed")
                break
            # if user does not confirm, exit program
            elif answer.lower() == 'n':
                logger.info("Exiting")
                exit()
            # if user response is not readable, ask question again
            else:
                logger.warning("Invalid response. Please type y or n")


def check_f(folder: str) -> None:
    """confirms user intends to execute main on specified folder"""
    while True:
        # asks user to confirm the current working directory is correct
        answer = input(f"Do you want to proceed in folder -- {folder}? (y/n) ")

        # if user confirms, continue
        if answer.lower() == 'y':
            logger.info("Confirmed")
            break
        # if user does not confirm, exit program
        elif answer.lower() == 'n':
            logger.info("Exiting")
            exit()
        # if user response is not readable, ask question again
        else:
            logger.warning("Invalid response. Please type y or n")


def validate_tools(args: argparse.Namespace) -> None:
    """Check that required tools (ffmpeg, ffprobe, and HandBrakeCLI) are installed"""
    # Check for ffmpeg (always required)
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is not installed or not in PATH. Please install ffmpeg.")

    # Check for ffprobe (separate binary but usually bundled with ffmpeg)
    if shutil.which("ffprobe") is None:
        raise RuntimeError(
            "ffprobe is not installed or not in PATH. "
            "ffprobe is typically included with ffmpeg. "
            "Please ensure your ffmpeg installation includes ffprobe."
        )

    # Check for HandBrakeCLI only if compression flag is set
    if args.c and shutil.which("HandBrakeCLI") is None:
        raise RuntimeError("HandBrakeCLI is not installed or not in PATH. Please install HandBrakeCLI or run without the -c flag.")


def main() -> None:
    """Main entry point for the script"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '-delete', help='Delete leftover files', action='store_true')
    parser.add_argument('-c', '-compress',
                        help='Compress concatenated files', action='store_true')
    parser.add_argument('-f', '-filepath',
                        help='Run script in specified directory')
    parser.add_argument(
        '-j', '-json', help='Run compression with preset from given JSON file')
    args = parser.parse_args()

    # if user added "-f" flag to indicate which directory to run program in
    if args.f:
        # changes current working directory to given filepath
        os.chdir(args.f)
        
    # sets "base_dir" as the absolute path of current working directory
    base_dir = os.getcwd()
    
    # sets "folder" as base path of current working directory
    folder = os.path.basename(base_dir)

    # Validate that required tools are installed
    validate_tools(args)

    logger.info('Starting')

    # if user added "-d" flag to delete old files
    if args.d:
        # asks user to confirm
        check_d(args)
    # if user added "-c" flag to compress concatenated files
    if args.c:
        # asks user to confirm
        check_c(args)

    # asks user to confirm current working directory is correct
    check_f(folder)

    # fills "directory_list" with all directories to run ffmpeg in
    directory_list = dir_no_subs(base_dir)

    # if user did not add "-d" flag to delete old files
    if not args.d:
        # creates directory to store old files
        os.makedirs(os.path.join(base_dir, "files to delete"), exist_ok=True)

    # loops through each folder in "directory_list"
    for directory in directory_list:
        # runs ffmpeg in current working directory
        ffmpeg_concat(base_dir, directory, args)

    logger.info("FINISHED")


if __name__ == "__main__":
    main()
