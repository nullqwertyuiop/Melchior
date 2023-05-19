from creart import it
from graia.broadcast import Broadcast
from loguru import logger

from melchior.daemon.event import (
    MelchiorDaemonConnected,
    MelchiorDaemonDisconnected,
    MelchiorDaemonTimeout,
)

bc = it(Broadcast)


@bc.receiver(MelchiorDaemonConnected)
async def daemon_on_connect():
    logger.success("[Daemon] 已连接至 Melchior Socket")


@bc.receiver(MelchiorDaemonDisconnected)
async def daemon_on_disconnect():
    logger.warning("[Daemon] 与 Melchior Socket 的连接已断开")


@bc.receiver(MelchiorDaemonTimeout)
async def daemon_on_timeout():
    logger.error("[Daemon] 连接至 Melchior Socket 超时，将在 5 秒后重试...")
