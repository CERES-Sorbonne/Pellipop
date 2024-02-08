import subprocess
from time import perf_counter as pc
from pathlib import Path

pc1 = pc()

frame_mode = "i-frame"
freq = 1
audio = True

video_path = Path('test.mp4')
output_path = Path('output')

if output_path.exists():
    for file in output_path.iterdir():
        file.unlink()
    else:
        print('output folder is empty')
else:
    output_path.mkdir()
    print('output folder created')

map_parts = {
    "audio_part": "-acodec copy -vn $OUTPUT_FOLDER/$FILE_STEM.aac ",
    "i-frame_part": "-skip_frame nokey ",
    "const_freq_part": "-r $FREQ "
}

base = (
    "ffmpeg -hide_banner -loglevel panic "
    "-nostdin -fps_mode vfr -frame_pts true "
)

if frame_mode == "i-frame":
    base += map_parts["i-frame_part"]
elif frame_mode == "const_freq":
    base += map_parts["const_freq_part"].replace("$FREQ", str(freq))
else:
    raise ValueError("frame_mode should be either i-frame or const_freq")

base += f"{output_path}/{video_path.stem}_d.jpg"

if audio:
    base += (
        map_parts["audio_part"]
        .replace("$OUTPUT_FOLDER", str(output_path))
        .replace("$FILE_STEM", video_path.stem)
    )

subprocess.run(base, shell=True)

print(f"Time taken: {pc() - pc1:.2f} seconds")
print(f"Time in ms: {(pc() - pc1) * 1000:.2f} ms")
