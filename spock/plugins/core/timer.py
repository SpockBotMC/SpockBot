"""
Provides clock-time and **SERVER** tick-timers and a convenient API for
registering them. Clock-time timers are as precise as the underlying OS
makes them, server tick-timers are based on time updates from the server
"""

import time
from spock.mcp import mcdata
from spock.utils import pl_announce
from spock.plugins.base import PluginBase

class BaseTimer(object):
    def __init__(self, callback, runs = -1):
        self.callback = callback
        self.runs = runs

    def countdown(self):
        return -1

    def check(self):
        return True

    def get_runs(self):
        return self.runs

    def update(self):
        if self.check():
            self.fire()

    def fire(self):
        self.callback()
        if self.runs>0 and not self.runs<0:
            self.runs-=1
        if self.runs:
            self.reset()

    def stop(self):
        self.runs = 0

    def reset(self):
        pass

#Time based timer
class EventTimer(BaseTimer):
    def __init__(self, wait_time, callback, runs = 1):
        super(self.__class__, self).__init__(callback, runs)
        self.wait_time = wait_time
        self.end_time = time.time() + self.wait_time

    def countdown(self):
        count = self.end_time - time.time()
        return count if count > 0 else 0

    def check(self):
        if self.runs == 0: return False
        return self.end_time<=time.time()

    def reset(self):
        self.end_time = time.time() + self.wait_time

#World tick based timer
class TickTimer(BaseTimer):
    def __init__(self, world, wait_ticks, callback, runs = 1):
        super(self.__class__, self).__init__(callback, runs)
        self.world = world
        self.wait_ticks = wait_ticks
        self.end_tick = self.world.age + self.wait_ticks

    def check(self):
        if self.runs == 0: return False
        return self.end_tick<=self.world.age

    def reset(self):
        self.end_tick = self.world.age + self.wait_ticks

class TimerCore:
    def __init__(self, world):
        self.timers = []
        self.persist_timers = []
        self.world = world

    def reg_timer(self, timer, persist = False):
        if not persist:
            self.timers.append(timer)
        else:
            self.persist_timers.append(timer)

    def get_timeout(self):
        timeout = -1
        for timer in self.timers + self.persist_timers:
            if timeout > timer.countdown() or timeout == -1:
                    timeout = timer.countdown()
        return timeout

    def reg_event_timer(self, wait_time, callback, runs = -1, persist = False):
        self.reg_timer(EventTimer(wait_time, callback, runs), persist)

    def reg_tick_timer(self, wait_ticks, callback, runs = -1, persist = False):
        self.reg_timer(TickTimer(self.world, wait_ticks, callback, runs), persist)

class WorldTick:
    def __init__(self):
        self.age = 0

@pl_announce('Timers')
class TimerPlugin(PluginBase):
    requires = ('World')
    events = {
        'event_tick': 'tick',
        'disconnect': 'handle_disconnect',
    }
    def __init__(self, ploader, settings):
        super(self.__class__, self).__init__(ploader, settings)
        if not self.world:
            self.world = WorldTick()
            ploader.reg_event_handler('PLAY<Time Update', self.handle_time_update)
        self.timer_core = TimerCore(self.world)
        ploader.provides('Timers', self.timer_core)

    def tick(self, name, data):
        for timer in self.timer_core.timers:
            timer.update()
            if not timer.get_runs():
                self.timer_core.timers.remove(timer)
        for timer in self.timer_core.persist_timers:
            timer.update()
            if not timer.get_runs():
                self.timer_core.persist_timers.remove(timer)

    #Time Update - We grab world age if the world plugin isn't available
    def handle_time_update(self, name, packet):
        self.world.age = packet.data['world_age']

    def handle_disconnect(self, name, data):
        self.timer_core.timers = []
