from argparse import Namespace
from contextvars import ContextVar

from launart import Launart

from melchior.daemon.parse import parser

launch_manager: ContextVar[Launart] = ContextVar("daemon.launch_manager")
launch_manager.set(Launart())

launch_args: ContextVar[Namespace] = ContextVar("daemon.launch_args")
launch_args.set(parser.parse_args())
