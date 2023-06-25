from multiprocessing import Process
from threading import Thread


def keepAliveD(daemon: bool = True):
    """Supports daemon threads"""

    def outer(fc):
        def inner(*args):
            t = Thread(name=fc.__name__, target=fc, args=args, daemon=daemon)
            t.start()

        return inner

    return outer


def keepAlive(fc):
    def inner(*args):
        t = Thread(name=fc.__name__, target=fc, args=args, daemon=False)
        t.start()

    return inner


def undeadD(daemon=True):
    """"Supports daemon process"""

    def outer(fc):
        def inner(*args):
            p = Process(name=fc.__name__, target=fc, args=args, daemon=daemon)
            p.start()

        return inner

    return outer


def undead(fc):
    def inner(*args):
        p = Process(name=fc.__name__, target=fc, args=args, daemon=False)
        p.start()

    return inner
