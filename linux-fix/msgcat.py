from ttkbootstrap.window import get_default_root


class MessageCatalog:
    @staticmethod

    def translate(src):
        return src

    @staticmethod
    def locale(newlocale=None):
        return newlocale

    @staticmethod
    def preferences():
        return []

    @staticmethod
    def load(dirname):
        return 0

    @staticmethod
    def set(locale, src, translated=None):
        pass

    @staticmethod
    def set_many(locale, *args):
        return 1

    @staticmethod
    def max(*src):
        return 1
