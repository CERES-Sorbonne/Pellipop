from pathlib import Path


# noinspection PyRedeclaration
class Path(type(Path()), Path):
    @classmethod
    def win_repair(cls, path):
        if any((path.exists(), path.is_file(), path.is_dir())):
            return path

        path = Path('//?/c:/') / path

        if path.exists():
            return path

        if len(str(path)) > 260:
            raise ValueError(
                f"{path} is too long, please change the path (rename the folders, etc.)"
                "to make it shorter than 260 characters"
                "\nOr ensure that you are not using forbidden characters in the path"
                "(like /, :, spaces, etc.)"
                "\nAnd ensure that you are not using reserved names in the path"
                "\nIf everything is correct, please also check if you have the right to access it"
            )

        raise ValueError(f"{path} does not exist")


if __name__ == "__main__":
    cwd = "/home/marceau/PycharmProjects/Pellipop/pellipop"
    classe = "<class '__main__.Path'>"
    p = Path.cwd()
    assert str(p) == cwd
    assert str(type(p)) == classe
    p = Path.win_repair(p)
    assert str(p) == cwd or str(p) == "//?/" + cwd
    assert str(type(p)) == classe
