from abc import ABC

from creart import AbstractCreator, CreateTargetInfo, add_creator, exists_module
from launart import Launart


class LaunchManagerCreator(AbstractCreator, ABC):
    targets = (CreateTargetInfo("launart.manager", "Launart"),)

    @staticmethod
    def available() -> bool:
        return exists_module("launart.manager")

    @staticmethod
    def create(create_type: type[Launart]) -> Launart:
        return Launart()


add_creator(LaunchManagerCreator)
