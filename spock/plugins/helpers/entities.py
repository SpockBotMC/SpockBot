"""
An entity tracker
"""
from spock.utils import pl_announce, Info
from spock.plugins.base import PluginBase

import logging
logger = logging.getLogger('spock')

class MCEntity(Info):
    eid = 0
    status = 0
    nbt = None

class ClientPlayerEntity(MCEntity):
    metadata = None

class MovementEntity(MCEntity):
    x = 0
    y = 0
    z = 0
    yaw = 0
    pitch = 0
    on_ground = True

class PlayerEntity(MovementEntity):
    uuid = 0
    current_item = 0
    metadata = None

class ObjectEntity(MovementEntity):
    obj_type = 0
    obj_data = 0
    speed_x = 0
    speed_y = 0
    speed_z = 0

class MobEntity(MovementEntity):
    mob_type = 0
    head_pitch = 0
    head_yaw = 0
    velocity_x = 0
    velocity_y = 0
    velocity_z = 0
    metadata = None

class PaintingEntity(MCEntity):
    title = ""
    location = {
        'x': 0,
        'y': 0,
        'z': 0,
    }
    direction = 0

class ExpEntity(MCEntity):
    x = 0
    y = 0
    z = 0
    count = 0

class GlobalEntity(MCEntity):
    global_type = 0
    x = 0
    y = 0
    z = 0

class EntityCore:
    def __init__(self):
        self.client_player = ClientPlayerEntity()
        self.entities = {}
        self.players = {}
        self.mobs = {}
        self.objects = {}
        self.paintings = {}
        self.exp_orbs = {}
        self.global_entities = {}

@pl_announce('Entities')
class EntityPlugin(PluginBase):
    requires = ('Event')
    events = {
        'PLAY<Join Game': 'handle_join_game',
        'PLAY<Spawn Player': 'handle_spawn_player',
        'PLAY<Spawn Object': 'handle_spawn_object',
        'PLAY<Spawn Mob': 'handle_spawn_mob',
        'PLAY<Spawn Painting': 'handle_spawn_painting',
        'PLAY<Spawn Experience Orb': 'handle_spawn_experience_orb',
        'PLAY<Destroy Entities': 'handle_destroy_entities',
        'PLAY<Entity Equipment': 'handle_unhandled',
        'PLAY<Entity Velocity': 'handle_set_dict',
        'PLAY<Entity Relative Move': 'handle_relative_move',
        'PLAY<Entity Look': 'handle_set_dict',
        'PLAY<Entity Look and Relative Move': 'handle_relative_move',
        'PLAY<Entity Teleport': 'handle_set_dict',
        'PLAY<Entity Head Look': 'handle_set_dict',
        'PLAY<Entity Status': 'handle_set_dict',
        'PLAY<Entity Metadata': 'handle_set_dict',
        'PLAY<Entity Effect': 'handle_unhandled',
        'PLAY<Remove Entity Effect': 'handle_unhandled',
        'PLAY<Entity Properties': 'handle_unhandled',
        'PLAY<Spawn Global Entity': 'handle_spawn_global_entity',
        'PLAY<Update Entity NBT': 'handle_set_dict',
    }
    def __init__(self, ploader, settings):
        super(self.__class__, self).__init__(ploader, settings)
        self.ec = EntityCore()
        ploader.provides('Entities', self.ec)

    #TODO: Implement all these things
    def handle_unhandled(self, event, packet):
        pass

    def handle_join_game(self, event, packet):
        self.ec.client_player.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = self.ec.client_player

    def handle_spawn_player(self, event, packet):
        entity = PlayerEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.players[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_spawn_object(self, event, packet):
        entity = ObjectEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.objects[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_spawn_mob(self, event, packet):
        entity = MobEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.mobs[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_spawn_painting(self, event, packet):
        entity = PaintingEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.paintings[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_spawn_experience_orb(self, event, packet):
        entity = ExpEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.exp_orbs[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_spawn_global_entity(self, event, packet):
        entity = GlobalEntity()
        entity.set_dict(packet.data)
        self.ec.entities[packet.data['eid']] = entity
        self.ec.global_entities[packet.data['eid']] = entity
        self.event.emit('entity_spawn', {'entity': entity})

    def handle_destroy_entities(self, event, packet):
        for eid in packet.data['eids']:
            if eid in self.ec.entities:
                entity = self.ec.entities[eid]
                del self.ec.entities[eid]
                if eid in self.ec.players:
                    del self.ec.players[eid]
                elif eid in self.ec.objects:
                    del self.ec.objects[eid]
                elif eid in self.ec.mobs:
                    del self.ec.mobs[eid]
                elif eid in self.ec.paintings:
                    del self.ec.paintings[eid]
                elif eid in self.ec.exp_orbs:
                    del self.ec.exp_orbs[eid]
                elif eid in self.ec.global_entities:
                    del self.ec.global_entities[eid]
                self.event.emit('entity_destroy', {'entity': entity})

    def handle_relative_move(self, event, packet):
        if packet.data['eid'] in self.ec.entities:
            entity = self.ec.entities[packet.data['eid']]
            old_pos = [entity.x, entity.y, entity.z]
            entity.set_dict(packet.data)
            entity.x = entity.x + packet.data['dx']
            entity.y = entity.y + packet.data['dy']
            entity.z = entity.z + packet.data['dz']
            self.event.emit('entity_move', {'entity': entity, 'old_pos': old_pos})

    def handle_set_dict(self, event, packet):
        if packet.data['eid'] in self.ec.entities:
            self.ec.entities[packet.data['eid']].set_dict(packet.data)
