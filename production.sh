#!/bin/bash
set -e

ffmpeg_concat_ftd() {
    folder="${PWD##*/}"
    # for f in $(find . -iname "*.MP4" -type f -size -4020M); do echo "file '$f'" >> files.txt | echo "'$f'" >> filesdelete.txt; done
    find . -iname "*.MP4" -type f -size -4020M -print0 | while IFS= read -r -d '' f;
    do
    echo "file '$f'" >> filestmp.txt;
    sort filestmp.txt > files.txt;
    echo "'$f'" >> filesdeletetmp.txt;
    sort filesdeletetmp.txt > filesdelete.txt;
    done
    rm filestmp.txt filesdeletetmp.txt
    ffmpeg -f concat -safe 0 -i files.txt -c copy "${folder}".MP4
    mkdir "$folder split files"
    # cat filesdelete.txt | xargs -I {} mv {} "$folder split files"
    < filesdelete.txt xargs -I {} mv {} "$folder split files"
    rm files.txt filesdelete.txt

}

ffmpeg_concat_delete_files() {
	folder="${PWD##*/}"
	# for f in $(find . -iname "*.MP4" -type f -size -4020M); do echo "file '$f'" >> files.txt | echo "'$f'" >> filesdelete.txt; done
  find . -iname "*.MP4" -type f -size -4020M -print0 | while IFS= read -r -d '' f;
  do
  echo "file '$f'" >> filestmp.txt;
  sort filestmp.txt > files.txt;
  echo "'$f'" >> filesdeletetmp.txt;
  sort filesdeletetmp.txt > filesdelete.txt;
  done
  rm filestmp.txt filesdeletetmp.txt
	ffmpeg -f concat -safe 0 -i files.txt -c copy "${folder}".MP4
	xargs -I{} rm -r "{}" < filesdelete.txt
	rm files.txt filesdelete.txt
}

move_split_files() {
    cd "$root"
    mkdir "files to delete"
    # find . -type d -name "*split files" -exec mv '{}' "$( realpath 'files to delete')" \;
    array=()
    while IFS=  read -r -d $'\0'; do
    array+=("$REPLY")
    done < <(find . -type d -name "*split files" -print0)
    for i in "${array[@]}"
    do
    mv "$( realpath "$i" )" "$( realpath 'files to delete')"
    done

}

main_ftd() {
	  IFS=$'\n';
    root="$PWD";
    array=()
    while IFS='' read -r line; do array+=("$line"); done < <(find "$root" -type d -exec sh -c 'set -- "$1"/*/; [ ! -d "$1" ]' sh {} \; ! -empty -print)
    for i in "${array[@]}"
    do
        cd "$( realpath "$i" )"
        ffmpeg_concat_ftd
    done

    move_split_files

}

main_delete_files() {
	IFS=$'\n'
	root="$PWD";
  array=()
  while IFS='' read -r line; do array+=("$line"); done < <(find "$root" -type d -exec sh -c 'set -- "$1"/*/; [ ! -d "$1" ]' sh {} \; ! -empty -print)
	for i in "${array[@]}"
	do
		cd "$( realpath "$i" )"
		ffmpeg_concat_delete_files
	done
}

compression() {
  IFS=$'\n';
  root="$PWD";
  compression_array=()
  while IFS='' read -r line; do compression_array+=("$line"); done < <(find "$root" -type d -exec sh -c 'set -- "$1"/*/; [ ! -d "$1" ]' sh {} \; ! -empty -print)
  for i in "${compression_array[@]}"
  do
      if [[ $i != *"files to delete"* ]]; then
      cd "$( realpath "$i" )"
      folder="${PWD##*/}"
      HandBrakeCLI -i "${folder}".MP4 -o "${folder}cp".MP4 --preset "Very Fast 1080p30" -r 60.0 -q 22.0
      # HandBrakeCLI -i "${folder}".MP4 --preset-import-file [PATH to JSON] -o "${folder} (compressed)".MP4
      fi
  done
}

check() {
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

check_delete(){
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
}


while getopts ":f:cdh" opt; do
case $opt in
  f) DIR=${OPTARG} ;;
  d) DELETE=1 ;;
  c) COMPRESS=1 ;;
  h) HELP=1
    echo "Options:
          -h       Print help
          -d       Delete leftover files
          -c       Compress concatenated files
          -f       Run script in specified directory"

  ;;
  *) echo "Invalid arguments" ;;
esac
done

STARTDIR="$PWD";

if [ "$HELP" == 1 ]; then
  exit
fi

if [ -n "$DIR" ]; then
    cd "$DIR"
    STARTDIR=$DIR
fi

if [ "$DELETE" == 1 ]; then
    check_delete
    check
    main_delete_files
  else
    check
    main_ftd
fi

if [ "$COMPRESS" == 1 ]; then
      cd "$STARTDIR"
      compression
fi
