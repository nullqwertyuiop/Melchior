import socket
from abc import ABCMeta, abstractmethod

from launart import ExportInterface, Launart

from melchior.daemon._ctx import launch_manager


class Daemon(ExportInterface[socket.socket], metaclass=ABCMeta):
    @property
    def manager(self) -> Launart:
        return launch_manager.get()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def listen(self):
        pass

    @abstractmethod
    def send(self, *args, **kwargs):
        pass

    @abstractmethod
    def command(self, *args, **kwargs):
        pass
