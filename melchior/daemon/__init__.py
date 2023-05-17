from creart import it
from graia.broadcast import Broadcast

from melchior.daemon._ctx import launch_manager
from melchior.daemon.service import MelchiorDaemonService


def run():
    bc = it(Broadcast)
    mgr = launch_manager.get()
    mgr.add_launchable(MelchiorDaemonService())
    mgr.launch_blocking(loop=bc.loop)
