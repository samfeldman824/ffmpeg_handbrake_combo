# ffmpeg_handbrake_combo

Dependencies: FFMPEG, HandBrakeCLI, GNU Coreutils


All in one script that concatenates video files using FFMPEG and compresses the concatenated video file using HandBrake. Currently configured to only handle .MP4 files. Any files larger than 4 GB will not be concatenated with the other files in a folder. Files in each folder will be sorted alphabetically by title before being concatenated.
