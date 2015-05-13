from spock.utils import get_settings

class PluginBase(object):
	"""A base class for cleaner plugin code.

	Extending from PluginBase allows you to declare any requirements, default
	settings, and event listeners in a declarative way. Define the appropriate
	attributes on your subclass and enjoy cleaner code.
	"""
	requires = ()
	defaults = {}
	events = {}

	def __init__(self, ploader, settings):
		# Load the plugin's settings.
		self.settings = get_settings(self.defaults, settings)

		# Load all the plugin's dependencies.
		for requirement in self.requires:
			setattr(self, requirement.lower(), ploader.requires(requirement))

		# Setup the plugin's event handlers.
		for event in self.events.keys():
			if hasattr(self, self.events[event]):
				ploader.reg_event_handler(event, getattr(self, self.events[event]))
			else:
				pass  # Do something useful here, like logging it.
