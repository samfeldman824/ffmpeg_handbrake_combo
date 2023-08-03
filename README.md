# Video Concatenation and Compression Utility

This utility script provides a convenient way to concatenate and compress multiple video files in a given folder. It supports automatic concatenation, compression, and deletion of the original video files.

## Prerequisites

Before running the script, ensure you have the required dependencies installed:

- [FFmpeg](https://www.ffmpeg.org/) - Used for video concatenation.
- [HandBrakeCLI](https://handbrake.fr/downloads2.php) - Used for video compression.

## Usage

You can use the script with various command-line arguments to control its behavior. Here are the available options:

```bash
usage: video_concat.py [-h] [-d] [-c] [-f FILEPATH] [-j JSON]

optional arguments:
  -h, --help          show this help message and exit
  -d, -delete         Delete leftover files after concatenation
  -c, -compress       Compress concatenated files using HandBrake
  -f FILEPATH, -filepath FILEPATH
                      Run the script in the specified directory
  -j JSON, -json JSON
                      Run compression with presets from the given JSON file
```

## Testing

To run tests
```
pytest
```