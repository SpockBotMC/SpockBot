#Most of the data formats, structures, and magic values

SERVER_TO_CLIENT = 0x01
CLIENT_TO_SERVER = 0x02
SERVER_LIST_PING_MAGIC = 0x01

data_types = {
	"bool": ('?', 1),
	"ubyte": ('B', 1),
	"byte": ('b', 1),
	"ushort": ('H', 2),
	"short": ('h', 2),
	"uint": ('I', 4),
	"int": ('i', 4),
	"long": ('q', 8),
	"float": ('f', 4),
	"double": ('d', 8),
}

slot = (
	("short", "block_id"),
	("byte", "item_count"),
	("short", "item_damage"),
	("short", "nbt_data_length"),
	("nbt", "nbt_data"),
)

names = {
	0x00: "Keep Alive",
	0x01: "Login Request",
	0x02: "Handshake",
	0x03: "Chat Message",
	0x04: "Time Update",
	0x05: "Entity Equipment",
	0x06: "Spawn Position",
	0x07: "Use Entity",
	0x08: "Update Health",
	0x09: "Respawn",
	0x0A: "Player",
	0x0B: "Player Position",
	0x0C: "Player Look",
	0x0D: "Player Position and Look",
	0x0E: "Player Digging",
	0x0F: "Player Block Placement",
	0x10: "Held Item Change",
	0x11: "Use Bed",
	0x12: "Animation",
	0x13: "Entity Action",
	0x14: "Named Entity Spawn",
	0x15: "Spawn Dropped Item",
	0x16: "Collect item",
	0x17: "Spawn Object/Vehicle",
	0x18: "Spawn Mob",
	0x19: "Spawn Painting",
	0x1A: "Spawn Experience Orb",
	0x1C: "Entity Velocity",
	0x1D: "Destroy Entity",
	0x1E: "Entity",
	0x1F: "Entity Relative Move",
	0x20: "Entity Look",
	0x21: "Entity Look And Relative Move",
	0x22: "Entity Teleport",
	0x23: "Entity Head Look",
	0x26: "Entity Status",
	0x27: "Attach Entity",
	0x28: "Entity Metadata",
	0x29: "Entity Effect",
	0x2A: "Remove Entity Effect",
	0x2B: "Set Experience",
	0x33: "Chunk Data",
	0x34: "Multi Block Change",
	0x35: "Block Change",
	0x36: "Block Action",
	0x37: "Block Break Animation",
	0x38: "Map Chunk Bulk",
	0x3C: "Explosion",
	0x3D: "Sound Or Particle Effect",
	0x3E: "Named Sound Effect",
	0x46: "Changed Game State",
	0x47: "Global Entity",
	0x64: "Open Window",
	0x65: "Close Window",
	0x66: "Window Click",
	0x67: "Set Slot",
	0x68: "Set Window Items",
	0x69: "Update Window Property",
	0x6A: "Confirm Transaction",
	0x6B: "Creative Inventory Action",
	0x6C: "Enchant Item",
	0x82: "Update Sign",
	0x83: "Item Data",
	0x84: "Update Tile Entity",
	0xC8: "Increment Statistic",
	0xC9: "Player List Item",
	0xCA: "Player Abilities",
	0xCB: "Tab-complete",
	0xCC: "Client Settings",
	0xCD: "Client Statuses",
	0xFA: "Plugin Message",
	0xFC: "Encryption Key Response",
	0xFD: "Encryption Key Request",
	0xFE: "Server List Ping",
	0xFF: "Disconnect",
}

structs = {
	#Keep Alive
	0x00: ("int", "keep_alive_id"),
	#Login Request
	0x01: (
		("int", "entity_id"),
		("string", "level_type"),
		("byte", "game_mode"),
		("byte", "dimension"),
		("byte", "difficulty"),
		("byte", "not_used"),
		("byte", "max_players"),
		),
	#Handshake
	0x02: (
		("byte", "protocol_version"),
		("string", "username"),
		("string", "server_host"),
		("int", "server_port"),
		),
	#Chat Message
	0x03: ("string", "message"),
	#Time Update
	0x04: (
		("long", "age_of_the_world"),
		("long", "time_of_day"),
		),
	#Entity Equipment
	0x05: (
		("int", "entity_id"),
		("short", "slot"),
		("slot", "item"),
		),
	#Spawn Position
	0x06: (
		("int", "x"),
		("int", "y"),
		("int", "z"),
		),
	#Use Entity
	0x07: (
		("int", "user"),
		("int", "target"),
		("bool", "mouse_button"),
		),
	#Update Health
	0x08: (
		("short", "health"),
		("short", "food"),
		("float", "food_saturation"),
		),
	#Respawn
	0x09: (
		("int", "dimension"),
		("byte", "difficulty"),
		("byte", "game_mode"),
		("short", "world_height"),
		("string", "level_type"),
		),
	#Player
	0x0A: ("bool", "on_ground"),
	#Player Position
	0x0B: (
		("double", "x"),
		("double", "y"),
		("double", "stance"),
		("double", "z"),
		("bool", "on_ground"),
		),
	#Player Look
	0x0C: (
		("float", "yaw"),
		("float", "pitch"),
		("bool", "on_ground"),
		),
	#Player Position and Look
	0x0D: {
		CLIENT_TO_SERVER: (
			("double", "x"),
			("double", "y"),
			("double", "stance"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground"),
			),
		SERVER_TO_CLIENT: (
			("double", "x"),
			("double", "stance"),
			("double", "y"),
			("double", "z"),
			("float", "yaw"),
			("float", "pitch"),
			("bool", "on_ground"),
			),
		},
	#Player Digging
	0x0E: (
		("byte", "status"),
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("byte", "face"),
		),
	#Player Block Placement
	0x0F: (
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		("byte", "direction"),
		("slot", "held_item"),
		("byte", "cursor_position_x"),
		("byte", "cursor_position_y"),
		("byte", "cursor_position_z"),
		),
	#Held Item Change
	0x10: ("short", "slot_id"),
	#Use Bed
	0x11: (
		("int", "entity_id"),
		("byte", "unknown"),
		("int", "x"),
		("ubyte", "y"),
		("int", "z"),
		),
	#Animation
	0x12: (
		("int", "entity_id"),
		("byte", "animation"),
		),
	#Entity Action
	0x13: (
		("int", "entity_id"),
		("byte", "action_id"),
		),
	#Spawn Named Entity
	0x14: (
		("int", "entity_id"),
		("string", "player_name"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("short", "current_item"),
		("metadata", "metadata"),
		),
	#Spawn Dropped Item - obsolete?
	0x15: (
		("int", "entity_id"),
		("slot", "slot"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "rotation"),
		("byte", "pitch"),
		("byte", "roll"),
		),
	#Collect Item
	0x16: (
		("int", "collected_entity_id"),
		("int", "collector_entity_id"),
		),
	#Spawn Object/Vehicle
	0x17: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("object_data", "object_data"),
		),
	#Spawn Mob
	0x18: (
		("int", "entity_id"),
		("byte", "type"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		("byte", "head_yaw"),
		("short", "velocity_z"),
		("short", "velocity_x"),
		("short", "velocity_y"),
		("metadata", "metadata"),
		),
	#Spawn Painting
	0x19: (
		("int", "entity_id"),
		("string", "title"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("int", "direction"),
		),
	#Spawn Experience Orb
	0x1A: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("short", "count"),
		),
	#Entity Velocity
	0x1C: (
		("int", "entity_id"),
		("short", "x_velocity"),
		("short", "y_velocity"),
		("short", "z_velocity"),
		),
	#Destroy Entity
	0x1D: (
		("byte", "entity_count"),
		("int", "entity_id"),
		),
	#Entity
	0x1E: ("int", "entity_id"),
	#Entity Relative Move
	0x1F: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change"),
		),
	#Entity Look
	0x20: (
		("int", "entity_id"),
		("byte", "yaw"),
		("byte", "pitch"),
		),
	#Entity Look and Relative Move
	0x21: (
		("int", "entity_id"),
		("byte", "x_change"),
		("byte", "y_change"),
		("byte", "z_change"),
		("byte", "yaw"),
		("byte", "pitch"),
		),
	#Entity Teleport
	0x22: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "yaw"),
		("byte", "pitch"),
		),
	#Entity Head Look
	0x23: (
		("int", "entity_id"),
		("byte", "head_yaw"),
		),
	#Entity Status
	0x26: (
		("int", "entity_id"),
		("byte", "entity_status"),
		),
	#Attach Entity
	0x27: (
		("int", "entity_id"),
		("int", "vehicle_id"),
		),
	#Entity Metadata
	0x28: (
		("int", "entity_id"),
		("metadata", "metadata"),
		),
	#Entity Effect
	0x29: (
		("int", "entity_id"),
		("byte", "effect_id"),
		("byte", "amplifier"),
		("short", "duration"),
		),
	#Remove Entity Effect
	0x2a: (
		("int", "entity_id"),
		("byte", "effect_id"),
		),
	#Set Experience
	0x2b: (
		("float", "experience_bar"),
		("short", "level"),
		("short", "total_experience"),
		),
	#Chunk Data
	0x33: (
		("int", "x_chunk"),
		("int", "z_chunk"),
		("bool", "ground_up_continuous"),
		("ushort", "primary_bitmap"),
		("ushort", "add_bitmap"),
		("int", "compressed_size"),
		("byte_array", "compressed_data"),
		),
	#Multi Block Change
	0x34: (
		("int", "x_chunk"),
		("int", "z_chunk"),
		("short", "record_count"),
		("int", "data_length"),
		("byte_array", "data"),
		),
	#Block Change
	0x35: (
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("short", "block_type"),
		("byte", "block_metadata"),
		),
	#Block Action
	0x36: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "byte_1"),
		("byte", "byte_2"),
		("short", "block_id"),
		),
	#Block Break Animation
	0x37: (
		("int", "entity_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		("byte", "destroy_stage"),
		),
	#Map Chunk Bulk
	0x38: (
		("short", "chunk_count"),
		("int", "chunk_data_length"),
		("bool", "sky_light_sent"),
		("byte_array", "chunk_data"),
		("chunk_meta", "meta_information"),
		),
	#Explosion
	0x3C: (
		("double", "x"),
		("double", "y"),
		("double", "z"),
		("float", "radius"),
		("int", "record_count"),
		("record", "records"),
		("float", "player_motion_x"),
		("float", "player_motion_y"),
		("float", "player_motion_z"),
		),
	#Sound or Particle Effect
	0x3D: (
		("int", "effect_id"),
		("int", "x"),
		("byte", "y"),
		("int", "z"),
		("int", "data"),
		("bool", "no_volume_decrease"),
		),
	#Named Sound Effect
	0x3E: (
		("string", "sound_name"),
		("int", "effect_position_x"),
		("int", "effect_position_y"),
		("int", "effect_position_z"),
		("float", "volume"),
		("byte", "pitch"),
		),
	#Change Game State
	0x46: (
		("byte", "reason"),
		("byte", "game_mode"),
		),
	#Global Entity
	0x47: (
		("int", "entity_id"),
		("byte", "global_id"),
		("int", "x"),
		("int", "y"),
		("int", "z"),
		),
	#Open Window
	0x64: (
		("byte", "window_id"),
		("byte", "inventory_type"),
		("string", "window_title"),
		("byte", "slots_count"),
		),
	#Close Window
	0x65: ("byte", "window_id"),
	#Click Window
	0x66: (
		("byte", "window_id"),
		("short", "slot"),
		("byte", "right_click"),
		("short", "transaction_id"),
		("bool", "shift"),
		("slot", "clicked_item"),
		),
	#Set Slot
	0x67: (
		("byte", "window_id"),
		("short", "slot"),
		("slot", "slot_data"),
		),
	#Set Window Items
	0x68: (
		("byte", "window_id"),
		("short", "count"),
		("slot",   "slot_data"),
		),
	#Update Window Property
	0x69: (
		("byte", "window_id"),
		("short", "property"),
		("short", "value"),
		),
	#Confirm Transaction
	0x6A: (
		("byte", "window_id"),
		("short", "transaction_id"),
		("bool", "accepted"),
		),
	#Creative Inventory Action
	0x6B: (
		("short", "slot"),
		("slot", "slot_data")
		),
	#Enchant Item
	0x6C: (
		("byte", "window_id"),
		("byte", "enchantment"),
		),
	#Update Sign
	0x82: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("string", "line_1"),
		("string", "line_2"),
		("string", "line_3"),
		("string", "line_4"),
		),
	#Item Data
	0x83: (
		("short", "item_type"),
		("short", "item_id"),
		("short", "text_length"),
		("byte_array", "text"),
		),
	#Update Tile Entity
	0x84: (
		("int", "x"),
		("short", "y"),
		("int", "z"),
		("byte", "action"),
		("short", "nbt_data_length"),
		("nbt", "nbt_data"),
		),
	#Increment Statistic
	0xC8: (
		("int", "statistic_id"),
		("byte", "amount"),
		),
	#Player List Item
	0xC9: (
		("string", "player_name"),
		("bool", "online"),
		("short", "ping"),
		),
	#Player Abilities
	0xCA: (
		("bool", "invulnerable"),
		("bool", "is_flying"),
		("bool", "can_fly"),
		("bool", "instabreak"),
		),
	#Tab-complete
	0xCB: ("string", "text"),
	#Locale and View Distance
	0xCC: (
		("string", "locale"),
		("int", "view_distance"),
		),
	#Plugin Message
	0xFA: (
		("string", "channel"),
		("short", "data_length"),
		("byte_array", "data"),
		),
	#Encryption Key Response
	0xFC: (
		("short", "shared_secret_length"),
		("byte_array", "shared_secret"),
		("short", "verify_token_length"),
		("byte_array", "verify_token"),
		),
	#Encryption Key Request
	0xFD: (
		("string", "server_id"),
		("short", "public_key_length"),
		("byte_array", "public_key"),
		("short", "verify_token_length"),
		("byte_array", "verify_token"),
		),
	#Server List Ping
	0xFE: ("byte", "Magic"),
	#Disconnect
	0xFF: ("string", "reason"),
}

#Normalize data structures
for key, val in structs.iteritems():
	if isinstance(val, dict):
		for k in (SERVER_TO_CLIENT, CLIENT_TO_SERVER):
			if len(val[k]) and not isinstance(val[k][0], tuple):
				structs[key][k] = (val[k],)
		continue
	elif len(val) and not isinstance(val[0], tuple):
		val = (val,)
	val = {
		CLIENT_TO_SERVER: val,
		SERVER_TO_CLIENT: val}
	structs[key] = val