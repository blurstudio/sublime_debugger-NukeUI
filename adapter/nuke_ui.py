
from Debugger.modules.typecheck import *
import Debugger.modules.debugger.adapter as adapter

from os.path import join, abspath, dirname, expanduser, exists
from shutil import copy, which
import socket

from .util import debugpy_path, ATTACH_TEMPLATE, log as custom_log

import sublime


# This is the id of your adapter. It must be unique and match no 
# other existing adapters.
adapter_type = "NukeUI"


class NukeUI(adapter.AdapterConfiguration):

	@property
	def type(self): return adapter_type

	async def start(self, log, configuration):
		"""
		start() is called when the play button is pressed in the debugger.
		
		The configuration is passed in, allowing you to get necessary settings
		to use when setting up the adapter as it starts up (such as getting the 
		desired host/port to connect to, show below)

		The configuration will be chosen by the user from the 
		configuration_snippets function below, and its contents are the contents 
		of "body:". However, the user can change the configurations manually so 
		make sure to account for unexpected changes. 
		"""

		# Start by finding the python installation on the system
		python = configuration.get("pythonPath")

		if not python:
			if which("python3"):
				python = "python3"
			elif not (python := which("python")):
				raise Exception('No python installation found')
		
		custom_log(f"Found python install: {python}")
		
		# Get host/port from config
		host = configuration['host']
		if host == 'localhost':
			host = '127.0.0.1'
		port = int(configuration['port'])

		# Format the simulated attach response to send it back to the debugger
		# while we set up the debugpy in the background
		attach_code = ATTACH_TEMPLATE.format(
			debugpy_path=debugpy_path,
			hostname=host,
			port=port,
			interpreter=python,
		)

		# Create a socket and connect to server in Nuke
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client.connect(("localhost", 8889))

		# Send the code directly to the server and close the socket
		client.send(attach_code.encode("UTF-8"))
		client.close()

		custom_log(f"Sent attach code:\n\n {attach_code}")

		custom_log(f"Connecting to {host}:{str(port)}")
		
		return adapter.SocketTransport(log, host, port)

	async def install(self, log):
		"""
		When someone installs your adapter, they will also have to install it 
		through the debugger itself. That is when this function is called. It
		allows you to download any extra files or resources, or install items
		to other parts of the device to prepare for debugging in the future
		"""
		
		package_path = dirname(abspath(__file__))
		adapter_path = join(package_path, "adapter")

		# Add debugpy injector to nuke if not present
		user_nuke_path = join(expanduser("~"), ".nuke")
		src_srv = join(adapter_path, 'resources', 'ui_debug_server.py')

		dst_srv = join(user_nuke_path, "ui_debug_server.py")
		menu = join(user_nuke_path, "menu.py")

		first_setup = False

		if not exists(dst_srv):
			copy(src_srv, dst_srv)
			first_setup = True

		if not exists(menu):
			with open(menu, 'w') as f:
				f.write('import ui_debug_server')
		else:
			with open(menu, 'r+') as f:
				contents = f.read()
				if "import ui_debug_server" not in contents:
					f.write("\nimport ui_debug_server")

		if first_setup:
			sublime.message_dialog(
				"Thanks for installing the Nuke UI debug adapter!\n"
				"Because this is your first time installing the adapter, a one-time "
				"setup was performed. Please restart Nuke before continuing."
			)

	@property
	def installed_version(self) -> Optional[str]:
		# The version is only used for display in the UI
		return '0.0.1'

	@property
	def configuration_snippets(self) -> Optional[list]:
		"""
		You can have several configurations here depending on your adapter's 
		offered functionalities, but they all need a "label", "description", 
		and "body"
		"""

		return [
			{
				"label": "Nuke: Custom UI Debugging",
				"description": "Debug Custom UI Components/Functions in Nuke",
				"body": {
					"name": "Nuke: Custom UI Debugging",
					"type": adapter_type,
					"request": "attach",  # can only be attach or launch
					"host": "localhost",
					"port": 7005,
				}
			},
		]

	@property
	def configuration_schema(self) -> Optional[dict]:
		"""
		I am not completely sure what this function is used for. However, 
		it must be present.
		"""

		return None

	async def configuration_resolve(self, configuration):
		"""
		In this function, you can take a currently existing configuration and 
		resolve various variables in it before it gets passed to start().

		Therefore, configurations where values are stated as {my_var} can 
		then be filled out before being used to start the adapter.
		"""

		return configuration
