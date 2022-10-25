#!/bin/bash
set -e

ffmpeg_concat() {
    folder="${PWD##*/}"
    find . -iname "*.MP4" -type f -size -4020M -print0 | while IFS= read -r -d '' f;
    do
    echo "file '$f'" >> filestmp.txt;
    sort filestmp.txt > files.txt;
    echo "'$f'" >> filesdeletetmp.txt;
    sort filesdeletetmp.txt > filesdelete.txt;
    done
    rm filestmp.txt filesdeletetmp.txt
    ffmpeg -f concat -safe 0 -i files.txt -c copy "${folder}".MP4


    if [ "$DELETE" == 0 ]; then
    mkdir "$folder split files"
    < filesdelete.txt xargs -I {} mv {} "$folder split files"
      if [ "$SINGLE" == 0 ]; then
      mv "$folder split files" "$FTDFOLDER"
      fi
    rm files.txt filesdelete.txt
    fi

    if [ "$COMPRESS" == 1 ]; then
      if [ "$JSON" == 1 ]; then
      HandBrakeCLI -i "${folder}".MP4 --preset-import-file "$JSONFILEPATH" -o "${folder}cp".MP4
      else
      HandBrakeCLI -i "${folder}".MP4 -o "${folder}cp".MP4 --preset "Very Fast 1080p30" -b 4000 --no-two-pass --encoder-level auto --vfr -e vt_h264
      fi
      xattr -w com.apple.metadata:_kMDItemUserTags '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><array><string>handbrake</string></array></plist>' "${folder}cp".MP4
    fi

    if [ "$DELETE" == 1 ]; then
    xargs -I{} rm -r "{}" < filesdelete.txt
    rm files.txt filesdelete.txt
      if [ "$COMPRESS" == 1 ]; then
      rm "${folder}".MP4
      mv "${folder}cp".MP4 "${folder}".MP4
      fi
    fi
}

main() {
	  IFS=$'\n';
    array=()
    while IFS='' read -r line; do array+=("$line"); done < <(find "$STARTDIR" -type d -exec sh -c 'set -- "$1"/*/; [ ! -d "$1" ]' sh {} \; ! -empty -print)

    if [ "$DELETE" == 0 ]; then
    mkdir "files to delete"
    FTDFOLDER="$( realpath 'files to delete')"
    fi

    for i in "${array[@]}"
    do
        cd "$( realpath "$i" )"
        ffmpeg_concat
    done
}

check() {

  if [ "$DELETE" == 1 ]; then
    while true; do

  	read -r -p "Are you sure you want to delete the leftover files? (y/n) " yn

  	case $yn in
  		[yY] ) echo confirmed;
  			break;;
  		[nN] ) echo exiting...;
  			exit;;
  		* ) echo invalid response;;
  	esac

  	done
  fi

  if [ "$COMPRESS" == 1 ]; then
    while true; do

  	read -r -p "Are you sure you want to compress all concatenated files? (y/n) " yn

  	case $yn in
  		[yY] ) echo confirmed;
  			break;;
  		[nN] ) echo exiting...;
  			exit;;
  		* ) echo invalid response;;
  	esac

  	done
  fi


	while true; do

	read -r -p "Do you want to proceed in folder -- ${PWD##*/}? (y/n) " yn

	case $yn in
		[yY] ) echo confirmed;
			break;;
		[nN] ) echo exiting...;
			exit;;
		* ) echo invalid response;;
	esac

	done


	echo Starting FFMPEG
cat << "EOF"

:::::::::  :::::::::   ::::::::  :::       ::: ::::    :::
:+:    :+: :+:    :+: :+:    :+: :+:       :+: :+:+:   :+:
+:+    +:+ +:+    +:+ +:+    +:+ +:+       +:+ :+:+:+  +:+
+#++:++#+  +#++:++#:  +#+    +:+ +#+  +:+  +#+ +#+ +:+ +#+
+#+    +#+ +#+    +#+ +#+    +#+ +#+ +#+#+ +#+ +#+  +#+#+#
#+#    #+# #+#    #+# #+#    #+#  #+#+# #+#+#  #+#   #+#+#
#########  ###    ###  ########    ###   ###   ###    ####
::::    ::::  :::::::::: ::::    ::: :::  ::::::::
+:+:+: :+:+:+ :+:        :+:+:   :+: :+  :+:    :+:
+:+ +:+:+ +:+ +:+        :+:+:+  +:+     +:+
+#+  +:+  +#+ +#++:++#   +#+ +:+ +#+     +#++:++#++
+#+       +#+ +#+        +#+  +#+#+#            +#+
#+#       #+# #+#        #+#   #+#+#     #+#    #+#
###       ### ########## ###    ####      ########
::::::::::: :::::::::: ::::    ::: ::::    ::: :::::::::::  ::::::::
    :+:     :+:        :+:+:   :+: :+:+:   :+:     :+:     :+:    :+:
    +:+     +:+        :+:+:+  +:+ :+:+:+  +:+     +:+     +:+
    +#+     +#++:++#   +#+ +:+ +#+ +#+ +:+ +#+     +#+     +#++:++#++
    +#+     +#+        +#+  +#+#+# +#+  +#+#+#     +#+            +#+
    #+#     #+#        #+#   #+#+# #+#   #+#+#     #+#     #+#    #+#
    ###     ########## ###    #### ###    #### ###########  ########


EOF

	sleep 3
}

HELP=0;
DELETE=0;
COMPRESS=0;
JSON=0;
SINGLE=0;

while getopts "f:j:cdhs" opt; do
case $opt in
  f) DIR=${OPTARG} ;;
  d) DELETE=1 ;;
  c) COMPRESS=1 ;;
  s) SINGLE=1 ;;
  j) JSONFILEPATH=${OPTARG}
     JSON=1;;
  h) HELP=1
    echo "Options:
          -h       Print help
          -d       Delete leftover files
          -c       Compress concatenated files
          -s       Run script on only given folder and not subdirectories
          -f       Run script in specified directory
          -j       Run compression with preset from JSON file"

  ;;
  *) echo "Invalid arguments" ;;
esac
done

STARTDIR="$PWD";
if [ -n "$DIR" ]; then
    cd "$DIR"
    STARTDIR=$DIR
fi

if [ "$HELP" == 1 ]; then
  exit
fi

check

if [ "$SINGLE" == 1 ]; then
  ffmpeg_concat
  exit
fi

main
echo FINISHED
