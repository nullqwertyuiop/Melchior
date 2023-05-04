import pkgutil
from pathlib import Path

import kayaku
from creart import it
from graia.broadcast import Broadcast
from graia.saya import Saya
from ichika.graia import IchikaComponent
from ichika.login import PathCredentialStore
from launart import Launart, Launchable
from loguru import logger

from library.core._config import init_kayaku


class MelchiorServiceEssential(Launchable):
    id = "melchior.service/essential"

    def __init__(self):
        init_kayaku()
        self._init_ichika()
        self._saya_require(Path("library") / "module")
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    @staticmethod
    def _saya_require(*paths: Path):
        saya = it(Saya)
        with saya.module_context():
            for path in paths:
                for module in pkgutil.iter_modules([str(path)]):
                    saya.require((path / module.name).as_posix().replace("/", "."))

    @staticmethod
    def _init_ichika():
        from library.core._ctx import launch_manager
        from library.model.config import MelchiorConfig

        mgr = launch_manager.get()
        ick = IchikaComponent(
            PathCredentialStore(Path("config") / "bots"), it(Broadcast)
        )

        mconfig: MelchiorConfig = kayaku.create(MelchiorConfig)
        for account in mconfig.accounts:
            parts = account.split(":", maxsplit=1)
            if len(parts) == 1:
                ick.add_qrcode_login(int(parts[0]))
            else:
                ick.add_password_login(int(parts[0]), parts[1])

        mgr.add_launchable(ick)

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[MelchiorService] 已保存配置文件")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[MelchiorService] 已保存配置文件")
