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
    mv "$folder split files" "$FTDFOLDER"
    rm files.txt filesdelete.txt
    fi

    if [ "$DELETE" == 1 ]; then
    xargs -I{} rm -r "{}" < filesdelete.txt
    rm files.txt filesdelete.txt
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

    if [ "$COMPRESS" == 1 ]; then
          cd "$STARTDIR"
          compression
    fi

}

compression() {
  IFS=$'\n';
  compression_array=()
  while IFS='' read -r line; do compression_array+=("$line"); done < <(find "$STARTDIR" -type d -exec sh -c 'set -- "$1"/*/; [ ! -d "$1" ]' sh {} \; ! -empty -print)
  for i in "${compression_array[@]}"
  do
      if [[ $i != *"files to delete"* ]]; then
      cd "$( realpath "$i" )"
      folder="${PWD##*/}"
        if [ "$JSON" == 1 ]; then
        HandBrakeCLI -i "${folder}".MP4 --preset-import-file "$JSONFILEPATH" -o "${folder}cp".MP4
        else
        HandBrakeCLI -i "${folder}".MP4 -o "${folder}cp".MP4 --preset "Very Fast 1080p30" -r 60.0 -q 22.0 --encoder-level 5.1
        fi
      fi
      if [ "$DELETE" == 1 ]; then
      rm "${folder}".MP4
      mv "${folder}cp".MP4 "${folder}".MP4
      fi

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

while getopts "f:j:cdh" opt; do
case $opt in
  f) DIR=${OPTARG} ;;
  d) DELETE=1 ;;
  c) COMPRESS=1 ;;
  j) JSONFILEPATH=${OPTARG}
     JSON=1;;
  h) HELP=1
    echo "Options:
          -h       Print help
          -d       Delete leftover files
          -c       Compress concatenated files
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
main

echo FINISHED
