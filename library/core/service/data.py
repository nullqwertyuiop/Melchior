import kayaku
from launart import Launart, Launchable
from loguru import logger


class MelchiorServiceData(Launchable):
    id = "melchior.service/data"

    @property
    def required(self):
        return {"melchior.service/essential"}

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, _: Launart):
        async with self.stage("preparing"):
            kayaku.bootstrap()
            kayaku.save_all()
            logger.success("[MelchiorService] 已保存配置文件")

        async with self.stage("cleanup"):
            kayaku.save_all()
            logger.success("[MelchiorService] 已保存配置文件")
