import ffmpeg
import subprocess
import os
from natsort import natsorted
import shutil

print('start')



def ffmpeg_concat():
    open("files.txt", "x")

    path = os.getcwd()
    list = os.listdir(path)
    name = os.path.basename(path)

    filestmp = []
    for file in list:
        if file.endswith(".MP4"):
            filestmp.append(file)
    filestmp = natsorted(filestmp)

    for file in filestmp:
        f = open("files.txt", "a")
        f.write("file '" + file + "'\n")
        f.close()
    title = name + ".MP4"
    # os.system("ffmpeg -f concat -safe 0 -i " + 'files.txt' + " -c copy title.MP4")
    os.remove("files.txt")

    ftd = name + " files to delete"
    os.mkdir("files to delete")


    for file in filestmp:
        source = path + '/' + file
        destination = path + '/' + ftd + '/' + file
        shutil.move(source, destination)


    # for file in filestmp:
    #     os.remove(file)

ffmpeg_concat()
