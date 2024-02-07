#!/usr/bin/bash
# Usage: ./i-frame_test.sh <input_file> <output_dir> <file_name>
INPUT_FILE=$1
OUTPUT_DIR=$2
FILE_NAME=$3
NO_AUDIO=$4
EVERY_FRAME=$5

if [ -z "$INPUT_FILE" ]; then
    echo "Input file not provided"
    exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
    echo "Output directory not provided"
    exit 1
fi

if [ -z "$FILE_NAME" ]; then
    FILE_NAME="${INPUT_FILE##*/}"
    FILE_NAME="${FILE_NAME%.*}"
fi

if [ "$NO_AUDIO" = "true" ]; then
    audio_part=""
else
    audio_part="-acodec copy -vn $OUTPUT_DIR/$FILE_NAME.aac"
fi

if [ "$EVERY_FRAME" = "true" ]; then
    frame_part=""
else
    frame_part="-skip_frame nokey"
fi

if [ -d "$OUTPUT_DIR" ]; then
    rm -fr $OUTPUT_DIR
fi

mkdir $OUTPUT_DIR
ts=$(date +%s%N)
ffmpeg -hide_banner -loglevel panic -nostdin -y $frame_part -i $INPUT_FILE -fps_mode vfr -frame_pts true $OUTPUT_DIR/$FILE_NAME%d.png $audio_part
echo "Fait en : $((($(date +%s%N)-ts)/1000000))ms"
