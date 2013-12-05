from concurrent.futures import ThreadPoolExecutor
from spock.utils import pl_announce

@pl_announce('ThreadPool')
class ThreadPoolPlugin:
	def __init__(self, ploader, settings):
		w = ploader.requires('Settings')['thread_workers']
		ploader.provides('ThreadPool', ThreadPoolExecutor(max_workers = w))