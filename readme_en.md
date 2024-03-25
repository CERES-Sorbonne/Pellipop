# Pellipop
[![PyPI - Version](https://img.shields.io/pypi/v/pellipop.svg)](https://pypi.org/project/pellipop)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pellipop.svg)](https://pypi.org/project/pellipop)

## Table of Contents
1. [Description](#description)
2. [Installation](#installation)
    1. [PyPi](#pypi)
    2. [Executable](#executable)
    3. [Development](#development)
3. [Usage](#usage)
    1. [Graphical Interface](#graphical-interface)
    2. [Command Line](#command-line)
4. [License](#license)

## Description
Pellipop is a tool for cutting videos into still images, with text and audio extraction.
It allows you to cut videos into still images, extracting the text and audio from the videos.
It also allows you to obtain a CSV file containing the information of the extracted images and facilitating the export
of data into image corpus processing software,
like [Panoptic](https://github.col/CERES-Sorbonne/panoptic).

It accepts the following input formats:

- `".mov"`
- `".avi"`
- `".mp4"`
- `".flv"`
- `".wmv"`
- `".webm"`
- `".mkv"`
- `".svf"`

## Installation
### PyPi
Pellipop is available on PyPi, you can install it with pip using the following command:
```bash
pip install pellipop
```
You can then check that the installation went well by running the command `pellipop --version`
Once installed, you can launch the graphical interface with the command `pellipop`.

### Executable
Executables are available for Windows, MacOS and Linux on the [releases](https://github.com/CERES-Sorbonne/Pellipop/releases/latest) page.
You can download the executable corresponding to your operating system, and launch the graphical interface by double-clicking on it.

### Development
To install Pellipop in development mode, you can clone the git repository and install the dependencies with pip:
```bash
git clone https://github.com/CERES-Sorbonne/Pellipop.git.
cd Pellipop
pip install -e .
```


## Usage
### Graphical Interface
It is launched with `pellipop`, without any argument, to open the graphical interface.

Alternatively, you can download the executable corresponding to your operating system on the
[releases](https://github.com/CERES-Sorbonne/Pellipop/releases/latest) page.

### Command Line
The CLI is launched with `pellipop` in a terminal, by default the videos are searched for in the folder where the command
is launched, and the created images are also stored in the same place. However, the parameters can be changed:

- `--input` : to specify the input folder to search for videos (recursive)
- `--output` : to specify where to store the output images

- `--interval` : time interval (in seconds) at which to take screenshots
- `--i-frame-mode` : allows you to remove duplicate images for the same film using the video's keyframes

- `--keep-audio` : allows you to keep the audio files extracted from the videos
- `--whisper-config` : to specify the path to the Whisper API configuration file, instead of the default path (`~\.whisperrc`)

- `--frames-only` : allows you not to extract the text from the videos
- `--reduce` : allows you to reduce the name of the output files to a certain number of characters from the original name
- `--offset` : allows you to shift the start of the name of the output files by n characters
- `--parents-in-name` : allows you to add the name of the parent folders in the name of the output files, separated by _

- `-g` or `--gui` : allows you to use the graphical interface
- `-v` or `--version` : displays the version of the current Pellipop installation

> Note: The cutting time of each video depends on the quality of the video being cut, the cutting frequency, the duration of the video and the power of the computer.

#### Example of usage:
```bash
pellipop --input C:\Users\User\Videos\Captures --output D:\Users\Desktop\Output --i-frame-mode
```

## License
This project is licensed under the MPL-2.0 License - see the [LICENSE](https://github.com/CERES-Sorbonne/Pellipop/blob/master/LICENSE.txt) file for details.

