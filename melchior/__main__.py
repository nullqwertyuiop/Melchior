import os
from pathlib import Path

from loguru import logger

from .shared.util import setup_logger
from .shared.var import MELCHIOR_ROOT


def _ensure_env():
    pyproject = Path("pyproject.toml")
    pdm_lock = Path("pdm.lock")
    if not pyproject.exists():
        os.system("pdm init --non-interactive")
    if not pdm_lock.exists():
        os.system("pdm install")


def _ensure_daemon():
    env = os.environ
    if env.get("MELCHIOR_DAEMON") != "1":
        logger.critical("Melchior 非守护进程启动，可能会导致 Melchior 无法正常运行")
        return
    if env.get("MELCHIOR_DAEMON_TOKEN") is None:
        logger.critical("Melchior 守护进程启动，但未提供合法的 TOKEN")
        return
    logger.debug("Melchior 由守护进程启动，token 为 {token}", token=env["MELCHIOR_DAEMON_TOKEN"])


if __name__ == "__main__":
    setup_logger(MELCHIOR_ROOT / "log", 7)
    _ensure_daemon()
    _ensure_env()

    from .library.core import launch

    launch()
