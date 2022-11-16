"""System module"""
import shutil
import argparse
import os
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
    current_path = os.getcwd()
    title = os.path.basename(current_path)
    open("files.txt", "x", encoding="utf8")

    filelist = []

    for filename in os.listdir():
        if filename.endswith(".MP4") and os.path.getsize(filename) < 4200000000:
            filelist.append(filename)
    filelist = natsorted(filelist)

    for file in filelist:
        fopen = open("files.txt", "a", encoding="utf8")
        fopen.write("file '" + file + "'\n")
        fopen.close()
    os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy '{title}.MP4'")
    os.remove("files.txt")

    if args.d is False:
        os.mkdir(f"{title} split files")
        split_files_path = os.path.abspath(f"{title} split files")
        for file in filelist:
            source = os.path.abspath(file)
            destination = split_files_path + '/' + file
            shutil.move(source, destination)
        files_to_delete_path = path + '/' + ("files to delete")
        split_destination = files_to_delete_path + \
                '/' + f"{title} split files"
        shutil.move(split_files_path, split_destination)

    if args.c:
        if args.j:
            os.system(
                f"HandBrakeCLI -i '{title}'.MP4 --preset-import-file {args.j} -o '{title}(cp)'.MP4 ")
        else:
            os.system(
                f"HandBrakeCLI -i '{title}'.MP4 -o '{title}(cp)'.MP4 --preset 'Very Fast 1080p30'\
                     -b 4000 --encoder-level auto --vfr -e vt_h264")

    if args.d:
        for file in filelist:
            os.remove(file)
        if args.c:
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
