from pydantic import BaseModel


class ModulePredefinedConfig(BaseModel):
    """模块预定义配置"""

    enable_by_default: bool = False
    """ 默认启用 """

    allow_disable: bool = True
    """ 允许禁用 """

    allow_unload: bool = True
    """ 允许卸载 """

    allow_delete: bool = True
    """ 允许删除 """


class ModuleRequirement(BaseModel):
    """模块依赖"""

    pack: str
    """ 模块 ID，使用 melchior 代表 Melchior 本体 """

    version: str = "0.0.0"
    """ 模块版本，0.0.0 表示任意版本 """


class MelchiorModule(BaseModel):
    """Melchior 模块基类"""

    name: str
    """ 模块名称 """

    version: str = "0.0.0"
    """ 模块版本 """

    pack: str
    """ 模块包名 """

    authors: list[str] = []
    """ 模块作者 """

    require: list[ModuleRequirement] = []
    """ 模块依赖 """

    description: str = ""
    """ 模块描述 """

    category: list[str] = []
    """ 模块分类 """

    config: ModulePredefinedConfig = ModulePredefinedConfig()
    """ 模块预定义配置 """

    @property
    def data_path(self):
        # TODO Implement data path
        raise NotImplementedError

    @property
    def config_path(self):
        # TODO Implement config path
        raise NotImplementedError
