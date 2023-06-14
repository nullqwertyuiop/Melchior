import asyncio
import os
import random
import signal
import string
import subprocess
import time

from creart import it
from fastapi import FastAPI, HTTPException
from graia.amnesia.builtins.uvicorn import UvicornService
from graiax.fastapi import FastAPIService
from launart import Launart, Launchable
from loguru import logger
from psutil import Process
from starlette.middleware.cors import CORSMiddleware

from melchior.shared.util import setup_logger
from melchior.shared.var import MELCHIOR_ROOT

setup_logger(MELCHIOR_ROOT / "log" / "daemon", 7)

fastapi = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN: str | None = None


def setup_token():
    global TOKEN
    random.seed()
    TOKEN = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    logger.debug(f"Generated token: {TOKEN}")


@fastapi.get("/daemon/regen_token")
async def regen_token(token: str):
    if token != TOKEN:
        raise HTTPException(403, "Invalid token")
    logger.info("Daemon Command received: regen_token")


@fastapi.get("/daemon/shutdown")
async def daemon_shutdown(token: str):
    if token != TOKEN:
        raise HTTPException(403, "Invalid token")
    logger.info("Daemon Command received: shutdown")
    proc_manager.keep_alive = False
    proc_manager.shutdown()
    signal.raise_signal(signal.SIGINT)


@fastapi.get("/command/shutdown")
async def shutdown(token: str):
    if token != TOKEN:
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: shutdown")
    proc_manager.keep_alive = False
    proc_manager.shutdown()


@fastapi.get("/command/boot")
async def boot(token: str, keep_alive: bool = True):
    if token != TOKEN:
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: boot")
    proc_manager.keep_alive = keep_alive
    proc_manager.boot()


@fastapi.get("/command/reboot")
async def restart(token: str, keep_alive: bool = True):
    if token != TOKEN:
        raise HTTPException(403, "Invalid token")
    logger.info("Command received: restart")
    proc_manager.keep_alive = keep_alive
    proc_manager.restart()


class MelchiorAlreadyRunning(Exception):
    pass


class MelchiorNotRunning(Exception):
    pass


class ProcessManager:
    proc: Process | None
    keep_alive: bool
    attempts: list

    def __init__(self):
        self.proc = None
        self.keep_alive = True
        self.attempts = []

    @staticmethod
    def run(*args, **kwargs) -> subprocess.Popen:
        return subprocess.Popen(*args, **kwargs)

    def boot(self):
        if self.proc is not None and self.proc.is_running():
            raise MelchiorAlreadyRunning()
        popen = self.run(
            ["pdm", "run", "python", "-m", "melchior"],
            cwd="melchior",
            env=os.environ
            | {
                "MELCHIOR_DAEMON": "1",
                "MELCHIOR_DAEMON_TOKEN": TOKEN,
                "PDM_NO_SELF": "1",
            },
        )
        self.proc = Process(popen.pid)

    def shutdown(self):
        if self.proc is None or not self.proc.is_running():
            raise MelchiorNotRunning()
        self.proc.send_signal(signal.SIGINT)
        self.proc.wait()
        self.proc = None

    def restart(self):
        self.shutdown()
        self.boot()

    def keep(self):
        if self.proc is None or not self.proc.is_running():
            self.check_and_add_attempt()
            logger.warning("[MelchiorDaemon] Melchior 未运行，正在启动...")
            self.boot()

    def check_and_add_attempt(self):
        self.attempts.append(time.time())
        attempts_one_minute = [
            attempt for attempt in self.attempts if attempt > time.time() - 60
        ]
        if len(attempts_one_minute) >= 3:
            self.keep_alive = False
            logger.critical("[MelchiorDaemon] Melchior 短时间内重启次数过多，已停止自动重启")
            logger.critical("[MelchiorDaemon] 请检查 Melchior 是否出现问题")
        self.attempts = attempts_one_minute


proc_manager = ProcessManager()


class DaemonService(Launchable):
    id = "melchior.daemon/core"

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart):
        async with self.stage("preparing"):
            setup_token()
            logger.success("[MelchiorDaemon] 已初始化 Daemon")

        async with self.stage("blocking"):
            while proc_manager.keep_alive and not manager.status.exiting:
                proc_manager.keep()
                await asyncio.sleep(1)

        async with self.stage("cleanup"):
            pass

        logger.success("[MelchiorDaemon] 已退出 Daemon")


it(Launart).add_service(DaemonService())
it(Launart).add_service(UvicornService())
it(Launart).add_service(FastAPIService(fastapi))


def launch_daemon():
    it(Launart).launch_blocking()
