"""
ClientInfo is a central plugin for recording data about the client,
e.g. Health, position, and some auxillary information like the player list.
Plugins subscribing to ClientInfo's events don't have to independently
track this information on their own.
"""

from spock.utils import pl_announce, Info, Position
from spock.mcp import mcdata
from spock.mcp.mcdata import (
    FLG_XPOS_REL, FLG_YPOS_REL, FLG_ZPOS_REL, FLG_YROT_REL, FLG_XROT_REL, GS_GAMEMODE
)
from spock.plugins.base import PluginBase

class GameInfo(Info):
    def __init__(self):
        self.level_type = 0
        self.dimension = 0
        self.gamemode = 0
        self.difficulty = 0
        self.max_players = 0

class Abilities(Info):
    def __init__(self):
        self.damage = True
        self.fly = False
        self.flying = False
        self.creative = False
        self.flying_speed = 0
        self.walking_speed = 0

class PlayerHealth(Info):
    def __init__(self):
        self.health = 20
        self.food = 20
        self.food_saturation = 5

class PlayerPosition(Position):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.yaw = 0.0
        self.pitch = 0.0
        self.on_ground = False

class PlayerListItem(Info):
    def __init__(self):
        self.uuid = 0
        self.name = ''
        self.display_name = None
        self.ping = 0
        self.gamemode = 0

class ClientInfo:
    def __init__(self):
        self.eid = 0
        self.name = ""
        self.uuid = ""
        self.abilities = Abilities()
        self.game_info = GameInfo()
        self.spawn_position = Position()
        self.health = PlayerHealth()
        self.position = PlayerPosition()
        self.player_list = {}

    def reset(self):
        self.__init__()

@pl_announce('ClientInfo')
class ClientInfoPlugin(PluginBase):
    requires = ('Event')
    events = {
        'LOGIN<Login Success': 'handle_login_success',
        'PLAY<Join Game': 'handle_join_game',
        'PLAY<Spawn Position': 'handle_spawn_position',
        'PLAY<Update Health': 'handle_update_health',
        'PLAY<Player Position and Look': 'handle_position_update',
        'PLAY<Player List Item': 'handle_player_list',
        'PLAY<Change Game State': 'handle_game_state',
        'PLAY<Server Difficulty': 'handle_server_difficulty',
        'PLAY<Player Abilities': 'handle_player_abilities',
        'disconnect': 'handle_disconnect',
    }
    def __init__(self, ploader, settings):
        super(self.__class__, self).__init__(ploader, settings)
        self.uuids = {}
        self.defered_pl = {}
        self.client_info = ClientInfo()
        ploader.provides('ClientInfo', self.client_info)

    #Login Success - Update client name and uuid
    def handle_login_success(self, name, packet):
        self.client_info.uuid = packet.data['uuid']
        self.client_info.name = packet.data['username']
        self.event.emit('cl_login_success')

    #Join Game - Update client state info
    def handle_join_game(self, name, packet):
        self.client_info.eid = packet.data['eid']
        self.client_info.game_info.set_dict(packet.data)
        self.event.emit('cl_join_game', self.client_info.game_info)

    #Spawn Position - Update client Spawn Position state
    def handle_spawn_position(self, name, packet):
        self.client_info.spawn_position.set_dict(packet.data['location'])
        self.event.emit('cl_spawn_update', self.client_info.spawn_position)

    #Update Health - Update client Health state
    def handle_update_health(self, name, packet):
        self.client_info.health.set_dict(packet.data)
        self.event.emit('cl_health_update', self.client_info.health)
        if packet.data['health'] <= 0.0:
            self.event.emit('cl_death', self.client_info.health)

    #Player Position and Look - Update client Position state
    def handle_position_update(self, name, packet):
        f = packet.data['flags']
        p = self.client_info.position
        d = packet.data
        p.x = p.x + d['x'] if f&FLG_XPOS_REL else d['x']
        p.y = p.y + d['y'] if f&FLG_YPOS_REL else d['y']
        p.z = p.z + d['z'] if f&FLG_ZPOS_REL else d['z']
        p.yaw = p.yaw + d['yaw'] if f&FLG_YROT_REL else d['yaw']
        p.pitch = p.pitch + d['pitch'] if f&FLG_XROT_REL else d['pitch']
        self.event.emit('cl_position_update', self.client_info.position)

    #Player List Item - Update player list
    def handle_player_list(self, name, packet):
        act = packet.data['action']
        for pl in packet.data['player_list']:
            if act == mcdata.PL_ADD_PLAYER and pl['uuid'] not in self.uuids:
                item = PlayerListItem()
                item.set_dict(pl)
                if pl['uuid'] in self.defered_pl:
                    for i in self.defered_pl[pl['uuid']]:
                        item.set_dict(i)
                    del self.defered_pl[pl['uuid']]
                self.client_info.player_list[pl['uuid']] = item
                self.uuids[pl['uuid']] = item
                self.event.emit('cl_add_player', item)
            elif (
                act == mcdata.PL_UPDATE_GAMEMODE or
                act == mcdata.PL_UPDATE_LATENCY  or
                act == mcdata.PL_UPDATE_DISPLAY
            ):
                if pl['uuid'] in self.uuids:
                    item = self.uuids[pl['uuid']]
                    item.set_dict(pl)
                    self.event.emit('cl_update_player', item)
                #Sometime the server sends updates before it gives us the player
                #We store those in a list and apply them when ADD_PLAYER is sent
                else:
                    defered = self.defered_pl.get(pl['uuid'], [])
                    defered.append(pl)
                    self.defered_pl[pl['uuid']] = defered
            elif act == mcdata.PL_REMOVE_PLAYER and pl['uuid'] in self.uuids:
                item = self.uuids[pl['uuid']]
                del self.client_info.player_list[pl['uuid']]
                del self.uuids[pl['uuid']]
                self.event.emit('cl_remove_player', item)

    #Change Game State
    def handle_game_state(self, name, packet):
        if packet.data['reason'] == GS_GAMEMODE:
            self.client_info.game_info.gamemode = packet.data['value']

    #Server Difficulty
    def handle_server_difficulty(self, name, packet):
        self.client_info.game_info.difficulty = packet.data['difficulty']

    #Player Abilities
    def handle_player_abilities(self, name, packet):
        #TODO: flag stuff here
        self.client_info.abilities.flying_speed = packet.data['flying_speed']
        self.client_info.abilities.walking_speed = packet.data['walking_speed']

    def handle_disconnect(self, name, data):
        self.client_info.reset()
