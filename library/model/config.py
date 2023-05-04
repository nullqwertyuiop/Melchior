from dataclasses import field

from kayaku import config


@config("config")
class MelchiorConfig:
    name: str = "Melchior"
    """ 机器人名称 """

    description: str = ""
    """ 机器人描述 """

    accounts: list[str] = field(default_factory=list)
    """
    机器人账号，使用分号分隔账号密码，无指定密码则表明使用二维码登录

    示例：
        80000000:password
    """

    owners: list[int] = field(default_factory=list)
    """ 机器人所有者 """

    debug: bool = False
    """ 是否开启调试模式 """

    proxy: str = ""
    """
    代理地址

    示例：
        http://localhost:1080
    """

    log_rotate: int = 7
    """ 日志文件保留天数 """
