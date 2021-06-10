
"""

This script adds the the containing package as a valid debug adapter in the Debugger's settings

"""

from Debugger.modules.debugger.adapter.adapters import Adapters
from .adapter.nuke_ui import NukeUI

import sublime


if sublime.version() < '4000':
	raise Exception('This version of the Houdini UI adapter requires Sublime Text 4. Use the st3 branch instead.')


def plugin_loaded():
    """
    Add Nuke UI adapter to list of adapters, that way it is recognized by the debugger.
    """

    Adapters.all.append(NukeUI())
