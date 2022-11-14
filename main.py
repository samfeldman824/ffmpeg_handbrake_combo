import subprocess
import os
from natsort import natsorted
import shutil

print('start')



def ffmpeg_concat():
    open("files.txt", "x")

    path = os.getcwd()
    name = os.path.basename(path)

    findCMD = 'find . -iname "*.MP4" -type f -size -4020M -print0'
    out = subprocess.Popen(findCMD,shell=True,stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    (stdout, stderr) = out.communicate()
    filelist = natsorted(stdout.decode().split('\x00')[:-1])

    for file in filelist:
        f = open("files.txt", "a")
        f.write("file '" + file + "'\n")
        f.close()
    title = '_'.join(name.split())
    os.system(f"ffmpeg -f concat -safe 0 -i files.txt -c copy {title}.MP4")
    # os.remove("files.txt")




    # os.mkdir("files to delete")
    # ftdpath = os.path.abspath('files to delete')

    # for file in filestmp:
    #     source = os.path.abspath(file)
    #     destination = ftdpath + '/' + file
    #     shutil.move(source, destination)

    # for file in filestmp:
    #     os.remove(file)

    # os.system(f"HandBrakeCLI -i {title}.MP4 -o {title}'(cp)'.MP4 --preset 'Very Fast 1080p30' -b 4000 --encoder-level auto --vfr -e vt_h264")

ffmpeg_concat()


