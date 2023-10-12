from pathlib import Path
import subprocess
import sys

from tqdm.auto import tqdm


def toAudio(videoPath: str | Path, audioPath: str | Path, extension=".wav"):
    if isinstance(videoPath, str):
        videoPath = Path(videoPath)
    if isinstance(audioPath, str):
        audioPath = Path(audioPath)

    if not videoPath.exists():
        print("File does not exist")
        sys.exit(1)

    if videoPath.suffix != ".mp4":
        print("File must be a mp4 file")
        sys.exit(1)

    if audioPath.exists():
        print("The audio file already exists ({audioPath.name})")

    subprocess.run(
        ["ffmpeg", "-i", videoPath.as_posix(), audioPath.as_posix()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return audioPath.as_posix()


def toAudioFolder(videoPath: str | Path, audioPath: str | Path, extension=".wav"):
    if isinstance(videoPath, str):
        videoPath = Path(videoPath)

    if isinstance(audioPath, str):
        audioPath = Path(audioPath)

    if not videoPath.exists():
        print("The folder does not exist")
        sys.exit(1)

    if not audioPath.exists():
        audioPath.mkdir(parents=True)

    videos = tqdm(list(videoPath.glob("*.mp4")))
    for video in videos:
        audio = audioPath / video.with_suffix(extension).name

        toAudio(video, audio, extension=extension)


if __name__ == "__main__":
    toAudioFolder("../../videos-collecte1", "../../audio-collecte1")
