from contextvars import ContextVar

from launart import Launart

launch_manager: ContextVar[Launart] = ContextVar("melchior.launch_manager")
launch_manager.set(Launart())
