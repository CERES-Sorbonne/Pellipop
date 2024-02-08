import subprocess
from pathlib import Path
from time import perf_counter as pc

pc1 = pc()

frame_mode = "i-frame"
# frame_mode = "const_freq"
freq = 0.25
audio = True

video_path = Path('test.mp4')
output_path = Path('output')

video_path = video_path.resolve()

if output_path.exists():
    for file in output_path.iterdir():
        file.unlink()
else:
    output_path.mkdir()
    print('output folder created')

map_parts = {
    "audio_part": "-acodec copy -vn $OUTPUT_FOLDER/$FILE_STEM.aac ",
    "i-frame_part": "-skip_frame nokey ",
    "const_freq_part": "-r $FREQ "
}

base = (
    "ffmpeg -hide_banner "
    "-loglevel panic "
    "-nostdin -y "
)

if frame_mode == "i-frame":
    base += map_parts["i-frame_part"]

base += "-i $VIDEO_PATH "

if frame_mode == "const_freq":
    base += map_parts["const_freq_part"]
elif frame_mode == "i-frame":
    base += "-fps_mode vfr -frame_pts true "

base += (
    "$OUTPUT_FOLDER/$FILE_STEM_%d.jpg "
)

if audio:
    base += map_parts["audio_part"]

command = (
    base
    .replace("$OUTPUT_FOLDER", str(output_path))
    .replace("$FILE_STEM", video_path.stem)
    .replace("$FREQ", str(freq))
    .replace("$VIDEO_PATH", str(video_path))
)

print(command)
subprocess.run(command, shell=True)

print(f"Time taken: {pc() - pc1:.2f} seconds")
print(f"Time in ms: {(pc() - pc1) * 1000:.2f} ms")
