#!/bin/bash
set -e

ffmpeg_concat_ftd() {
    folder="${PWD##*/}"
    # for f in $(find . -iname "*.MP4" -type f -size -4020M); do echo "file '$f'" >> files.txt | echo "'$f'" >> filesdelete.txt; done
    find . -iname "*.MP4" -type f -size -4020M -print0 | while IFS= read -r -d '' f;
    do
    echo "file '$f'" >> files.txt;
    echo "'$f'" >> filesdelete.txt;
    done
    ffmpeg -f concat -safe 0 -i files.txt -c copy "${folder}".MP4
    mkdir "$folder split files"
    # cat filesdelete.txt | xargs -I {} mv {} "$folder split files"
    < filesdelete.txt xargs -I {} mv {} "$folder split files"
    rm files.txt
    rm filesdelete.txt

}

ffmpeg_concat_delete_files() {
	folder="${PWD##*/}"
	# for f in $(find . -iname "*.MP4" -type f -size -4020M); do echo "file '$f'" >> files.txt | echo "'$f'" >> filesdelete.txt; done
  find . -iname "*.MP4" -type f -size -4020M -print0 | while IFS= read -r -d '' f;
  do
  echo "file '$f'" >> files.txt;
  echo "'$f'" >> filesdelete.txt;
  done
	ffmpeg -f concat -safe 0 -i files.txt -c copy "${folder}".MP4
	xargs -I{} rm -r "{}" < filesdelete.txt
	rm files.txt
	rm filesdelete.txt
}

move_split_files() {
    cd "$root"
    mkdir "files to delete"
    find . -type d -name "*split files" -exec mv '{}' "$( realpath 'files to delete')" \;
}

main_ftd() {
	IFS=$'\n';
    root="$PWD";

    array=()
    while IFS='' read -r line; do array+=("$line"); done < <(find . -type d -execdir sh -c 'test -z "$(find "{}" -mindepth 1 -type d)" && echo $PWD/{}' ';')

    # array=( $(find . -type d -execdir sh -c 'test -z "$(find "{}" -mindepth 1 -type d)" && echo $PWD/{}' ';') )
    # array=()
    # find . -type d -execdir sh -c 'test -z "$(find "{}" -mindepth 1 -type d)" && echo $PWD/{}' ';' | while IFS="" read -r line; do array+=("$line"); done


    for i in "${array[@]}"
    do
        cd "$( realpath "$i" )"
        ffmpeg_concat_ftd
        # HandBrakeCLI -i "${folder}".MP4 -o "${folder}cp".MP4 --preset "Very Fast 1080p30"

    done

    move_split_files

}

main_delete_files() {

	IFS=$'\n'
	root="$PWD";

  array=()
  while IFS='' read -r line; do array+=("$line"); done < <(find . -type d -execdir sh -c 'test -z "$(find "{}" -mindepth 1 -type d)" && echo $PWD/{}' ';')

	for i in "${array[@]}"
	do
		cd "$( realpath "$i" )"
		ffmpeg_concat_delete_files

	done
}

check() {
	while true; do

	read -p "Do you want to proceed in folder -- ${PWD##*/}? (y/n) " yn

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

	read -p "Are you sure you want to delete the leftover files? (y/n) " yn

	case $yn in
		[yY] ) echo confirmed;
			break;;
		[nN] ) echo exiting...;
			exit;;
		* ) echo invalid response;;
	esac

	done
}

if [[ -z $1 ]];
then
	check
    main_ftd
elif [[ -n $1 && -z $2 ]];
then
	if [[ $1 == delete ]];
	then
		check_delete
		check
		main_delete_files
	elif [[ ! -d $1 ]];
	then
		echo -"$1"- is not a valid directory;
		exit
	else
		cd "$1"
		check
		main_ftd
	fi
elif [[ -n $1 && -n $2 && -z $3 ]];
then
	if [[ ! -d $1 ]];
	then
		echo -"$1"- is not a valid directory;
		exit
	elif [[ $2 != delete ]];
	then
		echo argument -"$2"- not valid
	else
		cd "$1"
		check_delete
		check
		main_delete_files
	fi

else
echo Too many arguments entered
fi
