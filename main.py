"""System module"""
import shutil
import argparse
import os
import platform
from natsort import natsorted
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

# os.chdir('/Users/samfeldman/Desktop/Tennis/testfolder copy 2')

def ffmpeg_concat():
    """finds and combines all MP4 files in folder"""

    # gets current directory
    current_path = os.getcwd()

    # gets name of folder from current directory
    title = os.path.basename(current_path) # name of folder will be used as name of file

    # creates "files.txt" file in current directory
    # "utf8" encoding is standard for text files
    open("files.txt", "x", encoding="utf8")



    # initialize empty list to store files that will be concatenated
    filelist = []


    # loop through each file in current directory
    for filename in os.listdir():
        # Checks that file ends with ".MP4" and is smaller the 4.2 GB
        if filename.endswith(".MP4") and os.path.getsize(filename) < 4200000000:
            # adds filename to "filelist" if conditions are met
            filelist.append(filename)

    # sorts "filelist" using "natural sorting"
    # puts file names in order of when they were shot
    filelist = natsorted(filelist)

    # initialize combined size all files in folder starting at 0
    folder_size = 0

    # loop through each file in sorted list
    for file in filelist:
        # Calculate size of all files in list
        folder_size += os.path.getsize(file)
        # open "files.txt" and write file name formatted for ffmpeg
        fopen = open("files.txt", "a", encoding="utf8")
        fopen.write("file '" + file + "'\n")
        fopen.close()

    # run ffmpeg command that concatenates all files into one bigger file
    os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy '{title}.MP4'")
    # remove uneeded "files.txt" file
    os.remove("files.txt")
    # calculate size of the newly concatenated file
    concat_file = os.path.getsize(f'{title}.MP4')
    # print out size of all smaller files and the concatenated file
    # ffmpeg will get rid of a few bytes when combining the videos
    # if both sizes are roughly the same, the concatenation worked correctly
    print("folder size: ", folder_size)
    print("concat size: ", concat_file)

    # if user did not add "-d" flag to save old files
    if args.d is False:
        # create folder where old files from current directory will be moved to
        os.mkdir(f"{title} split files")
        # get filepath of the folder for old files
        split_files_path = os.path.abspath(f"{title} split files")
        # loop through each file in sorted filelist
        for file in filelist:
            # move each file to folder for old files
            source = os.path.abspath(file)
            destination = split_files_path + '/' + file
            shutil.move(source, destination)
        # move current folder for old files to main folder for old files
        files_to_delete_path = path + '/' + ("files to delete")
        split_destination = files_to_delete_path + \
                '/' + f"{title} split files"
        shutil.move(split_files_path, split_destination)

    # if user added "-c" flag to compress the concatenated file
    if args.c:
        # if user added "-j" flag to use customized json file for handbrake
        if args.j:
            # run handbrake on concatenated file using given json file as presets
            os.system(
                f"HandBrakeCLI -i '{title}'.MP4 --preset-import-file {args.j} -o '{title}(cp)'.MP4")
        else:
            # if running on MacOS
            # MacOS computers can use "VideoToolBox", which is more efficient
            if platform.system() == "Darwin":
                # run handbrake on concatenated file using "VideoToolBox"
                os.system(
                    f"HandBrakeCLI -i '{title}'.MP4 -o '{title}(cp)'.MP4 --preset 'Very Fast 1080p30'\
                        -r 59.94 --encoder-level auto -e vt_h265 -q 30")
            else:
                # run handbrake on concatenated file using normal presets
                os.system(
                    f"HandBrakeCLI -i '{title}'.MP4 -o '{title}(cp)'.MP4 --preset 'Very Fast 1080p30'\
                        -r 59.94 --encoder-level auto -e h265 -q 22")

    # if user added "-d" flag to delete old files
    if args.d:
        # loop through each file in sorted filelist and delete file
        for file in filelist:
            os.remove(file)
        # if user added "-c" flag to compress concatenated files
        if args.c:
            # remove non-compressed file and rename compressed file
            new = os.path.abspath(f"{title}.MP4")
            os.remove(f"{title}.MP4")
            old = os.path.abspath(f"{title}(cp).MP4")
            os.rename(old, new)


def dir_no_subs(directory_path, nsub_list):
    """finds all directories with no subdirectories and appends their
    absolute path to given list"""
    for file in os.scandir(directory_path):
        if file.is_dir():
            os.chdir(file.path)
            nsub = True
            for subfile in os.scandir(file.path):
                if subfile.is_dir():
                    nsub = False
                    break
                continue
            if nsub:
                nsub_list.append(file.path)
            dir_no_subs(file, nsub_list)
    if not nsub_list:
        nsub_list.append(path)


def main():
    """executes ffmpeg_concat in each folder nsub list"""
    directory_list = []
    dir_no_subs(path, directory_list)

    if args.d is False:
        os.mkdir(path + '/' + "files to delete")

    for file in directory_list:
        os.chdir(file)
        ffmpeg_concat()


def check_c():
    """confirms user intends to compress their files"""
    if args.c:
        answer = input(
            "Are you sure you want to compress all concatenated files? (y/n) ")

        if answer == 'y':
            print("Confirmed\n")
        if answer == 'n':
            print("Exiting")
            exit()
        if answer != 'y':
            print("Invalid response. Please type y or n\n")
            check_c()

def check_d():
    """confirms user intends to delete leftover files"""
    if args.d:
        answer = input(
            "Are you sure you want to delete the leftover files? (y/n) ")

        if answer == 'y':
            print("Confirmed\n")
        if answer == 'n':
            print("Exiting")
            exit()
        if answer != 'y':
            print("Invalid response. Please type y or n\n")
            check_d()

def check_f():
    """confirms user intends to execute main on specified folder"""
    answer = input(f"Do you want to proceed in folder -- {folder}? (y/n) ")

    if answer == 'y':
        print("Confirmed\n")
    if answer == 'n':
        print("Exiting")
        exit()
    if answer != 'y':
        print("Invalid response. Please type y or n\n")
        check_f()

if args.f:
    os.chdir(args.f)

path = os.getcwd()

folder = os.path.basename(path)

print('Starting\n')


if args.d:
    check_d()

if args.c:
    check_c()

check_f()

main()

print("FINISHED")
