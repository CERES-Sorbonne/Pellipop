import sys
from subprocess import check_output, STDOUT


def get_version():
    if "pellipop" in sys.modules:
        del sys.modules["pellipop"]
    from pellipop.__about__ import __version__
    return __version__

def pip():
    return check_output(
        [sys.executable, "-m", "pip", "install", "-U", "pellipop"],
        stderr=STDOUT
    ).decode("utf-8", errors="ignore")

def main():
    console = ""

    try:
        print("Installing the latest version of Pellipop...")

        old = get_version()

        print(f"Current version: {old}")
        console += pip()

        new = get_version()

        if old == new:
            console += pip()

            new = get_version()

            if old == new:
                print("Pellipop is already up to date.")
                return

        print(f"Updated from version {old} to {new}.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print(console)
        raise e


if __name__ == "__main__":
    main()
