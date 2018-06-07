import lab_remote as gr


class LabRemoteErrorMeta(type):
    ID_MAX = 0
    ID_LIST = []

    def __new__(cls, name, bases, dictionary):
        dictionary['ID'] = cls.ID_MAX
        cls.ID_MAX += 1
        try:
            bases = (*bases, LabRemoteError)
        except NameError:
            assert name == 'LabRemoteError'
        newcls = super(LabRemoteErrorMeta, cls).__new__(cls, name, bases, dictionary)
        cls.ID_LIST.append(newcls)
        return newcls

    @classmethod
    def make(cls, id, *args, **kwargs):
        return cls.ID_LIST[id](*args, **kwargs)


class LabRemoteError(RuntimeError, metaclass=LabRemoteErrorMeta):
    pass


class TimestepTimeoutError(TimeoutError, metaclass=LabRemoteErrorMeta):
    pass


class WallClockTimeoutError(TimeoutError, metaclass=LabRemoteErrorMeta):
    pass


class ClientDisconnectError(gr.Bridge.Closed, metaclass=LabRemoteErrorMeta):
    pass


class ServerDisconnectError(gr.Bridge.Closed, metaclass=LabRemoteErrorMeta):
    pass


class ResetError(metaclass=LabRemoteErrorMeta):
    pass


def make(id, *args, **kwargs):
    return LabRemoteErrorMeta.make(id, *args, **kwargs)
