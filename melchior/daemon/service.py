import asyncio
import os
import random
import socket
import subprocess
from asyncio import Task
from typing import Literal, Set

from creart import it
from graia.broadcast import Broadcast
from launart import ExportInterface, Launart, Launchable
from loguru import logger

from melchior.daemon._ctx import launch_args
from melchior.daemon.event import MelchiorDaemonConnected, MelchiorDaemonTimeout


class MelchiorDaemonService(Launchable):
    id = "melchior.daemon/service"
    server: socket.socket
    task: Task
    _token: str = None
    broadcast = it(Broadcast)

    @property
    def required(self) -> Set[str | type[ExportInterface]]:
        return set()

    @property
    def stages(self) -> Set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "blocking", "cleanup"}

    @property
    def token(self) -> str:
        if self._token:
            return self._token
        chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # noqa
        self._token = "".join(random.choices(chars, k=32))
        return self._token

    @property
    def loop(self):
        return asyncio.get_running_loop()

    @staticmethod
    def _popen(args: list[str]):
        subprocess.Popen(args, cwd="melchior", env=os.environ)

    def run(self):
        self._popen(["pdm", "run", "main.py"])

    async def daemon_accept(self, manager: Launart):
        while not manager.status.exiting:
            try:
                client, addr = await asyncio.wait_for(  # noqa
                    asyncio.get_running_loop().sock_accept(self.server), 5
                )
                self.broadcast.postEvent(MelchiorDaemonConnected())
            except TimeoutError:
                if not manager.status.exiting:
                    self.broadcast.postEvent(MelchiorDaemonTimeout())
                    await asyncio.sleep(5)

    # @broadcast.receiver(MelchiorDaemonConnected)
    async def daemon_connected(self):
        logger.success(f"[{self.id}] 已连接至 Melchior Socket")

    # @broadcast.receiver(MelchiorDaemonTimeout)
    async def daemon_timeout(self):
        logger.error(f"[{self.id}] 连接至 Melchior Socket 超时，将在 5 秒后重试...")

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            os.environ["MELCHIOR_DAEMON_TOKEN"] = self.token
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(("localhost", launch_args.get().port))
            self.server.setblocking(False)

        async with self.stage("blocking"):
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, self.server.listen, 5)
            loop.run_in_executor(None, self.run)
            logger.debug(f"[{self.id}] 正在尝试连接至 Melchior Socket...")
            self.task = loop.create_task(self.daemon_accept(manager))
            await manager.status.wait_for_cleaning()

        async with self.stage("cleanup"):
            logger.info(f"[{self.id}] 正在关闭 Melchior Socket 服务...")
            self.task.cancel()
