#Most of the data formats, structures, and magic values

MC_PROTOCOL_VERSION = 47

SERVER_TO_CLIENT    = 0x00
CLIENT_TO_SERVER    = 0x01

PROTO_COMP_ON       = 0x00
PROTO_COMP_OFF      = 0x01

MC_BOOL             = 0x00
MC_UBYTE            = 0x01
MC_BYTE             = 0x02
MC_USHORT           = 0x03
MC_SHORT            = 0x04
MC_UINT             = 0x05
MC_INT              = 0x06
MC_ULONG            = 0x07
MC_LONG             = 0x08
MC_FLOAT            = 0x09
MC_DOUBLE           = 0x0A
MC_VARINT           = 0x0B
MC_VARLONG          = 0x0C
MC_FP_INT           = 0x0D
MC_FP_BYTE          = 0x0E
MC_UUID             = 0x0F
MC_POSITION         = 0x10
MC_STRING           = 0x11
MC_CHAT             = 0x12
MC_SLOT             = 0x13
MC_META             = 0x14

HANDSHAKE_STATE     = 0x00
STATUS_STATE        = 0x01
LOGIN_STATE         = 0x02
PLAY_STATE          = 0x03

SMP_NETHER          =-0x01
SMP_OVERWORLD       = 0x00
SMP_END             = 0x01

FLG_XPOS_REL        = 0x01
FLG_YPOS_REL        = 0x02
FLG_ZPOS_REL        = 0x04
FLG_YROT_REL        = 0x08
FLG_XROT_REL        = 0x10

GM_SURVIVAL         = 0x00
GM_CREATIVE         = 0x01
GM_ADVENTURE        = 0x02
GM_SPECTATOR        = 0x03

#Actions
#Clientbound 0x38 Player List Item
PL_ADD_PLAYER       = 0x00
PL_UPDATE_GAMEMODE  = 0x01
PL_UPDATE_LATENCY   = 0x02
PL_UPDATE_DISPLAY   = 0x03
PL_REMOVE_PLAYER    = 0x04

#Clientbound 0x3B Scoreboard Objective
SO_CREATE_BOARD     = 0x00
SO_REMOVE_BOARD     = 0x01
SO_UPDATE_BOARD     = 0x02

#Clientbound 0x3C Update Score
US_UPDATE_SCORE     = 0x00
US_REMOVE_SCORE     = 0x01

#Clientbound 0x3E Teams
TE_CREATE_TEAM      = 0x00
TE_REMOVE_TEAM      = 0x01
TE_UPDATE_TEAM      = 0x02
TE_ADDPLY_TEAM      = 0x03
TE_REMPLY_TEAM      = 0x04

#Clientbound 0x42 Combat Event
CE_ENTER_COMBAT     = 0x00
CE_END_COMBAT       = 0x01
CE_ENTITY_DEAD      = 0x02

#Clientbound 0x44 World Border
WB_SET_SIZE         = 0x00
WB_LERP_SIZE        = 0x01
WB_SET_CENTER       = 0x02
WB_INITIALIZE       = 0x03
WB_SET_WARN_TIME    = 0x04
WB_SET_WARN_BLOCKS  = 0x05

#Clientbound 0x45 Title
TL_TITLE            = 0x00
TL_SUBTITLE         = 0x01
TL_TIMES            = 0x02
TL_CLEAR            = 0x03
TL_RESET            = 0x04

#Serverbound 0x02 Use Entity
UE_INTERACT         = 0x00
UE_ATTACK           = 0x01
UE_INTERACT_AT      = 0x02

#Serverbound 0x16 Client Status
CL_STATUS_RESPAWN   = 0x00
CL_STATUS_STATS     = 0x01
CL_STATUS_INV       = 0x02

#Clientbound 0x2B Change Game State
GS_INVALID_BED      = 0x00
GS_END_RAIN         = 0x01
GS_START_RAIN       = 0x02
GS_GAMEMODE         = 0x03
GS_CREDITS          = 0x04
GS_DEMO_MESSAGE     = 0x05
GS_ARROW            = 0x06
GS_FADE_VALUE       = 0x07
GS_FADE_TIME        = 0x08

data_structs = (
    #(struct_suffix, size), #type
    ('?', 1), #bool
    ('B', 1), #ubyte
    ('b', 1), #byte
    ('H', 2), #ushort
    ('h', 2), #short
    ('I', 4), #uint
    ('i', 4), #int
    ('Q', 8), #ulong
    ('q', 8), #long
    ('f', 4), #float
    ('d', 8), #double
)

particles = (
    #(name, data_length)
    ('explosion_normal' , 0),
    ('explosion_large'  , 0),
    ('explosion_huge'   , 0),
    ('fireworks_spark'  , 0),
    ('water_bubble'     , 0),
    ('water_splash'     , 0),
    ('water_wake'       , 0),
    ('suspended'        , 0),
    ('suspended_depth'  , 0),
    ('crit'             , 0),
    ('crit_magic'       , 0),
    ('smoke_normal'     , 0),
    ('smoke_large'      , 0),
    ('spell'            , 0),
    ('spell_instant'    , 0),
    ('spell_mob'        , 0),
    ('spell_mob_ambient', 0),
    ('spell_witch'      , 0),
    ('drip_water'       , 0),
    ('drip_lava'        , 0),
    ('villager_angry'   , 0),
    ('villager_happy'   , 0),
    ('town_aura'        , 0),
    ('note'             , 0),
    ('portal'           , 0),
    ('enchantment_table', 0),
    ('flame'            , 0),
    ('lava'             , 0),
    ('footstep'         , 0),
    ('cloud'            , 0),
    ('redstone'         , 0),
    ('snowball'         , 0),
    ('snow_shovel'      , 0),
    ('slime'            , 0),
    ('heart'            , 0),
    ('barrier'          , 0),
    ('icon_crack'       , 2),
    ('block_crack'      , 1),
    ('block_dust'       , 1),
    ('water_drop'       , 0),
    ('item_take'        , 0),
    ('mob_appearance'   , 0),
)

#Structs formatted for readibility
#Packed into tuples at end of file
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
            0x00: 'Keep Alive',
            0x01: 'Join Game',
            0x02: 'Chat Message',
            0x03: 'Time Update',
            0x04: 'Entity Equipment',
            0x05: 'Spawn Position',
            0x06: 'Update Health',
            0x07: 'Respawn',
            0x08: 'Player Position and Look',
            0x09: 'Held Item Change',
            0x0A: 'Use Bed',
            0x0B: 'Animation',
            0x0C: 'Spawn Player',
            0x0D: 'Collect Item',
            0x0E: 'Spawn Object',
            0x0F: 'Spawn Mob',
            0x10: 'Spawn Painting',
            0x11: 'Spawn Experience Orb',
            0x12: 'Entity Velocity',
            0x13: 'Destroy Entities',
            0x14: 'Entity',
            0x15: 'Entity Relative Move',
            0x16: 'Entity Look',
            0x17: 'Entity Look and Relative Move',
            0x18: 'Entity Teleport',
            0x19: 'Entity Head Look',
            0x1A: 'Entity Status',
            0x1B: 'Attach Entity',
            0x1C: 'Entity Metadata',
            0x1D: 'Entity Effect',
            0x1E: 'Remove Entity Effect',
            0x1F: 'Set Experience',
            0x20: 'Entity Properties',
            0x21: 'Chunk Data',
            0x22: 'Multi Block Change',
            0x23: 'Block Change',
            0x24: 'Block Action',
            0x25: 'Block Break Animation',
            0x26: 'Map Chunk Bulk',
            0x27: 'Explosion',
            0x28: 'Effect',
            0x29: 'Sound Effect',
            0x2A: 'Particle',
            0x2B: 'Change Game State',
            0x2C: 'Spawn Global Entity',
            0x2D: 'Open Window',
            0x2E: 'Close Window',
            0x2F: 'Set Slot',
            0x30: 'Window Items',
            0x31: 'Window Property',
            0x32: 'Confirm Transaction',
            0x33: 'Update Sign',
            0x34: 'Maps',
            0x35: 'Update Block Entity',
            0x36: 'Sign Editor Open',
            0x37: 'Statistics',
            0x38: 'Player List Item',
            0x39: 'Player Abilities',
            0x3A: 'Tab-Complete',
            0x3B: 'Scoreboard Objective',
            0x3C: 'Update Score',
            0x3D: 'Display Scoreboard',
            0x3E: 'Teams',
            0x3F: 'Plugin Message',
            0x40: 'Disconnect',
            0x41: 'Server Difficulty',
            0x42: 'Combat Event',
            0x43: 'Camera',
            0x44: 'World Border',
            0x45: 'Title',
            0x46: 'Set Compression',
            0x47: 'Player List Header/Footer',
            0x48: 'Resource Pack Send',
            0x49: 'Update Entity NBT',
        },

        CLIENT_TO_SERVER: {
            0x00: 'Keep Alive',
            0x01: 'Chat Message',
            0x02: 'Use Entity',
            0x03: 'Player',
            0x04: 'Player Position',
            0x05: 'Player Look',
            0x06: 'Player Position and Look',
            0x07: 'Player Digging',
            0x08: 'Player Block Placement',
            0x09: 'Held Item Change',
            0x0A: 'Animation',
            0x0B: 'Entity Action',
            0x0C: 'Steer Vehicle',
            0x0D: 'Close Window',
            0x0E: 'Click Window',
            0x0F: 'Confirm Transaction',
            0x10: 'Creative Inventory Action',
            0x11: 'Enchant Item',
            0x12: 'Update Sign',
            0x13: 'Player Abilities',
            0x14: 'Tab-Complete',
            0x15: 'Client Settings',
            0x16: 'Client Status',
            0x17: 'Plugin Message',
            0x18: 'Spectate',
            0x19: 'Resource Pack Status',
        },
    },
}

packet_structs = {
    HANDSHAKE_STATE: {
        SERVER_TO_CLIENT: {
            #Empty, server doesn't handshake
        },
        CLIENT_TO_SERVER: {
            #Handshake
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
            #Status Response
            0x00: (
                (MC_STRING, 'response'),
            ),
            #Status Ping
            0x01: (
                (MC_LONG, 'time'),
            ),
        },
        CLIENT_TO_SERVER: {
            #Status Request
            0x00: (
                #Empty Packet
            ),
            #Status Ping
            0x01: (
                (MC_LONG, 'time'),
            ),
        },
    },

    LOGIN_STATE: {
        SERVER_TO_CLIENT: {
            #Disconnect
            0x00: (
                (MC_CHAT, 'json_data'),
            ),
            #Encryption Request
            0x01: (
                (MC_STRING, 'server_id'),
                #Extension
                    #byte string 'public_key'
                    #byte string 'verify_token'
            ),
            #Login Success
            0x02: (
                (MC_STRING, 'uuid'),
                (MC_STRING, 'username'),
            ),
            #Set Compression
            0x03: (
                (MC_VARINT, 'threshold'),
            ),
        },
        CLIENT_TO_SERVER: {
            #Login Start
            0x00: (
                (MC_STRING, 'name'),
            ),
            #Encryption Response
            0x01: (
                #Extension
                    #byte string 'shared_secret'
                    #byte string 'verify token'
            ),
        },
    },

    PLAY_STATE: {
        SERVER_TO_CLIENT: {
            #Keep Alive
            0x00: (
                (MC_VARINT, 'keep_alive'),
            ),
            #Join Game
            0x01: (
                (MC_INT   , 'eid'),
                (MC_UBYTE , 'gamemode'),
                (MC_BYTE  , 'dimension'),
                (MC_UBYTE , 'difficulty'),
                (MC_UBYTE , 'max_players'),
                (MC_STRING, 'level_type'),
                (MC_BOOL  , 'reduce_debug'),
            ),
            #Chat Message
            0x02: (
                (MC_CHAT, 'json_data'),
                (MC_BYTE, 'position'),
            ),
            #Time Update
            0x03: (
                (MC_LONG, 'world_age'),
                (MC_LONG, 'time_of_day'),
            ),
            #Entity Equipment
            0x04: (
                (MC_VARINT, 'eid'),
                (MC_SHORT , 'slot'),
                (MC_SLOT  , 'item'),
            ),
            #Spawn Position
            0x05: (
                (MC_POSITION, 'location'),
            ),
            #Update Health
            0x06: (
                (MC_FLOAT , 'health'),
                (MC_VARINT, 'food'),
                (MC_FLOAT , 'saturation'),
            ),
            #Respawn
            0x07: (
                (MC_INT   , 'dimension'),
                (MC_UBYTE , 'difficulty'),
                (MC_UBYTE , 'gamemode'),
                (MC_STRING, 'level_type'),
            ),
            #Player Position and Look
            0x08: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT , 'yaw'),
                (MC_FLOAT , 'pitch'),
                (MC_BYTE  , 'flags'),
            ),
            #Held Item Change
            0x09: (
                (MC_BYTE, 'slot'),
            ),
            #Use Bed
            0x0A: (
                (MC_INT     , 'eid'),
                (MC_POSITION, 'location'),
            ),
            #Animation
            0x0B: (
                (MC_VARINT, 'eid'),
                (MC_UBYTE , 'animation'),
            ),
            #Spawn Player
            0x0C: (
                (MC_VARINT, 'eid'),
                (MC_UUID  , 'uuid'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
                (MC_BYTE  , 'yaw'),
                (MC_BYTE  , 'pitch'),
                (MC_SHORT , 'current_item'),
                (MC_META  , 'metadata'),
            ),
            #Collect Item
            0x0D: (
                (MC_VARINT, 'collected_eid'),
                (MC_VARINT, 'collector_eid'),
            ),
            #Spawn Object
            0x0E: (
                (MC_VARINT, 'eid'),
                (MC_UBYTE , 'obj_type'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
                (MC_BYTE  , 'pitch'),
                (MC_BYTE  , 'yaw'),
                (MC_INT   , 'obj_data'),
                #Extension
                    #If obj_data != 0
                    #short 'speed_x'
                    #short 'speed_y'
                    #short 'speed_z'
            ),
            #Spawn Mob
            0x0F: (
                (MC_VARINT, 'eid'),
                (MC_UBYTE , 'type'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
                (MC_BYTE  , 'pitch'),
                (MC_BYTE  , 'head_pitch'),
                (MC_BYTE  , 'yaw'),
                (MC_SHORT , 'velocity_x'),
                (MC_SHORT , 'velocity_y'),
                (MC_SHORT , 'velocity_z'),
                (MC_META  , 'metadata'),
            ),
            #Spawn Painting
            0x10: (
                (MC_VARINT  , 'eid'),
                (MC_STRING  , 'title'),
                (MC_POSITION, 'location'),
                (MC_UBYTE   , 'direction'),
            ),
            #Spawn Experience Orb
            0x11: (
                (MC_VARINT, 'eid'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
                (MC_SHORT , 'count'),
            ),
            #Entity Velocity
            0x12: (
                (MC_VARINT, 'eid'),
                (MC_SHORT , 'velocity_x'),
                (MC_SHORT , 'velocity_y'),
                (MC_SHORT , 'velocity_z'),
            ),
            #Destroy Entities
            0x13: (
                #Extension
                    #List of ints 'eids'
            ),
            #Entity
            0x14: (
                (MC_VARINT, 'eid'),
            ),
            #Entity Relative Move
            0x15: (
                (MC_VARINT , 'eid'),
                (MC_FP_BYTE, 'dx'),
                (MC_FP_BYTE, 'dy'),
                (MC_FP_BYTE, 'dz'),
                (MC_BOOL   , 'on_ground'),
            ),
            #Entity Look
            0x16: (
                (MC_VARINT, 'eid'),
                (MC_BYTE  , 'yaw'),
                (MC_BYTE  , 'pitch'),
                (MC_BOOL  , 'on_ground'),
            ),
            #Entity Look and Relative Move
            0x17: (
                (MC_VARINT , 'eid'),
                (MC_FP_BYTE, 'dx'),
                (MC_FP_BYTE, 'dy'),
                (MC_FP_BYTE, 'dz'),
                (MC_BYTE   , 'yaw'),
                (MC_BYTE   , 'pitch'),
                (MC_BOOL   , 'on_ground'),
            ),
            #Entity Teleport
            0x18: (
                (MC_VARINT, 'eid'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
                (MC_BYTE  , 'yaw'),
                (MC_BYTE  , 'pitch'),
                (MC_BOOL  , 'on_ground'),
            ),
            #Entity Head Look
            0x19: (
                (MC_VARINT, 'eid'),
                (MC_BYTE  , 'head_yaw'),
            ),
            #Entity Status
            0x1A: (
                (MC_INT , 'eid'),
                (MC_BYTE, 'status')
            ),
            #Attach Entity
            0x1B: (
                (MC_INT , 'eid'),
                (MC_INT , 'v_eid'),
                (MC_BOOL, 'leash'),
            ),
            #Entity Metadata
            0x1C: (
                (MC_VARINT, 'eid'),
                (MC_META  , 'metadata'),
            ),
            #Entity Effect
            0x1D: (
                (MC_VARINT, 'eid'),
                (MC_BYTE  , 'effect'),
                (MC_BYTE  , 'amplifier'),
                (MC_VARINT, 'duration'),
                (MC_BOOL  , 'no_particles'),
            ),
            #Remove Entity Effect
            0x1E: (
                (MC_VARINT, 'eid'),
                (MC_BYTE  , 'effect'),
            ),
            #Set Experience
            0x1F: (
                (MC_FLOAT , 'exp_bar'),
                (MC_VARINT, 'level'),
                (MC_VARINT, 'total_exp'),
            ),
            #Entity Properties
            0x20: (
                (MC_VARINT, 'eid'),
                #Extension
                    #List of dicts 'properties'
                    #Entity properties are complex beasts
                    #Consult the decoder to get all of the keys
            ),
            #Chunk Data
            0x21: (
                (MC_INT   , 'chunk_x'),
                (MC_INT   , 'chunk_z'),
                (MC_BOOL  , 'continuous'),
                (MC_USHORT, 'primary_bitmap'),
                #Extension
                    #byte string 'data'
            ),
            #Multi Block Change
            0x22: (
                (MC_INT  , 'chunk_x'),
                (MC_INT  , 'chunk_z'),
                #Extension
                    #List of dicts 'blocks'
            ),
            #Block Change
            0x23: (
                (MC_POSITION, 'location'),
                (MC_VARINT  , 'block_data'),
            ),
            #Block Action
            0x24: (
                (MC_POSITION, 'location'),
                (MC_UBYTE   , 'byte_1'),
                (MC_UBYTE   , 'byte_2'),
                (MC_VARINT  , 'block_id'),
            ),
            #Block Break Animation
            0x25: (
                (MC_VARINT  , 'eid'),
                (MC_POSITION, 'location'),
                (MC_BYTE    , 'stage'),
            ),
            #Map Chunk Bulk
            0x26: (
                #Extension
                    #bool 'sky_light'
                    #List of dicts 'metadata'
                    #byte string 'data'
                    #Metadata is identical to 0x21
                    #But the 'continuous' bool is assumed True
            ),
            #Explosion
            0x27: (
                (MC_FLOAT, 'x'),
                (MC_FLOAT, 'y'),
                (MC_FLOAT, 'z'),
                (MC_FLOAT, 'radius'),
                #Extension
                    #List of lists 'blocks'
                    #Each list is 3 ints x,y,z
                    #float 'player_x'
                    #float 'player_y'
                    #float 'player_z'
            ),
            #Effect
            0x28: (
                (MC_INT     , 'effect'),
                (MC_POSITION, 'location'),
                (MC_INT     , 'data'),
                (MC_BOOL    , 'no_rel_vol'),
            ),
            #Sound Effect
            0x29: (
                (MC_STRING, 'name'),
                (MC_INT   , 'ef_x'),
                (MC_INT   , 'ef_y'),
                (MC_INT   , 'ef_z'),
                (MC_FLOAT , 'vol'),
                (MC_UBYTE , 'pitch'),
            ),
            #Particle
            0x2A: (
                (MC_INT   , 'id'),
                (MC_BOOL  , 'long_dist'),
                (MC_FLOAT , 'x'),
                (MC_FLOAT , 'y'),
                (MC_FLOAT , 'z'),
                (MC_FLOAT , 'off_x'),
                (MC_FLOAT , 'off_y'),
                (MC_FLOAT , 'off_z'),
                (MC_FLOAT , 'speed'),
                (MC_INT   , 'num'),
                #Extension
                    #List of ints 'data'
                    #Possibly zero length list of
                    #particle-dependent data
            ),
            #Change Game State
            0x2B: (
                (MC_UBYTE, 'reason'),
                (MC_FLOAT, 'value'),
            ),
            #Spawn Global Entity
            0x2C: (
                (MC_VARINT, 'eid'),
                (MC_BYTE  , 'type'),
                (MC_FP_INT, 'x'),
                (MC_FP_INT, 'y'),
                (MC_FP_INT, 'z'),
            ),
            #Open Window
            0x2D: (
                (MC_UBYTE , 'window_id'),
                (MC_STRING, 'inv_type'),
                (MC_CHAT  , 'title'),
                (MC_UBYTE , 'slot_count'),
                #Extension
                    #Only present if 'inv_type' == 'EntityHorse'
                    #MC_INT 'eid'
            ),
            #Close Window
            0x2E: (
                (MC_UBYTE, 'window_id'),
            ),
            #Set Slot
            0x2F: (
                (MC_BYTE , 'window_id'),
                (MC_SHORT, 'slot'),
                (MC_SLOT , 'slot_data'),
            ),
            #Window Items
            0x30: (
                (MC_UBYTE, 'window_id'),
                #Extension
                    #List of slots 'slots'
            ),
            #Window Property
            0x31: (
                (MC_UBYTE, 'window_id'),
                (MC_SHORT, 'property'),
                (MC_SHORT, 'value'),
            ),
            #Confirm Transaction
            0x32: (
                (MC_UBYTE, 'window_id'),
                (MC_SHORT, 'action'),
                (MC_BOOL , 'accepted'),
            ),
            #Update Sign
            0x33: (
                (MC_POSITION, 'location'),
                (MC_CHAT    , 'line_1'),
                (MC_CHAT    , 'line_2'),
                (MC_CHAT    , 'line_3'),
                (MC_CHAT    , 'line_4'),
            ),
            #Maps
            0x34: (
                (MC_VARINT, 'item_damage'),
                (MC_BYTE  , 'scale'),
                #Extension
                    #List of tuples 'icons', (Direction, Type, X, Y)
                    #MC_BYTE 'columns'
                    #If Columns > 0
                        #MC_BYTE 'rows'
                        #MC_BYTE 'x'
                        #MC_BYTE 'y'
                        #byte string 'data'
            ),
            #Update Block Entity
            0x35: (
                (MC_POSITION, 'location'),
                (MC_UBYTE   , 'action'),
                #Extension
                    #NBT Data 'nbt'
            ),
            #Sign Editor Open
            0x36: (
                (MC_POSITION, 'location'),
            ),
            #Statistics
            0x37: (
                #Extension
                    #List of lists 'entries'
                    #First value is a string, stat's name
                    #Second value is an int, stat's value
            ),
            #Player List Item
            0x38: (
                (MC_VARINT, 'action'),
                #Extension
                #List of dicts 'player_list'
                    #MC_UUID 'uuid'
                    #PL_ADD_PLAYER
                        #MC_STRING 'name'
                        #List of dicts, 'properties'
                            #MC_STRING 'name'
                            #MC_STRING 'value'
                            #MC_BOOL   'signed'
                            #signed == True
                                #MC_STRING 'signature'
                        #MC_VARINT 'gamemode'
                        #MC_VARINT 'ping'
                        #MC_BOOL   'has_display'
                        #has_display == True
                            #MC_CHAT 'display_name'
                    #PL_UPDATE_GAMEMODE
                        #MC_VARINT 'gamemode'
                    #PL_UPDATE_LATENCY
                        #MC_VARINT 'ping'
                    #PL_UPDATE_DISPLAY
                        #MC_BOOL 'has_display'
                        #has_display == True
                            #MC_CHAT 'display_name'
                    #PL_REMOVE_PLAYER
                        #No extra fields
            ),
            #Player Abilities
            0x39: (
                (MC_BYTE , 'flags'),
                (MC_FLOAT, 'flying_speed'),
                (MC_FLOAT, 'walking_speed'),
            ),
            #Tab-Complete
            0x3A: (
                #Extension
                    #List of strings 'matches'
            ),
            #Scoreboard Objective
            0x3B: (
                (MC_STRING, 'obj_name'),
                (MC_BYTE  , 'action'),
                #Extension
                    #SO_CREATE_BOARD
                    #SO_UPDATE_BOARD
                        #MC_STRING 'obj_val'
                        #MC_STRING 'type'
            ),
            #Update Score
            0x3C: (
                (MC_STRING, 'item_name'),
                (MC_BYTE  , 'action'),
                (MC_STRING, 'score_name'),
                #Extension
                    #US_UPDATE_SCORE
                        #MC_VARINT 'value'
            ),
            #Display Scoreboard
            0x3D: (
                (MC_BYTE  , 'position'),
                (MC_STRING, 'score_name'),
            ),
            #Teams
            0x3E: (
                (MC_STRING, 'team_name'),
                (MC_BYTE  , 'action'),
                #Extension
                    #Depends on action
                    #TE_CREATE_TEAM gets all fields
                    #TE_UPDATE_TEAM
                        #MC_STRING 'display_name'
                        #MC_STRING 'team_prefix'
                        #MC_STRING 'team_suffix'
                        #MC_BYTE   'friendly_fire'
                        #MC_STRING 'name_visibility'
                        #MC_BYTE   'color'
                    #TE_ADDPLY_TEAM
                    #TE_REMPLY_TEAM
                        # List of strings 'players'
            ),
            #Plugin Message
            0x3F: (
                (MC_STRING, 'channel'),
                #Extension
                    #byte string 'data'
            ),
            #Disconnect
            0x40: (
                (MC_STRING, 'reason'),
            ),
            #Server Difficulty
            0x41: (
                (MC_UBYTE, 'difficulty'),
            ),
            #Combat Event
            0x42: (
                (MC_VARINT, 'event'),
                #Extension
                    #CE_END_COMBAT
                        #MC_VARINT 'duration'
                        #MC_INT    'eid'
                    #CE_ENTITY_DEAD
                        #MC_VARINT 'player_id'
                        #MC_INT    'eid'
                        #MC_STRING 'message'
            ),
            #Camera
            0x43: (
                (MC_VARINT, 'camera_id'),
            ),
            #World Border
            0x44: (
                (MC_VARINT, 'action'),
                #Extension
                    #WB_SET_SIZE
                        #MC_DOUBLE  'radius'
                    #WB_LERP_SIZE
                        #MC_DOUBLE  'old_radius'
                        #MC_DOUBLE  'new_radius'
                        #MC_VARLONG 'speed'
                    #WB_SET_CENTER
                        #MC_DOUBLE  'x'
                        #MC_DOUBLE  'z'
                    #WB_INITIALIZE
                        #MC_DOUBLE  'x'
                        #MC_DOUBLE  'z'
                        #MC_DOUBLE  'old_radius'
                        #MC_DOUBLE  'new_radius'
                        #MC_VARLONG 'speed'
                        #MC_VARINT  'port_tele_bound' #Portal Teleport Boundary
                        #MC_VARINT  'warn_time'
                        #MC_VARINT  'warn_blocks'
                    #WB_SET_WARN_TIME
                        #MC_VARINT 'warn_time'
                    #WB_SET_WARN_BLOCKS
                        #MC_VARINT 'warn_blocks'
            ),
            #Title
            0x45: (
                (MC_VARINT, 'action'),
                #Extension
                    #TL_TITLE
                    #TL_SUBTITLE
                        #MC_CHAT 'text'
                    #TL_TIMES
                        #MC_INT  'fade_in'
                        #MC_INT  'stay'
                        #MC_INT  'fade_out'
            ),
            #Set Compression
            0x46: (
                (MC_VARINT, 'threshold'),
            ),
            #Play List Header/Footer
            0x47: (
                (MC_CHAT, 'header'),
                (MC_CHAT, 'footer'),
            ),
            #Resource Pack Send
            0x48: (
                (MC_STRING, 'url'),
                (MC_STRING, 'hash'),
            ),
            #Update Entity NBT
            0x49: (
                (MC_VARINT, 'eid'),
                #Extension
                    #NBT Data 'nbt'
            ),
        },

        CLIENT_TO_SERVER: {
            #Keep Alive
            0x00: (
                (MC_VARINT, 'keep_alive'),
            ),
            #Chat Message
            0x01: (
                (MC_STRING, 'message'),
            ),
            #Use Entity
            0x02: (
                (MC_VARINT, 'target'),
                (MC_VARINT, 'action'),
                #Extension
                    #UE_INTERACT_AT
                        #MC_FLOAT 'target_x'
                        #MC_FLOAT 'target_y'
                        #MC_FLOAT 'target_z'
            ),
            #Player
            0x03: (
                (MC_BOOL, 'on_ground'),
            ),
            #Player Position
            0x04: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_BOOL  , 'on_ground'),
            ),
            #Player Look
            0x05: (
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
                (MC_BOOL , 'on_ground'),
            ),
            #Player Position and Look
            0x06: (
                (MC_DOUBLE, 'x'),
                (MC_DOUBLE, 'y'),
                (MC_DOUBLE, 'z'),
                (MC_FLOAT, 'yaw'),
                (MC_FLOAT, 'pitch'),
                (MC_BOOL , 'on_ground'),
            ),
            #Player Digging
            0x07: (
                (MC_BYTE    , 'status'),
                (MC_POSITION, 'location'),
                (MC_BYTE    , 'face'),
            ),
            #Player Block Placement
            0x08: (
                (MC_POSITION, 'location'),
                (MC_BYTE    , 'direction'),
                (MC_SLOT    , 'held_item'),
                (MC_BYTE    , 'cur_pos_x'),
                (MC_BYTE    , 'cur_pos_y'),
                (MC_BYTE    , 'cur_pos_z'),
            ),
            #Held Item Change
            0x09: (
                (MC_SHORT, 'slot'),
            ),
            #Animation
            0x0A: (
                #Empty Packet
            ),
            #Entity Action
            0x0B: (
                (MC_VARINT, 'eid'),
                (MC_VARINT, 'action'),
                (MC_VARINT, 'jump_boost'),
            ),
            #Steer Vehicle
            0x0C: (
                (MC_FLOAT, 'sideways'),
                (MC_FLOAT, 'forward'),
                (MC_UBYTE, 'flags'),
            ),
            #Close Window
            0x0D: (
                (MC_BYTE, 'window_id'),
            ),
            #Click Window
            0x0E: (
                (MC_BYTE , 'window_id'),
                (MC_SHORT, 'slot'),
                (MC_BYTE , 'button'),
                (MC_SHORT, 'action'),
                (MC_BYTE , 'mode'),
                (MC_SLOT , 'clicked_item'),
            ),
            #Confirm Transaction
            0x0F: (
                (MC_BYTE , 'window_id'),
                (MC_SHORT, 'action'),
                (MC_BOOL , 'accepted'),
            ),
            #Creative Inventory Action
            0x10: (
                (MC_SHORT, 'slot'),
                (MC_SLOT , 'clicked_item'),
            ),
            #Enchant Item
            0x11: (
                (MC_BYTE, 'window_id'),
                (MC_BYTE, 'enchantment'),
            ),
            #Update Sign
            0x12: (
                (MC_POSITION, 'location'),
                (MC_CHAT    , 'line_1'),
                (MC_CHAT    , 'line_2'),
                (MC_CHAT    , 'line_3'),
                (MC_CHAT    , 'line_4'),
            ),
            #Player Abilities
            0x13: (
                (MC_BYTE , 'flags'),
                (MC_FLOAT, 'flying_speed'),
                (MC_FLOAT, 'walking_speed'),
            ),
            #Tab-Complete
            0x14: (
                (MC_STRING, 'text'),
                (MC_BOOL  , 'has_position')
                #Extension
                    #has_position == True
                        #MC_POSITION 'block_loc'
            ),
            #Client Settings
            0x15: (
                (MC_STRING, 'locale'),
                (MC_BYTE  , 'view_distance'),
                (MC_BYTE  , 'chat_flags'),
                (MC_BOOL  , 'chat_colours'),
                (MC_UBYTE , 'skin_flags'),
            ),
            #Client Status
            0x16: (
                (MC_VARINT, 'action'),
            ),
            #Plugin Message
            0x17: (
                (MC_STRING, 'channel'),
                #Extension
                    #byte string 'data'
            ),
            #Spectate
            0x18: (
                (MC_UUID, 'target_player'),
            ),
            #Resource Pack Status
            0x19: (
                (MC_STRING, 'hash'),
                (MC_VARINT, 'result'),
            ),
        },
    },
}

#Useful for some lookups
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
    state_lookup[state] + ('<', '>')[direction] + packet_names[state][direction][packet_id]
    for state in packet_structs
    for direction in packet_structs[state]
    for packet_id in packet_structs[state][direction]
}
packet_str2ident = {v: k for k, v in packet_ident2str.items()}

#Pack the protocol more efficiently
packet_names = tuple(tuple(packet_names[i][j] for j in (0,1)) for i in (0,1,2,3))
packet_structs = tuple(tuple(packet_structs[i][j] for j in (0,1)) for i in (0,1,2,3))
