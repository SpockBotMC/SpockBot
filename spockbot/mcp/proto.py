# Most of the data formats, structures, and magic values
MC_PROTOCOL_VERSION = 109

SERVER_TO_CLIENT = 0x00
CLIENT_TO_SERVER = 0x01

PROTO_COMP_ON = 0x00
PROTO_COMP_OFF = 0x01

MC_BOOL = 0x00
MC_UBYTE = 0x01
MC_BYTE = 0x02
MC_USHORT = 0x03
MC_SHORT = 0x04
MC_UINT = 0x05
MC_INT = 0x06
MC_ULONG = 0x07
MC_LONG = 0x08
MC_FLOAT = 0x09
MC_DOUBLE = 0x0A
MC_VARINT = 0x0B
MC_VARLONG = 0x0C
MC_FP_INT = 0x0D
MC_FP_BYTE = 0x0E
MC_UUID = 0x0F
MC_POSITION = 0x10
MC_STRING = 0x11
MC_CHAT = 0x12
MC_SLOT = 0x13
MC_META = 0x14

HANDSHAKE_STATE = 0x00
STATUS_STATE = 0x01
LOGIN_STATE = 0x02
PLAY_STATE = 0x03

data_structs = (
    # (struct_suffix, size), #type
    ('?', 1),  # bool
    ('B', 1),  # ubyte
    ('b', 1),  # byte
    ('H', 2),  # ushort
    ('h', 2),  # short
    ('I', 4),  # uint
    ('i', 4),  # int
    ('Q', 8),  # ulong
    ('q', 8),  # long
    ('f', 4),  # float
    ('d', 8),  # double
)

particles = (
    # (name, data_length)
    ('explosion_normal', 0),
    ('explosion_large', 0),
    ('explosion_huge', 0),
    ('fireworks_spark', 0),
    ('water_bubble', 0),
    ('water_splash', 0),
    ('water_wake', 0),
    ('suspended', 0),
    ('suspended_depth', 0),
    ('crit', 0),
    ('crit_magic', 0),
    ('smoke_normal', 0),
    ('smoke_large', 0),
    ('spell', 0),
    ('spell_instant', 0),
    ('spell_mob', 0),
    ('spell_mob_ambient', 0),
    ('spell_witch', 0),
    ('drip_water', 0),
    ('drip_lava', 0),
    ('villager_angry', 0),
    ('villager_happy', 0),
    ('town_aura', 0),
    ('note', 0),
    ('portal', 0),
    ('enchantment_table', 0),
    ('flame', 0),
    ('lava', 0),
    ('footstep', 0),
    ('cloud', 0),
    ('redstone', 0),
    ('snowball', 0),
    ('snow_shovel', 0),
    ('slime', 0),
    ('heart', 0),
    ('barrier', 0),
    ('icon_crack', 2),
    ('block_crack', 1),
    ('block_dust', 1),
    ('water_drop', 0),
    ('item_take', 0),
    ('dragon_breath', 0),
    ('endrod', 0),
    ('damage_indicator', 0),
    ('sweep_attack', 0),
)

# Structs formatted for readability
# Packed into tuples at end of file
packet_names = {
    HANDSHAKE_STATE: {
        SERVER_TO_CLIENT: {},
        CLIENT_TO_SERVER: {
            0x00: 'Handshake',
        },
    },

    STATUS_STATE: {
        SERVER_TO_CLIENT: {
            0x00: 'Status Response',
            0x01: 'Status Ping',
        },
        CLIENT_TO_SERVER: {
            0x00: 'Status Request',
            0x01: 'Status Ping',
        },
    },

    LOGIN_STATE: {
        SERVER_TO_CLIENT: {
            0x00: 'Disconnect',
            0x01: 'Encryption Request',
            0x02: 'Login Success',
            0x03: 'Set Compression',
        },
        CLIENT_TO_SERVER: {
            0x00: 'Login Start',
            0x01: 'Encryption Response',
        },
    },

    PLAY_STATE: {
        SERVER_TO_CLIENT: {
            0x00: 'Spawn Object',
            0x01: 'Spawn Experience Orb',
            0x02: 'Spawn Global Entity',
            0x03: 'Spawn Mob',
            0x04: 'Spawn Painting',
            0x05: 'Spawn Player',
            0x06: 'Animation',
            0x07: 'Statistics',
            0x08: 'Block Break Animation',
            0x09: 'Update Block Entity',
            0x0A: 'Block Action',
            0x0B: 'Block Change',
            0x0C: 'Boss Bar',  # new
            0x0D: 'Server Difficulty',
            0x0E: 'Tab-Complete',
            0x0F: 'Chat Message',
            0x10: 'Multi Block Change',
            0x11: 'Confirm Transaction',
            0x12: 'Close Window',
            0x13: 'Open Window',
            0x14: 'Window Items',
            0x15: 'Window Property',
            0x16: 'Set Slot',
            0x17: 'Set Cooldown',  # new
            0x18: 'Plugin Message',
            0x19: 'Named Sound Effect',  # new
            0x1A: 'Disconnect',
            0x1B: 'Entity Status',
            0x1C: 'Explosion',
            0x1D: 'Unload Chunk',  # new
            0x1E: 'Change Game State',
            0x1F: 'Keep Alive',
            0x20: 'Chunk Data',
            0x21: 'Effect',
            0x22: 'Particle',
            0x23: 'Join Game',
            0x24: 'Map',  # name change
            0x25: 'Entity Relative Move',
            0x26: 'Entity Look And Relative Move',
            0x27: 'Entity Look',
            0x28: 'Entity',
            0x29: 'Vehicle Move',  # new
            0x2A: 'Open Sign Editor',  # name change
            0x2B: 'Player Abilities',
            0x2C: 'Combat Event',
            0x2D: 'Player List Item',
            0x2E: 'Player Position and Look',
            0x2F: 'Use Bed',
            0x30: 'Destroy Entities',
            0x31: 'Remove Entity Effect',
            0x32: 'Resource Pack Send',
            0x33: 'Respawn',
            0x34: 'Entity Head Look',
            0x35: 'World Border',
            0x36: 'Camera',
            0x37: 'Held Item Change',
            0x38: 'Display Scoreboard',
            0x39: 'Entity Metadata',
            0x3A: 'Attach Entity',
            0x3B: 'Entity Velocity',
            0x3C: 'Entity Equipment',
            0x3D: 'Set Experience',
            0x3E: 'Update Health',
            0x3F: 'Scoreboard Objective',
            0x40: 'Set Passengers',  # new
            0x41: 'Teams',
            0x42: 'Update Score',
            0x43: 'Spawn Position',
            0x44: 'Time Update',
            0x45: 'Title',
            0x46: 'Update Sign',
            0x47: 'Sound Effect',
            0x48: 'Player List Header/Footer',
            0x49: 'Collect Item',
            0x4A: 'Entity Teleport',
            0x4B: 'Entity Properties',
            0x4C: 'Entity Effect',
        },

        CLIENT_TO_SERVER: {
            0x00: 'Teleport Confirm',  # new
            0x01: 'Tab-Complete',
            0x02: 'Chat Message',
            0x03: 'Client Status',
            0x04: 'Client Settings',
            0x05: 'Confirm Transaction',
            0x06: 'Enchant Item',
            0x07: 'Click Window',
            0x08: 'Close Window',
            0x09: 'Plugin Message',
            0x0A: 'Use Entity',
            0x0B: 'Keep Alive',
            0x0C: 'Player Position',
            0x0D: 'Player Position and Look',
            0x0E: 'Player Look',
            0x0F: 'Player',
            0x10: 'Vehicle Move',  # new
            0x11: 'Steer Boat',  # new
            0x12: 'Player Abilities',
            0x13: 'Player Digging',
            0x14: 'Entity Action',
            0x15: 'Steer Vehicle',
            0x16: 'Resource Pack Status',
            0x17: 'Held Item Change',
            0x18: 'Creative Inventory Action',
            0x19: 'Update Sign',
            0x1A: 'Animation',
            0x1B: 'Spectate',
            0x1C: 'Player Block Placement',
            0x1D: 'Use Item',
        },
    },
}

packet_structs = {
    HANDSHAKE_STATE: {
        SERVER_TO_CLIENT: {
            # Empty, server doesn't handshake
        },
        CLIENT_TO_SERVER: {
            # Handshake
            0x00: (
                (MC_VARINT, 'protocol_version'),
                (MC_STRING, 'host'),
                (MC_USHORT, 'port'),
                (MC_VARINT, 'next_state'),
            ),
        },
    },

    STATUS_STATE: {
        SERVER_TO_CLIENT: {
            # Status Response
            0x00: (
                (MC_STRING, 'response'),
            ),
            # Status Ping
            0x01: (
                (MC_LONG, 'time'),
            ),
        },
        CLIENT_TO_SERVER: {
            # Status Request
            0x00: (
                # Empty Packet
            ),
            # Status Ping
            0x01: (
                (MC_LONG, 'time'),
            ),
        },
    },

    LOGIN_STATE: {
        SERVER_TO_CLIENT: {
            # Disconnect
            0x00: (
                (MC_CHAT, 'json_data'),
            ),
            # Encryption Request
            0x01: (
                (MC_STRING, 'server_id'),
                # Extension
                # byte string 'public_key'
                # byte string 'verify_token'
            ),
            # Login Success
            0x02: (
                (MC_STRING, 'uuid'),
                (MC_STRING, 'username'),
            ),
            # Set Compression
            0x03: (
                (MC_VARINT, 'threshold'),
            ),
        },
        CLIENT_TO_SERVER: {
            # Login Start
            0x00: (
                (MC_STRING, 'name'),
            ),
            # Encryption Response
            0x01: (
                # Extension
                # byte string 'shared_secret'
                # byte string 'verify token'
            ),
        },
    },

    PLAY_STATE: {
        SERVER_TO_CLIENT: {
            # Spawn Object
            0x00: (
                (MC_VARINT, 'eid'),
                (MC_UUID, 'uuid'),
                (MC_UBYTE, 'obj_type'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BYTE, 'pitch'),
                (MC_BYTE, 'yaw'),
                (MC_INT, 'obj_data'),
                # Extension
                # If obj_data != 0
                # short 'speed_x'
                # short 'speed_y'
                # short 'speed_z'
            ),
            # Spawn Experience Orb
            0x01: (
                (MC_VARINT, 'eid'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_SHORT, 'count'),
            ),
            # Spawn Global Entity
            0x02: (
                (MC_VARINT, 'eid'),
                (MC_BYTE, 'global_type'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
            ),
            # Spawn Mob
            0x03: (
                (MC_VARINT, 'eid'),
                (MC_UUID, 'uuid'),
                (MC_UBYTE, 'mob_type'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BYTE, 'yaw'),
                (MC_BYTE, 'pitch'),
                (MC_BYTE, 'head_pitch'),
                (MC_SHORT, 'velocity_x'),
                (MC_SHORT, 'velocity_y'),
                (MC_SHORT, 'velocity_z'),
                (MC_META, 'metadata'),
            ),
            # Spawn Painting
            0x04: (
                (MC_VARINT, 'eid'),
                (MC_UUID, 'uuid'),
                (MC_STRING, 'title'),
                (MC_POSITION, 'location'),
                (MC_BYTE, 'direction'),
            ),
            # Spawn Player
            0x05: (
                (MC_VARINT, 'eid'),
                (MC_UUID, 'uuid'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BYTE, 'yaw'),
                (MC_BYTE, 'pitch'),
                (MC_META, 'metadata'),
            ),
            # Animation
            0x06: (
                (MC_VARINT, 'eid'),
                (MC_UBYTE, 'animation'),
            ),
            # Statistics
            0x07: (
                # Extension
                # List of lists 'entries'
                # First value is a string, stat's name
                # Second value is an int, stat's value
            ),
            # Block Break Animation
            0x08: (
                (MC_VARINT, 'eid'),
                (MC_POSITION, 'location'),
                (MC_BYTE, 'stage'),
            ),
            # Update Block Entity
            0x09: (
                (MC_POSITION, 'location'),
                (MC_UBYTE, 'action'),
                # Extension
                # NBT Data 'nbt'
            ),
            # Block Action
            0x0A: (
                (MC_POSITION, 'location'),
                (MC_UBYTE, 'byte_1'),
                (MC_UBYTE, 'byte_2'),
                (MC_VARINT, 'block_id'),
            ),
            # Block Change
            0x0B: (
                (MC_POSITION, 'location'),
                (MC_VARINT, 'block_data'),
            ),
            # Boss Bar
            0x0C: (
                (MC_UUID, 'uuid'),
                (MC_VARINT, 'action'),
                # Extension
                # TODO
            ),
            # Server Difficulty
            0x0D: (
                (MC_UBYTE, 'difficulty'),
            ),
            # Tab-Complete
            0x0E: (
                # Extension
                # List of strings 'matches'
            ),
            # Chat Message
            0x0F: (
                (MC_CHAT, 'json_data'),
                (MC_BYTE, 'position'),
            ),
            # Multi Block Change
            0x10: (
                (MC_INT, 'chunk_x'),
                (MC_INT, 'chunk_z'),
                # Extension
                # List of dicts 'blocks'
            ),
            # Confirm Transaction
            0x11: (
                (MC_UBYTE, 'window_id'),
                (MC_SHORT, 'action'),
                (MC_BOOL, 'accepted'),
            ),
            # Close Window
            0x12: (
                (MC_UBYTE, 'window_id'),
            ),
            # Open Window
            0x13: (
                (MC_UBYTE, 'window_id'),
                (MC_STRING, 'inv_type'),
                (MC_CHAT, 'title'),
                (MC_UBYTE, 'slot_count'),
                # Extension
                # Only present if 'inv_type' == 'EntityHorse'
                # MC_INT 'eid'
            ),
            # Window Items
            0x14: (
                (MC_UBYTE, 'window_id'),
                # Extension
                # List of slots 'slots'
            ),
            # Window Property
            0x15: (
                (MC_UBYTE, 'window_id'),
                (MC_SHORT, 'property'),
                (MC_SHORT, 'value'),
            ),
            # Set Slot
            0x16: (
                (MC_BYTE, 'window_id'),
                (MC_SHORT, 'slot'),
                (MC_SLOT, 'slot_data'),
            ),
            # Set Cooldown
            0x17: (
                (MC_VARINT, 'id'),
                (MC_VARINT, 'ticks'),
            ),
            # Plugin Message
            0x18: (
                (MC_STRING, 'channel'),
                # Extension
                # byte string 'data'
            ),
            # Named Sound Effect
            0x19: (
                (MC_STRING, 'name'),
                (MC_VARINT, 'type'),
                (MC_INT, 'ef_x'),
                (MC_INT, 'ef_y'),
                (MC_INT, 'ef_z'),
                (MC_FLOAT, 'vol'),
                (MC_UBYTE, 'pitch'),
            ),
            # Disconnect
            0x1A: (
                (MC_STRING, 'reason'),
            ),
            # Entity Status
            0x1B: (
                (MC_INT, 'eid'),
                (MC_BYTE, 'status')
            ),
            # Explosion
            0x1C: (
                (MC_FLOAT, 'x'),
                (MC_FLOAT, 'y'),
                (MC_FLOAT, 'z'),
                (MC_FLOAT, 'radius'),
                # Extension
                # List of lists 'blocks'
                # Each list is 3 ints x,y,z
                # float 'player_x'
                # float 'player_y'
                # float 'player_z'
            ),
            # Unload Chunk
            0x1D: (
                (MC_INT, 'x'),
                (MC_INT, 'z'),
            ),
            # Change Game State
            0x1E: (
                (MC_UBYTE, 'reason'),
                (MC_FLOAT, 'value'),
            ),
            # Keep Alive
            0x1F: (
                (MC_VARINT, 'keep_alive'),
            ),
            # Chunk Data
            0x20: (
                (MC_INT, 'chunk_x'),
                (MC_INT, 'chunk_z'),
                (MC_BOOL, 'continuous'),
                (MC_VARINT, 'primary_bitmap'),
                # Extension
                # byte string 'data'
                # byte string 'biomes'
            ),
            # Effect
            0x21: (
                (MC_INT, 'effect'),
                (MC_POSITION, 'location'),
                (MC_INT, 'data'),
                (MC_BOOL, 'no_rel_vol'),
            ),
            # Particle
            0x22: (
                (MC_INT, 'id'),
                (MC_BOOL, 'long_dist'),
                (MC_FLOAT, 'x'),
                (MC_FLOAT, 'y'),
                (MC_FLOAT, 'z'),
                (MC_FLOAT, 'off_x'),
                (MC_FLOAT, 'off_y'),
                (MC_FLOAT, 'off_z'),
                (MC_FLOAT, 'speed'),
                (MC_INT, 'num'),
                # Extension
                # List of ints 'data'
                # Possibly zero length list of
                # particle-dependent data
            ),
            # Join Game
            0x23: (
                (MC_INT, 'eid'),
                (MC_UBYTE, 'gamemode'),
                (MC_INT, 'dimension'),
                (MC_UBYTE, 'difficulty'),
                (MC_UBYTE, 'max_players'),
                (MC_STRING, 'level_type'),
                (MC_BOOL, 'reduce_debug'),
            ),
            # Map
            0x24: (
                (MC_VARINT, 'item_damage'),
                (MC_BYTE, 'scale'),
                # Extension
                # List of tuples 'icons', (Direction, Type, X, Y)
                # MC_BYTE 'columns'
                # If Columns > 0
                # MC_BYTE 'rows'
                # MC_BYTE 'x'
                # MC_BYTE 'y'
                # byte string 'data'
            ),
            # Entity Relative Move
            0x25: (
                (MC_VARINT, 'eid'),
                (MC_SHORT, 'dx'),
                (MC_SHORT, 'dy'),
                (MC_SHORT, 'dz'),
                (MC_BOOL, 'on_ground'),
            ),
            # Entity Look And Relative Move
            0x26: (
                (MC_VARINT, 'eid'),
                (MC_SHORT, 'dx'),
                (MC_SHORT, 'dy'),
                (MC_SHORT, 'dz'),
                (MC_BYTE, 'yaw'),
                (MC_BYTE, 'pitch'),
                (MC_BOOL, 'on_ground'),
            ),
            # Entity Look
            0x27: (
                (MC_VARINT, 'eid'),
                (MC_BYTE, 'yaw'),
                (MC_BYTE, 'pitch'),
                (MC_BOOL, 'on_ground'),
            ),
            # Entity
            0x28: (
                (MC_VARINT, 'eid'),
            ),
            # Vehicle Move
            0x29: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
            ),
            # Open Sign Editor
            0x2A: (
                (MC_POSITION, 'location'),
            ),
            # Player Abilities
            0x2B: (
                (MC_BYTE, 'flags'),
                (MC_FLOAT, 'flying_speed'),
                (MC_FLOAT, 'walking_speed'),
            ),
            # Combat Event
            0x2C: (
                (MC_VARINT, 'event'),
                # Extension
                # CE_END_COMBAT
                # MC_VARINT 'duration'
                # MC_INT    'eid'
                # CE_ENTITY_DEAD
                # MC_VARINT 'player_id'
                # MC_INT    'eid'
                # MC_STRING 'message'
            ),
            # Player List Item
            0x2D: (
                (MC_VARINT, 'action'),
                # Extension
                # List of dicts 'player_list'
                # MC_UUID 'uuid'
                # PL_ADD_PLAYER
                # MC_STRING 'name'
                # List of dicts, 'properties'
                # MC_STRING 'name'
                # MC_STRING 'value'
                # MC_BOOL   'signed'
                # signed == True
                # MC_STRING 'signature'
                # MC_VARINT 'gamemode'
                # MC_VARINT 'ping'
                # MC_BOOL   'has_display'
                # has_display == True
                # MC_CHAT 'display_name'
                # PL_UPDATE_GAMEMODE
                # MC_VARINT 'gamemode'
                # PL_UPDATE_LATENCY
                # MC_VARINT 'ping'
                # PL_UPDATE_DISPLAY
                # MC_BOOL 'has_display'
                # has_display == True
                # MC_CHAT 'display_name'
                # PL_REMOVE_PLAYER
                # No extra fields
            ),
            # Player Position and Look
            0x2E: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
                (MC_BYTE, 'flags'),
                (MC_VARINT, 'teleport_id'),
            ),
            # Use Bed
            0x2F: (
                (MC_INT, 'eid'),
                (MC_POSITION, 'location'),
            ),
            # Destroy Entities
            0x30: (
                # Extension
                # List of ints 'eids'
            ),
            # Remove Entity Effect
            0x31: (
                (MC_VARINT, 'eid'),
                (MC_BYTE, 'effect'),
            ),
            # Resource Pack Send
            0x32: (
                (MC_STRING, 'url'),
                (MC_STRING, 'hash'),
            ),
            # Respawn
            0x33: (
                (MC_INT, 'dimension'),
                (MC_UBYTE, 'difficulty'),
                (MC_UBYTE, 'gamemode'),
                (MC_STRING, 'level_type'),
            ),
            # Entity Head Look
            0x34: (
                (MC_VARINT, 'eid'),
                (MC_BYTE, 'head_yaw'),
            ),
            # World Border
            0x35: (
                (MC_VARINT, 'action'),
                # Extension
                # WB_SET_SIZE
                # MC_DOUBLE  'radius'
                # WB_LERP_SIZE
                # MC_DOUBLE  'old_radius'
                # MC_DOUBLE  'new_radius'
                # MC_VARLONG 'speed'
                # WB_SET_CENTER
                # MC_DOUBLE  'x'
                # MC_DOUBLE  'z'
                # WB_INITIALIZE
                # MC_DOUBLE  'x'
                # MC_DOUBLE  'z'
                # MC_DOUBLE  'old_radius'
                # MC_DOUBLE  'new_radius'
                # MC_VARLONG 'speed'
                # MC_VARINT  'port_tele_bound' #Portal Teleport Boundary
                # MC_VARINT  'warn_time'
                # MC_VARINT  'warn_blocks'
                # WB_SET_WARN_TIME
                # MC_VARINT 'warn_time'
                # WB_SET_WARN_BLOCKS
                # MC_VARINT 'warn_blocks'
            ),
            # Camera
            0x36: (
                (MC_VARINT, 'camera_id'),
            ),
            # Held Item Change
            0x37: (
                (MC_BYTE, 'slot'),
            ),
            # Display Scoreboard
            0x38: (
                (MC_BYTE, 'position'),
                (MC_STRING, 'score_name'),
            ),
            # Entity Metadata
            0x39: (
                (MC_VARINT, 'eid'),
                (MC_META, 'metadata'),
            ),
            # Attach Entity
            0x3A: (
                (MC_INT, 'eid'),
                (MC_INT, 'holding_eid'),
            ),
            # Entity Velocity
            0x3B: (
                (MC_VARINT, 'eid'),
                (MC_SHORT, 'velocity_x'),
                (MC_SHORT, 'velocity_y'),
                (MC_SHORT, 'velocity_z'),
            ),
            # Entity Equipment
            0x3C: (
                (MC_VARINT, 'eid'),
                (MC_SHORT, 'slot'),
                (MC_SLOT, 'item'),
            ),
            # Set Experience
            0x3D: (
                (MC_FLOAT, 'exp_bar'),
                (MC_VARINT, 'level'),
                (MC_VARINT, 'total_exp'),
            ),
            # Update Health
            0x3E: (
                (MC_FLOAT, 'health'),
                (MC_VARINT, 'food'),
                (MC_FLOAT, 'saturation'),
            ),
            # Scoreboard Objective
            0x3F: (
                (MC_STRING, 'obj_name'),
                (MC_BYTE, 'action'),
                # Extension
                # SO_CREATE_BOARD
                # SO_UPDATE_BOARD
                # MC_STRING 'obj_val'
                # MC_STRING 'type'
            ),
            # Set Passengers
            0x40: (
                (MC_VARINT, 'eid'),
                # Extension
                # List of ints 'eids'
            ),
            # Teams
            0x41: (
                (MC_STRING, 'team_name'),
                (MC_BYTE, 'action'),
                # Extension
                # Depends on action
                # TE_CREATE_TEAM gets all fields
                # TE_UPDATE_TEAM
                # MC_STRING 'display_name'
                # MC_STRING 'team_prefix'
                # MC_STRING 'team_suffix'
                # MC_BYTE   'friendly_fire'
                # MC_STRING 'name_visibility'
                # MC_BYTE   'color'
                # TE_ADDPLY_TEAM
                # TE_REMPLY_TEAM
                # List of strings 'players'
            ),
            # Update Score
            0x42: (
                (MC_STRING, 'item_name'),
                (MC_BYTE, 'action'),
                (MC_STRING, 'score_name'),
                # Extension
                # US_UPDATE_SCORE
                # MC_VARINT 'value'
            ),
            # Spawn Position
            0x43: (
                (MC_POSITION, 'location'),
            ),
            # Time Update
            0x44: (
                (MC_LONG, 'world_age'),
                (MC_LONG, 'time_of_day'),
            ),
            # Title
            0x45: (
                (MC_VARINT, 'action'),
                # Extension
                # TL_TITLE
                # TL_SUBTITLE
                # MC_CHAT 'text'
                # TL_TIMES
                # MC_INT  'fade_in'
                # MC_INT  'stay'
                # MC_INT  'fade_out'
            ),
            # Update Sign
            0x46: (
                (MC_POSITION, 'location'),
                (MC_CHAT, 'line_1'),
                (MC_CHAT, 'line_2'),
                (MC_CHAT, 'line_3'),
                (MC_CHAT, 'line_4'),
            ),
            # Sound Effect
            0x47: (
                (MC_STRING, 'name'),
                (MC_INT, 'ef_x'),
                (MC_INT, 'ef_y'),
                (MC_INT, 'ef_z'),
                (MC_FLOAT, 'vol'),
                (MC_UBYTE, 'pitch'),
            ),
            # Player List Header/Footer
            0x48: (
                (MC_CHAT, 'header'),
                (MC_CHAT, 'footer'),
            ),
            # Collect Item
            0x49: (
                (MC_VARINT, 'collected_eid'),
                (MC_VARINT, 'collector_eid'),
            ),
            # Entity Teleport
            0x4A: (
                (MC_VARINT, 'eid'),
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BYTE, 'yaw'),
                (MC_BYTE, 'pitch'),
                (MC_BOOL, 'on_ground'),
            ),
            # Entity Properties
            0x4B: (
                (MC_VARINT, 'eid'),
                # Extension
                # List of dicts 'properties'
                # Entity properties are complex beasts
                # Consult the decoder to get all of the keys
            ),
            # Entity Effect
            0x4C: (
                (MC_VARINT, 'eid'),
                (MC_BYTE, 'effect'),
                (MC_BYTE, 'amplifier'),
                (MC_VARINT, 'duration'),
                (MC_BOOL, 'no_particles'),
            ),
        },

        CLIENT_TO_SERVER: {
            # Teleport Confirm
            0x00: (
                (MC_VARINT, 'teleport_id'),
            ),
            # Tab-Complete
            0x01: (
                (MC_STRING, 'text'),
                (MC_BOOL, 'has_position')
                # Extension
                # has_position == True
                # MC_POSITION 'block_loc'
            ),
            # Chat Message
            0x02: (
                (MC_STRING, 'message'),
            ),
            # Client Status
            0x03: (
                (MC_VARINT, 'action'),
            ),
            # Client Settings
            0x04: (
                (MC_STRING, 'locale'),
                (MC_BYTE, 'view_distance'),
                (MC_VARINT, 'chat_mode'),
                (MC_BOOL, 'chat_colors'),
                (MC_UBYTE, 'skin_flags'),
                (MC_VARINT, 'main_hand'),
            ),
            # Confirm Transaction
            0x05: (
                (MC_BYTE, 'window_id'),
                (MC_SHORT, 'action'),
                (MC_BOOL, 'accepted'),
            ),
            # Enchant Item
            0x06: (
                (MC_BYTE, 'window_id'),
                (MC_BYTE, 'enchantment'),
            ),
            # Click Window
            0x07: (
                (MC_BYTE, 'window_id'),
                (MC_SHORT, 'slot'),
                (MC_BYTE, 'button'),
                (MC_SHORT, 'action'),
                (MC_BYTE, 'mode'),
                (MC_SLOT, 'clicked_item'),
            ),
            # Close Window
            0x08: (
                (MC_BYTE, 'window_id'),
            ),
            # Plugin Message
            0x09: (
                (MC_STRING, 'channel'),
                # Extension
                # byte string 'data'
            ),
            # Use Entity
            0x0A: (
                (MC_VARINT, 'target'),
                (MC_VARINT, 'action'),
                # Extension
                # INTERACT_ENTITY_AT
                # MC_FLOAT 'target_x'
                # MC_FLOAT 'target_y'
                # MC_FLOAT 'target_z'
            ),
            # Keep Alive
            0x0B: (
                (MC_VARINT, 'keep_alive'),
            ),
            # Player Position
            0x0C: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BOOL, 'on_ground'),
            ),
            # Player Position and Look
            0x0D: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
                (MC_BOOL, 'on_ground'),
            ),
            # Player Look
            0x0E: (
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
                (MC_BOOL, 'on_ground'),
            ),
            # Player
            0x0F: (
                (MC_BOOL, 'on_ground'),
            ),
            # Vehicle Move
            0x10: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
            ),
            # Steer Boat
            0x11: (
                (MC_BOOL, 'right_paddle'),
                (MC_BOOL, 'left_paddle'),
            ),
            # Player Abilities
            0x12: (
                (MC_BYTE, 'flags'),
                (MC_FLOAT, 'flying_speed'),
                (MC_FLOAT, 'walking_speed'),
            ),
            # Player Digging
            0x13: (
                (MC_BYTE, 'status'),
                (MC_POSITION, 'location'),
                (MC_BYTE, 'face'),
            ),
            # Entity Action
            0x14: (
                (MC_VARINT, 'eid'),
                (MC_VARINT, 'action'),
                (MC_VARINT, 'jump_boost'),
            ),
            # Steer Vehicle
            0x15: (
                (MC_FLOAT, 'sideways'),
                (MC_FLOAT, 'forward'),
                (MC_UBYTE, 'flags'),
            ),
            # Resource Pack Status
            0x16: (
                (MC_STRING, 'hash'),
                (MC_VARINT, 'result'),
            ),
            # Held Item Change
            0x17: (
                (MC_SHORT, 'slot'),
            ),
            # Creative Inventory Action
            0x18: (
                (MC_SHORT, 'slot'),
                (MC_SLOT, 'clicked_item'),
            ),
            # Update Sign
            0x19: (
                (MC_POSITION, 'location'),
                (MC_CHAT, 'line_1'),
                (MC_CHAT, 'line_2'),
                (MC_CHAT, 'line_3'),
                (MC_CHAT, 'line_4'),
            ),
            # Animation
            0x1A: (
                (MC_VARINT, 'hand'),
            ),
            # Spectate
            0x1B: (
                (MC_UUID, 'target_player'),
            ),
            # Player Block Placement
            0x1C: (
                (MC_POSITION, 'location'),
                (MC_VARINT, 'direction'),
                (MC_VARINT, 'hand'),
                (MC_UBYTE, 'cur_pos_x'),
                (MC_UBYTE, 'cur_pos_y'),
                (MC_UBYTE, 'cur_pos_z'),
            ),
            # Use Item
            0x1D: (
                (MC_VARINT, 'hand'),
            ),
        },
    },
}

# Useful for some lookups
hashed_names = {
    (state, direction, packet_id):
        packet_names[state][direction][packet_id]
    for state in packet_names
    for direction in packet_names[state]
    for packet_id in packet_names[state][direction]
}
hashed_structs = {
    (state, direction, packet_id):
        packet_structs[state][direction][packet_id]
    for state in packet_structs
    for direction in packet_structs[state]
    for packet_id in packet_structs[state][direction]
}

state_lookup = 'HANDSHAKE', 'STATUS', 'LOGIN', 'PLAY'

packet_ident2str = {
    (state, direction, packet_id):
        state_lookup[state] + ('<', '>')[direction] +
        packet_names[state][direction][packet_id]
    for state in packet_structs
    for direction in packet_structs[state]
    for packet_id in packet_structs[state][direction]
}
packet_str2ident = {v: k for k, v in packet_ident2str.items()}

# Pack the protocol more efficiently
packet_names = tuple(
    tuple(packet_names[i][j] for j in (0, 1)) for i in (0, 1, 2, 3))
packet_structs = tuple(
    tuple(packet_structs[i][j] for j in (0, 1)) for i in (0, 1, 2, 3))
