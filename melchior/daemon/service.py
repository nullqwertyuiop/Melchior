import asyncio
import os
import signal
import socket
import subprocess
from asyncio import Task
from asyncio.subprocess import Process  # noqa
from typing import Literal, Set, Type

from creart import it
from graia.broadcast import Broadcast
from launart import ExportInterface, Launart, Service
from launart.service import TInterface
from loguru import logger

from melchior.daemon._ctx import launch_args
from melchior.daemon.event import (
    MelchiorDaemonConnected,
    MelchiorDaemonDisconnected,
    MelchiorDaemonTimeout,
)
from melchior.daemon.exception import MelchiorAlreadyLaunched
from melchior.daemon.interface import Daemon
from melchior.daemon.util import get_token


class MelchiorDaemon(Daemon):
    conn: socket.socket
    tasks: list[Task]
    client: socket.socket | None
    address: ...
    melchior_proc: Process | None
    auto_restart: bool

    def __init__(self):
        self.init_socket()
        self.tasks = []
        self.client = None
        self.address = None
        self.launched = False
        self.melchior_proc = None
        self.auto_restart = launch_args.get().auto_restart

    @property
    def token(self) -> str:
        return get_token()

    def cancel_all(self):
        for task in self.tasks:
            task.cancel()

    def _callback_remove_task(self, task: Task):
        if task in self.tasks:
            self.tasks.remove(task)
            logger.debug(f"[MelchiorDaemon] 已移除任务 {task.get_name()}")

    def init_socket(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind(("localhost", port := launch_args.get().port))
        self.conn.setblocking(False)
        logger.info(f"[MelchiorDaemon] 将在 {port} 端口监听 Melchior Socket")

    def listen(self):
        self.conn.listen(5)

    async def _async_connect(self):
        while not self.manager.status.exiting:
            try:
                loop = asyncio.get_running_loop()
                self.client, self.address = await loop.sock_accept(self.conn)
                it(Broadcast).postEvent(MelchiorDaemonConnected())
                return
            except Exception as e:
                logger.exception(e)

    def connect(self):
        logger.info("[MelchiorDaemon] 正在尝试连接至 Melchior Socket...")
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._async_connect())
        self.tasks.append(task)
        task.add_done_callback(self._callback_remove_task)

    def disconnect(self):
        logger.info("[MelchiorDaemon] 正在断开 Melchior Socket 连接...")
        if self.client is not None:
            self.client.close()
            it(Broadcast).postEvent(MelchiorDaemonDisconnected())
        self.conn.close()

    async def _async_receive(self):
        while not self.manager.status.exiting:
            try:
                loop = asyncio.get_running_loop()
                data = await loop.sock_recvfrom(self.client, 1024)
                logger.info(f"[MelchiorDaemon] 收到数据: {data}")
            except Exception as e:
                logger.exception(e)

    def receive(self):
        pass

    def send(self, *args, **kwargs):
        raise NotImplementedError("MelchiorDaemon.send is not implemented")

    @staticmethod
    async def _async_exec(args: list[str]) -> Process:
        return await asyncio.create_subprocess_exec(
            *args, cwd="melchior", env=os.environ
        )

    def launch(self):
        if self.melchior_proc is not None:
            raise MelchiorAlreadyLaunched()
        loop = asyncio.get_running_loop()

        def _exit_callback(_task: Task):
            if not self.manager.status.exiting:
                signal.raise_signal(signal.SIGINT)
                self._callback_remove_task(_task)

        def _relaunch_callback(_task: Task):
            if exc := _task.exception():
                logger.exception(exc)
            logger.info(f"[MelchiorDaemon] Melchior@{_task.get_name()} 似乎已关闭，正在重新启动")
            self.melchior_proc = None
            self._callback_remove_task(_task)
            loop.call_soon(self.launch)

        def _exec_callback(_task: Task):
            self.melchior_proc = _task.result()
            if exc := _task.exception():
                logger.exception(exc)
            __task = loop.create_task(self.melchior_proc.wait())
            if self.auto_restart:
                __task.add_done_callback(_relaunch_callback)
            else:
                __task.add_done_callback(_exit_callback)
            self._callback_remove_task(_task)

        task = loop.create_task(self._async_exec(["pdm", "run", "main.py"]))
        task.add_done_callback(_exec_callback)
        self.tasks.append(task)

    def command(self, *args, **kwargs):
        pass


class MelchiorDaemonService(Service):
    id = "melchior.daemon/service"
    supported_interface_types = {MelchiorDaemon}

    @property
    def required(self) -> Set[str | type[ExportInterface]]:
        return set()

    def get_interface(self, interface_type: Type[TInterface]) -> TInterface:
        return MelchiorDaemon()

    @property
    def stages(self) -> Set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "blocking", "cleanup"}

    @property
    def loop(self):
        return asyncio.get_running_loop()

    @staticmethod
    def _popen(args: list[str]):
        proc = subprocess.Popen(args, cwd="melchior", env=os.environ)
        proc.wait()

    def run(self):
        self._popen(["pdm", "run", "main.py"])

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            connector = manager.get_interface(MelchiorDaemon)

        async with self.stage("blocking"):
            connector.listen()
            connector.connect()
            connector.launch()
            await manager.status.wait_for_cleaning()

        async with self.stage("cleanup"):
            connector.disconnect()
            logger.info(f"[{self.id}] 正在关闭 Melchior Socket 服务...")
            connector.cancel_all()


bc = it(Broadcast)


@bc.receiver(MelchiorDaemonConnected)
async def daemon_on_connect():
    logger.success("[MelchiorDaemon] 已连接至 Melchior Socket")


@bc.receiver(MelchiorDaemonDisconnected)
async def daemon_on_disconnect():
    logger.warning("[MelchiorDaemon] 与 Melchior Socket 的连接已断开")


@bc.receiver(MelchiorDaemonTimeout)
async def daemon_on_timeout():
    logger.error("[MelchiorDaemon] 连接至 Melchior Socket 超时，将在 5 秒后重试...")
