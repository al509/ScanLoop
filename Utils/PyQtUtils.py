import traceback
import types
from functools import wraps

from PyQt5.QtCore import pyqtSlot


def pyqtSlotWExceptions(*args):
    if len(args) == 0 or isinstance(args[0], types.FunctionType):
        args = []

    @pyqtSlot(*args)
    def slotdecorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args)
            except Exception as e:
                print(e)
                traceback.print_exc()
        return wrapper

    return slotdecorator


def reconnect(signal, new_handler=None, old_handler=None):
    while True:
        try:
            if old_handler is not None:
                signal.disconnect(old_handler)
            else:
                signal.disconnect()
        except TypeError:
            break

    if new_handler is not None:
        signal.connect(new_handler)
