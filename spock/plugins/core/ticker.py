class TickPlugin:
    def __init__(self, ploader, settings):
        self.event = ploader.requires("Event")
        timers = ploader.requires("Timers")
        timers.reg_event_timer(0.05, self.client_tick, -1)
        timers.reg_event_timer(0.02, self.physics_tick, -1)

    def client_tick(self):
        self.event.emit('client_tick')

    def physics_tick(self):
        self.event.emit('physics_tick')
