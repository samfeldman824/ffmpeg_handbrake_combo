import subprocess
import os
from natsort import natsorted
import shutil
import argparse

print('start')

parser = argparse.ArgumentParser()
parser.add_argument('-d', '-delete', help='Delete leftover files', action='store_true')
parser.add_argument('-c', '-compress', help='Compress concatenated files', action='store_true')
parser.add_argument('-s', '-single', help='Run script on only given folder and not subdirectories', action='store_true')
parser.add_argument('-f', '-filepath', help='Run script in specified directory')
parser.add_argument('-j', '-json', help='Run compression with preset from given JSON file')
args = parser.parse_args()

if args.f:
    print(args.f)

if args.j:
    print(args.j)

# os.chdir('/Users/samfeldman/Desktop/Tennis/testfolder copy 2')

path = os.getcwd()
list = os.listdir(path)



def ffmpeg_concat():
    open("files.txt", "x")
    current_path = os.getcwd()
    name = os.path.basename(current_path)

    findCMD = 'find . -iname "*.MP4" -type f -size -4020M -print0'
    out = subprocess.Popen(findCMD,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdout, stderr) = out.communicate()
    filelist = natsorted(stdout.decode().split('\x00')[:-1])

    # for f in list:
    #     if file.endswith(".MP4") and os.path.getsize(f) < 4200000000:



    for file in filelist:
        ft = open("files.txt", "a")
        ft.write("file '" + file + "'\n")
        ft.close()
    title = '_'.join(name.split())
    os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy {title}.MP4")
    os.remove("files.txt")




    os.mkdir(f"{title} split files")
    split_files_path = os.path.abspath(f"{title} split files")
    for file in filelist:
        source = os.path.abspath(file)
        destination = split_files_path + '/' + file
        shutil.move(source, destination)
    files_to_delete_path = path + '/' + ("files to delete")
    split_destination = files_to_delete_path + '/' + f"{title} split files" + '/' + file    
    shutil.move(split_files_path, split_destination)

    # for file in filelist:
    #     os.remove(file)

    # os.system(f"HandBrakeCLI -i {title}.MP4 -o {title}'(cp)'.MP4 --preset 'Very Fast 1080p30' -b 4000 --encoder-level auto --vfr -e vt_h264")

# ffmpeg_concat()

def dir_no_subs(directory_path, list):
    for file in os.scandir(directory_path):
        if file.is_dir():
            os.chdir(file.path)
            nsub = True
            for f in os.scandir(file.path):
                if f.is_dir():
                    nsub = False
                    break
                continue
            if nsub == True:
                list.append(file.path)           
            dir_no_subs(file, list)
    
                

def main():
    directory_list = []
    dir_no_subs(path, directory_list)
    os.mkdir(path + '/' + "files to delete")
    
    
    for i in directory_list:
        os.chdir(i)
        ffmpeg_concat()

main()




