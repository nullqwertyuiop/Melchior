from creart import it
from graia.broadcast import Broadcast

from library.core._ctx import launch_manager
from library.core.service.data import MelchiorServiceData
from library.core.service.essential import MelchiorServiceEssential


def launch():
    mgr = launch_manager.get()
    mgr.add_launchable(MelchiorServiceEssential())
    mgr.add_launchable(MelchiorServiceData())
    mgr.launch_blocking(loop=it(Broadcast).loop)
