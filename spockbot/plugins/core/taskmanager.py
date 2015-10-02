from spockbot.plugins.base import PluginBase
from spockbot.plugins.tools.task import Task
from spockbot.utils import pl_announce


@pl_announce('TaskManager')
class TaskManager(PluginBase):
    requires = 'Event'

    def __init__(self, ploader, settings):
        super(TaskManager, self).__init__(ploader, settings)
        ploader.provides('TaskManager', self)

    def run_task(self, task, parent=None):
        if not isinstance(task, Task):
            task = Task(task, parent)
        task.run(self)
        return task
