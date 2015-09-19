import types


class TaskFailed(Exception):
    def __init__(self, *args):
        self.args = args


def accept(evt, data):
    return True


class RunTask(object):
    def __init__(self, task, reg_event_handler, parent=None):
        self.task = task
        self.reg_event_handler = reg_event_handler
        self.parent = parent
        self.expected = {}  # event -> check

        self.run(lambda: next(self.task))

    def run(self, func):
        try:
            response = func()
        except StopIteration as exception:
            if self.parent:
                self.parent.on_success(exception.value)
        except TaskFailed as exception:
            if self.parent:
                self.parent.on_error(exception)
        else:
            self.register(response)

    def on_success(self, data):
        self.run(lambda: self.task.send((None, data)))

    def on_error(self, exception):
        self.run(lambda: self.task.throw(exception))

    def handler(self, event, data):
        check = self.expected.get(event, lambda *_: False)
        if check(event, data):  # TODO does check really need event?
            self.run(lambda: self.task.send((event, data)))
        return True  # remove this handler

    def register(self, response):
        self.parse_response(response)
        for event, check in self.expected.items():
            self.reg_event_handler(event, self.handler)

    def parse_response(self, response):
        # TODO what format do we want to use? also documentation
        # recursive check what the response is
        # generator: subtask
        # str: evt name
        # iterable: check 2. element
        # - str/generator: list of events, register recursively
        # - other (func): evt name + test func

        self.expected.clear()
        if isinstance(response, types.GeneratorType):  # subtask
            RunTask(response, self.reg_event_handler, parent=self)
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
