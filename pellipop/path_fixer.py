from pathlib import Path as Path_


def for_all_methods(exclude, decorator):
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)) and attr not in exclude:
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def win_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            args[0] = Path('//?/c:/') / args[0]
            return func(*args, **kwargs)

    return wrapper


@for_all_methods(exclude={"__init__"}, decorator=win_decorator)
class Path(type(Path_()), Path_):
    # _flavour = _PosixFlavour() if os.name == 'posix' else _WindowsFlavour()

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
