import types

from spockbot.plugins.tools.event import EVENT_UNREGISTER


def accept(evt, data):
    return True


def check_key(key, value):
    """Generates a check function for a certain key-value pair.

    Creates and returns a function that takes two arguments ``(event, data)``
    and checks ``data[key]`` and ``value`` for equality.

    This is supposed to be used as a check function generator for the
    ``yield`` statements in tasks.

    Example:
        Wait for the next ``player_join`` event that has
        its ``name`` set to ``Bob``, i.e. ``data = {'name': 'Bob'}``.

        >>> def my_task():
        ...     yield 'player_join', check_key('name', 'Bob')
    """
    return lambda event, data: data[key] == value


class TaskFailed(Exception):
    """
    Raising this exception in any task stops it and signalizes the parent task
    that the task was aborted due to an error.

    Attributes:
        message (str): Description of the failure
        tasktrace (List[Task]): List of all failed tasks
                                since raising this error.
        prev_error (TaskFailed): The previous error, if any.
                                 Provide via ``with_error()``.
    """
    def __init__(self, message, *args):
        self.message = message
        self.args = (message,) + args
        self.tasktrace = []
        self.prev_error = None

    def with_error(self, prev_error):
        """Sets the previous error and returns self.

        When re-throwing a TaskFailed, you can provide a new,
        more high level failure description and pass along the
        previously failed tasks to still be able to reconstruct
        the full history of failed tasks.

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

    def __str__(self):
        """
        Newline-separated text with all failed tasks and all previous errors.
        """
        s = self.prev_error.failures + '\n' if self.prev_error else ''

        s += '%s' % self.message
        if self.args[1:]:
            s += ' %s' % str(self.args[1:])

        for task in self.tasktrace:
            s += '\n  in %s %s' % (task.task.__name__, task.name)
        return s


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
        self.last_child = None
        self.expected = {}  # event -> check

    @property
    def tasktrace(self):
        """
        List of all parent tasks up to this one.

        Returns:
            List[Task]
        """
        if self.parent:
            return self.parent.parents + [self]
        else:
            return [self]

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
            if isinstance(exception, TaskFailed):
                exception.tasktrace.append(self)
            if self.parent:
                self.parent.on_error(exception)
            else:
                raise
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
                             % (type(response), response))
