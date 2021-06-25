
"""

This script adds the the containing package as a valid debug adapter in the Debugger's settings

"""

import sublime

if sublime.version() < '4000':
	raise Exception('This version of the Nuke UI adapter requires Sublime Text 4. Use the st3 branch instead.')

from .adapter.nuke_ui import NukeUI
