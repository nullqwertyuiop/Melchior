from graia.broadcast import DispatcherInterface
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.entities.event import Dispatchable


class MelchiorDaemonEvent(Dispatchable):
    class Dispatcher(BaseDispatcher):
        @staticmethod
        async def catch(interface: DispatcherInterface):  # noqa
            pass


class MelchiorDaemonConnected(MelchiorDaemonEvent):
    pass


class MelchiorDaemonDisconnected(MelchiorDaemonEvent):
    pass


class MelchiorDaemonTimeout(MelchiorDaemonEvent):
    pass
