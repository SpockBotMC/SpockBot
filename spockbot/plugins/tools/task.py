import types

from spockbot.plugins.tools.event import EVENT_UNREGISTER


def accept(evt, data):
    return True


def check_key(key, value):
    return lambda event, data: data[key] == value


class TaskFailed(Exception):
    def __init__(self, message, *args):
        self.message = message
        self.args = (message,) + args

        #: List[Task]: List of all failed tasks since raising this error.
        # Populated in Task.continue_with().
        self.tasktrace = []

        #: TaskFailed: The previous error, if any. Provide via with_error().
        self.prev_error = None

    def with_error(self, prev_error):
        """
        Set the previous error and return self.

        When re-throwing a TaskFailed, you can provide a new, more
        high level failure description and pass along the previously
        failed tasks to still be able to reconstruct the full history of
        failed tasks.

        Examples:
            Re-throw a TaskFailed with a new, more high level description.

            >>> try:
            ...     raise TaskFailed('Low level', {'some': 1}, 'args')
            ... except TaskFailed as prev_err:
            ...     raise TaskFailed('High level').with_error(prev_err)

        Returns:
            TaskFailed
        """
        self.prev_error = prev_error
        return self

    @property
    def full_tasktrace(self):
        """
        List of all failed tasks caused by this and all previous errors.

        Returns:
            List[Task]
        """
        if self.prev_error:
            return self.prev_error.tasktrace + self.tasktrace
        else:
            return self.tasktrace


class TaskCallback(object):
    def __init__(self, cb=None, eb=None):
        self.cb = cb
        self.eb = eb

    def on_success(self, data):
        if self.cb:
            self.cb(data)

    def on_error(self, error):
        if self.eb:
            self.eb(error)


class Task(object):
    def __init__(self, task, parent=None, name=None):
        self.name = name or task.__name__
        self.task = task
        self.parent = parent
        self.expected = {}  # event -> check

    def run(self, task_manager):
        self.task_manager = task_manager
        self.continue_with(lambda: next(self.task))

    def continue_with(self, func):
        try:
            response = func()
        except StopIteration as exception:
            if self.parent:
                self.parent.on_success(exception.args)
        except BaseException as exception:
            if not isinstance(exception, TaskFailed):
                # this task just failed by raising an exception
                exception = TaskFailed('An exception was raised', exception)
            exception.tasktrace.append(self)
            if self.parent:  # xxx makes tasks fail silently by default
                self.parent.on_error(exception)
        else:
            self.register(response)

    def on_success(self, data):
        self.continue_with(lambda: self.task.send((None, data)))

    def on_error(self, exception):
        self.continue_with(lambda: self.task.throw(exception))

    def register(self, response):
        self.expected.clear()
        self.parse_response(response)
        for event, check in self.expected.items():
            self.task_manager.event.reg_event_handler(event, self.on_event)

    def on_event(self, event, data):
        check = self.expected.get(event, None)
        if check and check(event, data):  # TODO does check really need event?
            self.continue_with(lambda: self.task.send((event, data)))
        return EVENT_UNREGISTER  # remove this handler

    def parse_response(self, response):
        # TODO what format do we want to use? also documentation
        # recursive check what the response is
        # generator: subtask
        # str: evt name
        # iterable: check 2. element
        # - str/generator: list of events, register recursively
        # - other (func): evt name + test func

        if isinstance(response, types.GeneratorType):  # subtask
            self.task_manager.run_task(response, parent=self)
        elif isinstance(response, str):  # event name
            self.expected[response] = accept
        elif hasattr(response, '__getitem__'):
            if isinstance(response[1], (str, types.GeneratorType)) \
                    or hasattr(response[1], '__getitem__'):
                # recursive check
                for sub_response in response:
                    self.parse_response(sub_response)
            else:  # event name + check function
                # we should not split these tuples recursively, so catch them
                event, check = response
                self.expected[event] = check
        else:  # unexpected
            self.expected.clear()
            raise ValueError('Illegal task yield argument of type %s: %s'
                             % type(response), response)
