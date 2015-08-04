from spock.utils import BoundingBox

#Materials
MCM_MAT_ROCK         = 0x00
MCM_MAT_DIRT         = 0x01
MCM_MAT_WOOD         = 0x02
MCM_MAT_WEB          = 0x03
MCM_MAT_WOOL         = 0x04
MCM_MAT_VINE         = 0x05
MCM_MAT_LEAVES       = 0x06

#Gate
MCM_GATE_SOUTH       = 0x00
MCM_GATE_WEST        = 0x01
MCM_GATE_NORTH       = 0x02
MCM_GATE_EAST        = 0x03

MCM_GATE_CLOSE       = 0x00
MCM_GATE_OPEN        = 0x01

MCM_GATE_UNPOWERED   = 0x00
MCM_GATE_POWERED     = 0x01

#Door
MCM_DOOR_WEST        = 0x00
MCM_DOOR_NORTH       = 0x01
MCM_DOOR_EAST        = 0x02
MCM_DOOR_SOUTH       = 0x03

MCM_DOOR_CLOSE       = 0x00
MCM_DOOR_OPEN        = 0x01

MCM_DOOR_LOWER       = 0x00
MCM_DOOR_UPPER       = 0x01

MCM_DOOR_HINGE_LEFT  = 0x00
MCM_DOOR_HINGE_RIGHT = 0x01


#Trapdoor
MCM_TRAPDOOR_WEST    = 0x00
MCM_TRAPDOOR_NORTH   = 0x01
MCM_TRAPDOOR_EAST    = 0x02
MCM_TRAPDOOR_SOUTH   = 0x03

MCM_TRAPDOOR_CLOSE   = 0x00
MCM_TRAPDOOR_OPEN    = 0x01

MCM_TRAPDOOR_LOWER   = 0x00
MCM_TRAPDOOR_UPPER   = 0x01

#Slab
MCM_SLAB_LOWER       = 0x00
MCM_SLAB_UPPER       = 0x01


blocks = {}
def map_block(block_id):
    def inner(cl):
        blocks[block_id] = cl
        cl.block_id = block_id
        return cl
    return inner

def get_block(block_id, meta = 0, init=True):
    if init:
        return blocks[block_id](meta) if block_id < len(blocks) else None
    else:
        return blocks[block_id] if block_id < len(blocks) else None


class MapBlock:
    display_name = 'Map Block'
    name = 'map_block'
    hardness = 0
    stack_size = 64
    diggable = True
    material = None
    harvest_tools = None

    def __init__(self, meta):
        self.bounding_box = BoundingBox(1,1)

    def change_meta(self, meta):
        pass

class FenceBlock(MapBlock):
    def __init__(self, meta):
        self.bounding_box = BoundingBox(1,1.5)

class GateBlock(MapBlock):
    def __init__(self, meta):
        self.direction = meta&0x03
        self.open = (meta>>2)&0x01 == MCM_GATE_OPEN
        self.powered = meta>>3 == MCM_GATE_POWERED
        if self.open:
            self.bounding_box = None
        else:
            self.bounding_box = BoundingBox(1,1.5)

class DoorBlock(MapBlock):
    def __init__(self, meta):
        self.section = (meta>>3)&0x1
        if self.section == MCM_DOOR_LOWER:
            self.open = (meta>>2)&0x01 == MCM_DOOR_OPEN
            self.direction = meta&0x03
            if not self.open:
                self.bounding_box = BoundingBox(1,2)
            else:
                self.bounding_box = None
        elif self.section == MCM_DOOR_UPPER:
            self.hinge = meta&0x01
            self.bounding_box = None

class SlabBlock(MapBlock):
    def __init__(self, meta):
        self.orientation = (meta>>3)&0x1
        self.bounding_box = BoundingBox(1,1)

class StairBlock(MapBlock):
    def __init__(self, meta):
        self.bounding_box = BoundingBox(1,1)

class TrapdoorBlock(MapBlock):
    def __init__(self, meta):
        self.direction = meta&0x03
        self.open = (meta>>2)&0x01 == MCM_TRAPDOOR_OPEN
        self.orientation = (meta>>3)&0x1
        if self.open == MCM_TRAPDOOR_OPEN:
            self.bounding_box = None
        elif self.orientation == MCM_TRAPDOOR_UPPER:
            self.bounding_box = BoundingBox(1,1)
        elif self.orientation == MCM_TRAPDOOR_LOWER:
            self.bounding_box = BoundingBox(1,0.4)

class NoCollisionBlock(MapBlock):
    def __init__(self, meta):
        self.bounding_box = None

@map_block(0)
class AirBlock(NoCollisionBlock):
    display_name = 'Air'
    name = 'air'
    diggable = False

@map_block(1)
class StoneBlock(MapBlock):
    display_name = 'Stone'
    name = 'stone'
    hardness = 1.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(2)
class GrassBlock(MapBlock):
    display_name = 'Grass Block'
    name = 'grass'
    hardness = 0.6
    material = MCM_MAT_DIRT

@map_block(3)
class DirtBlock(MapBlock):
    display_name = 'Dirt'
    name = 'dirt'
    hardness = 0.5
    material = MCM_MAT_DIRT

@map_block(4)
class CobbleBlock(MapBlock):
    display_name = 'Cobblestone'
    name = 'stonebrick'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(5)
class WoodplankBlock(MapBlock):
    display_name = 'Wooden Planks'
    name = 'wood'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(6)
class SaplingBlock(NoCollisionBlock):
    display_name = 'Sapling'
    name = 'sapling'

@map_block(7)
class BedrockBlock(MapBlock):
    display_name = 'Bedrock'
    name = 'bedrock'
    hardness = None
    diggable = False

@map_block(8)
class WaterBlock(NoCollisionBlock):
    display_name = 'Water'
    name = 'water'
    hardness = 100
    diggable = False

@map_block(9)
class StationarywaterBlock(NoCollisionBlock):
    display_name = 'Stationary Water'
    name = 'waterStationary'
    hardness = 100
    diggable = False

@map_block(10)
class LavaBlock(NoCollisionBlock):
    display_name = 'Lava'
    name = 'lava'
    hardness = 100
    diggable = False

@map_block(11)
class StationarylavaBlock(NoCollisionBlock):
    display_name = 'Stationary Lava'
    name = 'lavaStationary'
    hardness = 100
    diggable = False

@map_block(12)
class SandBlock(MapBlock):
    display_name = 'Sand'
    name = 'sand'
    hardness = 0.5
    material = MCM_MAT_DIRT

@map_block(13)
class GravelBlock(MapBlock):
    display_name = 'Gravel'
    name = 'gravel'
    hardness = 0.6
    material = MCM_MAT_DIRT

@map_block(14)
class GoldoreBlock(MapBlock):
    display_name = 'Gold Ore'
    name = 'oreGold'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(15)
class IronoreBlock(MapBlock):
    display_name = 'Iron Ore'
    name = 'oreIron'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (274, 257, 278)

@map_block(16)
class CoaloreBlock(MapBlock):
    display_name = 'Coal Ore'
    name = 'oreCoal'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(17)
class Woodblock(MapBlock):
    display_name = 'Wood'
    name = 'log'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(18)
class LeavesBlock(MapBlock):
    display_name = 'Leaves'
    name = 'leaves'
    hardness = 0.2
    material = MCM_MAT_LEAVES

@map_block(19)
class SpongeBlock(MapBlock):
    display_name = 'Sponge'
    name = 'sponge'
    hardness = 0.6

@map_block(20)
class GlassBlock(MapBlock):
    display_name = 'Glass'
    name = 'glass'
    hardness = 0.3

@map_block(21)
class LapisoreBlock(MapBlock):
    display_name = 'Lapis Lazuli Ore'
    name = 'oreLapis'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (274, 257, 278)

@map_block(22)
class LapisBlock(MapBlock):
    display_name = 'Lapis Lazuli Block'
    name = 'blockLapis'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (274, 257, 278)

@map_block(23)
class DispenserBlock(MapBlock):
    display_name = 'Dispenser'
    name = 'dispenser'
    hardness = 3.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(24)
class SandstoneBlock(MapBlock):
    display_name = 'Sandstone'
    name = 'sandStone'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(25)
class NoteBlock(MapBlock):
    display_name = 'Note Block'
    name = 'musicBlock'
    hardness = 0.8
    material = MCM_MAT_WOOD

@map_block(26)
class BedBlock(MapBlock):
    display_name = 'Bed'
    name = 'bed'
    hardness = 0.2
    stack_size = 1

@map_block(27)
class PoweredrailBlock(NoCollisionBlock):
    display_name = 'Powered Rail'
    name = 'goldenRail'
    hardness = 0.7
    material = MCM_MAT_ROCK

@map_block(28)
class DetectorrailBlock(NoCollisionBlock):
    display_name = 'Detector Rail'
    name = 'detectorRail'
    hardness = 0.7
    material = MCM_MAT_ROCK

@map_block(29)
class StickypistonBlock(MapBlock):
    display_name = 'Sticky Piston'
    name = 'pistonStickyBase'

@map_block(30)
class CobwebBlock(NoCollisionBlock):
    display_name = 'Cobweb'
    name = 'web'
    hardness = 4
    material = MCM_MAT_WEB
    harvest_tools = (359, 267, 268, 272, 276, 283)

@map_block(31)
class TallgrassBlock(NoCollisionBlock):
    display_name = 'Grass'
    name = 'tallgrass'

@map_block(32)
class DeadbushBlock(NoCollisionBlock):
    display_name = 'Dead Bush'
    name = 'deadbush'

@map_block(33)
class PistonBlock(MapBlock):
    display_name = 'Piston'
    name = 'pistonBase'

@map_block(34)
class PistonextensionBlock(MapBlock):
    display_name = 'Piston Extension'
    name = 'pistonExtension'

@map_block(35)
class WoolBlock(MapBlock):
    display_name = 'Wool'
    name = 'cloth'
    hardness = 0.8
    material = MCM_MAT_WOOL

@map_block(36)
class PistonmovedBlock(MapBlock):
    display_name = 'Block Moved by Piston'
    name = 'blockMovedByPiston'

@map_block(37)
class FlowerBlock(NoCollisionBlock):
    display_name = 'Flower'
    name = 'flower'

@map_block(38)
class RoseBlock(NoCollisionBlock):
    display_name = 'Rose'
    name = 'rose'

@map_block(39)
class BrownshroomBlock(NoCollisionBlock):
    display_name = 'Brown Mushroom'
    name = 'mushroomBrown'

@map_block(40)
class RedshroomBlock(NoCollisionBlock):
    display_name = 'Red Mushroom'
    name = 'mushroomRed'

@map_block(41)
class GoldBlock(MapBlock):
    display_name = 'Block of Gold'
    name = 'blockGold'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(42)
class IronBlock(MapBlock):
    display_name = 'Block of Iron'
    name = 'blockIron'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (274, 257, 278)

@map_block(43)
class DoublestoneslabBlock(MapBlock):
    display_name = 'Double Stone Slab'
    name = 'stoneSlabDouble'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(44)
class StoneslabBlock(SlabBlock):
    display_name = 'Stone Slab'
    name = 'stoneSlab'
    hardness = 2

@map_block(45)
class BricksBlock(MapBlock):
    display_name = 'Bricks'
    name = 'brick'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(46)
class TntBlock(MapBlock):
    display_name = 'TNT'
    name = 'tnt'

@map_block(47)
class BookshelfBlock(MapBlock):
    display_name = 'Bookshelf'
    name = 'bookshelf'
    hardness = 1.5
    material = MCM_MAT_WOOD

@map_block(48)
class MossstoneBlock(MapBlock):
    display_name = 'Moss Stone'
    name = 'stoneMoss'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(49)
class ObsidianBlock(MapBlock):
    display_name = 'Obsidian'
    name = 'obsidian'
    hardness = 50
    material = MCM_MAT_ROCK
    harvest_tools = (278,)

@map_block(50)
class TorchBlock(NoCollisionBlock):
    display_name = 'Torch'
    name = 'torch'

@map_block(51)
class FireBlock(NoCollisionBlock):
    display_name = 'Fire'
    name = 'fire'

@map_block(52)
class MobspawnerBlock(MapBlock):
    display_name = 'Monster Spawner'
    name = 'mobSpawner'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(53)
class WoodstairBlock(StairBlock):
    display_name = 'Wooden Stairs'
    name = 'stairsWood'
    material = MCM_MAT_WOOD

@map_block(54)
class ChestBlock(MapBlock):
    display_name = 'Chest'
    name = 'chest'
    hardness = 2.5
    material = MCM_MAT_WOOD

@map_block(55)
class RedstonedustBlock(NoCollisionBlock):
    display_name = 'Redstone Dust'
    name = 'redstoneDust'

@map_block(56)
class DiamondoreBlock(MapBlock):
    display_name = 'Diamond Ore'
    name = 'oreDiamond'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(57)
class DiamondBlock(MapBlock):
    display_name = 'Block of Diamond'
    name = 'blockDiamond'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(58)
class CraftingBlock(MapBlock):
    display_name = 'Crafting Table'
    name = 'workbench'
    hardness = 2.5
    material = MCM_MAT_WOOD

@map_block(59)
class CropsBlock(NoCollisionBlock):
    display_name = 'Wheat Crops'
    name = 'wheat'

@map_block(60)
class FarmBlock(MapBlock):
    display_name = 'Farmland'
    name = 'farmland'
    hardness = 0.6
    material = MCM_MAT_DIRT

@map_block(61)
class FurnaceBlock(MapBlock):
    display_name = 'Furnace'
    name = 'furnace'
    hardness = 3.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(62)
class BurningfurnaceBlock(MapBlock):
    display_name = 'Burning Furnace'
    name = 'furnaceBurning'
    hardness = 3.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(63)
class StandingsignBlock(NoCollisionBlock):
    display_name = 'Sign Post'
    name = 'signPost'
    hardness = 1
    stack_size = 16
    material = MCM_MAT_WOOD

@map_block(64)
class WooddoorBlock(DoorBlock):
    display_name = 'Wooden Door'
    name = 'doorWood'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

@map_block(65)
class LadderBlock(NoCollisionBlock):
    display_name = 'Ladder'
    name = 'ladder'
    hardness = 0.4

@map_block(66)
class RailBlock(NoCollisionBlock):
    display_name = 'Rail'
    name = 'rail'
    hardness = 0.7
    material = MCM_MAT_ROCK

@map_block(67)
class CobblestairBlock(StairBlock):
    display_name = 'Cobblestone Stairs'
    name = 'stairsStone'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(68)
class WallsignBlock(NoCollisionBlock):
    display_name = 'Wall Sign'
    name = 'signWall'
    hardness = 1
    stack_size = 16
    material = MCM_MAT_WOOD

@map_block(69)
class LeverBlock(NoCollisionBlock):
    display_name = 'Lever'
    name = 'lever'
    hardness = 0.5

@map_block(70)
class StoneplateBlock(NoCollisionBlock):
    display_name = 'Stone Pressure Plate'
    name = 'stonePressurePlate'
    hardness = 0.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(71)
class IrondoorBlock(DoorBlock):
    display_name = 'Iron Door'
    name = 'doorIron'
    hardness = 5
    stack_size = 1
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(72)
class WoodplateBlock(NoCollisionBlock):
    display_name = 'Wooden Pressure Plate'
    name = 'woodPressurePlate'
    hardness = 0.5
    material = MCM_MAT_WOOD

@map_block(73)
class RedstoneoreBlock(MapBlock):
    display_name = 'Redstone Ore'
    name = 'oreRedstone'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(74)
class GlowingredstoneoreBlock(MapBlock):
    display_name = 'Glowing Redstone Ore'
    name = 'oreRedstoneGlowing'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(75)
class RedstonetorchoffBlock(NoCollisionBlock):
    display_name = 'Redstone Torch (Inactive)'
    name = 'notGateInactive'

@map_block(76)
class RedstonetorchonBlock(NoCollisionBlock):
    display_name = 'Redstone Torch (Active)'
    name = 'notGateActive'

@map_block(77)
class StonebuttonBlock(NoCollisionBlock):
    display_name = 'Stone Button'
    name = 'buttonStone'
    hardness = 0.5

@map_block(78)
class GroundsnowBlock(NoCollisionBlock):
    display_name = 'Snow'
    name = 'snow'
    hardness = 0.1
    material = MCM_MAT_DIRT
    harvest_tools = (269, 273, 256, 277, 284)

@map_block(79)
class IceBlock(MapBlock):
    display_name = 'Ice'
    name = 'ice'
    hardness = 0.5
    material = MCM_MAT_ROCK

@map_block(80)
class SnowBlock(MapBlock):
    display_name = 'Snow Block'
    name = 'snowBlock'
    hardness = 0.2
    material = MCM_MAT_DIRT
    harvest_tools = (269, 273, 256, 277, 284)

@map_block(81)
class CactusBlock(MapBlock):
    display_name = 'Cactus'
    name = 'cactus'
    hardness = 0.4

@map_block(82)
class ClayBlock(MapBlock):
    display_name = 'Clay'
    name = 'clay'
    hardness = 0.6
    material = MCM_MAT_DIRT

@map_block(83)
class ReedsBlock(NoCollisionBlock):
    display_name = 'Sugar cane'
    name = 'reeds'

@map_block(84)
class JukeboxBlock(MapBlock):
    display_name = 'Jukebox'
    name = 'jukebox'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(85)
class WoodfenceBlock(FenceBlock):
    display_name = 'Fence'
    name = 'fence'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(86)
class PumpkinBlock(MapBlock):
    display_name = 'Pumpkin'
    name = 'pumpkin'
    hardness = 1
    material = 'plant'

@map_block(87)
class NetherrackBlock(MapBlock):
    display_name = 'Netherrack'
    name = 'hellrock'
    hardness = 0.4
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(88)
class SoulsandBlock(MapBlock):
    display_name = 'Soul Sand'
    name = 'hellsand'
    hardness = 0.5
    material = MCM_MAT_DIRT

@map_block(89)
class GlowstoneBlock(MapBlock):
    display_name = 'Glowstone'
    name = 'lightgem'
    hardness = 0.3

@map_block(90)
class PortalBlock(NoCollisionBlock):
    display_name = 'Portal'
    name = 'portal'
    hardness = None
    diggable = False

@map_block(91)
class JackBlock(MapBlock):
    display_name = 'Jack \'o\' Lantern'
    name = 'litpumpkin'
    hardness = 1
    material = 'plant'

@map_block(92)
class CakeBlock(MapBlock):
    display_name = 'Cake'
    name = 'cake'
    hardness = 0.5
    stack_size = 1

@map_block(93)
class RedstonerepoffBlock(NoCollisionBlock):
    display_name = 'Redstone Repeater (Inactive)'
    name = 'redstoneRepeaterInactive'

@map_block(94)
class RedstonereponBlock(NoCollisionBlock):
    display_name = 'Redstone Repeater (Active)'
    name = 'redstoneRepeaterActive'

@map_block(95)
class LockedchestBlock(MapBlock):
    display_name = 'Locked chest'
    name = 'lockedchest'

@map_block(96)
class OaktrapdoorBlock(TrapdoorBlock):
    display_name = 'Trapdoor'
    name = 'trapdoor'
    hardness = 3
    material = MCM_MAT_WOOD

@map_block(97)
class MonstereggBlock(MapBlock):
    display_name = 'Monster Egg'
    name = 'monsterStoneEgg'
    hardness = 0.75

@map_block(98)
class StonebrickBlock(MapBlock):
    display_name = 'Stone Brick'
    name = 'stonebricksmooth'
    hardness = 1.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(99)
class HugebrownshroomBlock(MapBlock):
    display_name = 'Huge Brown Mushroom'
    name = 'mushroomHugeBrown'
    hardness = 0.2
    material = MCM_MAT_WOOD

@map_block(100)
class HugeredshroomBlock(MapBlock):
    display_name = 'Huge Red Mushroom'
    name = 'mushroomHugeRed'
    hardness = 0.2
    material = MCM_MAT_WOOD

@map_block(101)
class IronfenceBlock(FenceBlock):
    display_name = 'Iron Bars'
    name = 'fenceIron'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(102)
class GlasspaneBlock(MapBlock):
    display_name = 'Glass Pane'
    name = 'glassPane'
    hardness = 0.3

@map_block(103)
class MelonBlock(MapBlock):
    display_name = 'Melon'
    name = 'melon'
    hardness = 1
    material = 'melon'

@map_block(104)
class PumpkinstemBlock(NoCollisionBlock):
    display_name = 'Pumpkin Stem'
    name = 'pumpkinStem'

@map_block(105)
class MelonstemBlock(NoCollisionBlock):
    display_name = 'Melon Stem'
    name = 'melonStem'

@map_block(106)
class VinesBlock(NoCollisionBlock):
    display_name = 'Vines'
    name = 'vine'
    hardness = 0.2
    material = MCM_MAT_VINE

@map_block(107)
class WoodfencegateBlock(GateBlock):
    display_name = 'Fence Gate'
    name = 'fenceGate'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(108)
class BrickstairBlock(StairBlock):
    display_name = 'Brick Stairs'
    name = 'stairsBrick'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(109)
class StonebrickstairBlock(StairBlock):
    display_name = 'Stone Brick Stairs'
    name = 'stairsStoneBrickSmooth'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(110)
class MyceliumBlock(MapBlock):
    display_name = 'Mycelium'
    name = 'mycel'
    hardness = 0.6
    material = MCM_MAT_DIRT

@map_block(111)
class LilypadBlock(MapBlock):
    display_name = 'Lily Pad'
    name = 'waterlily'
    def __init__(self, meta):
        self.bounding_box = BoundingBox(1,0.2,1)

@map_block(112)
class NetherbrickBlock(MapBlock):
    display_name = 'Nether Brick'
    name = 'netherBrick'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(113)
class NetherbrickfenceBlock(FenceBlock):
    display_name = 'Nether Brick Fence'
    name = 'netherFence'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(114)
class NetherbrickstairBlock(StairBlock):
    display_name = 'Nether Brick Stairs'
    name = 'stairsNetherBrick'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(115)
class NetherwartBlock(NoCollisionBlock):
    display_name = 'Nether Wart'
    name = 'netherStalk'

@map_block(116)
class EnchantmentBlock(MapBlock):
    display_name = 'Enchantment Table'
    name = 'enchantmentTable'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(117)
class BrewingBlock(MapBlock):
    display_name = 'Brewing Stand'
    name = 'brewingStand'
    hardness = 0.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(118)
class CauldronBlock(MapBlock):
    display_name = 'Cauldron'
    name = 'cauldron'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(119)
class EndportalBlock(NoCollisionBlock):
    display_name = 'End Portal'
    name = 'endPortal'
    hardness = None
    diggable = False

@map_block(120)
class EndportalframeBlock(MapBlock):
    display_name = 'End Portal Frame'
    name = 'endPortalFrame'
    hardness = None
    diggable = False

@map_block(121)
class EndstoneBlock(MapBlock):
    display_name = 'End Stone'
    name = 'whiteStone'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(122)
class DragoneggBlock(MapBlock):
    display_name = 'Dragon Egg'
    name = 'dragonEgg'
    hardness = 3

@map_block(123)
class RedstonelampoffBlock(MapBlock):
    display_name = 'Redstone Lamp (Inactive)'
    name = 'redstoneLightInactive'
    hardness = 0.3

@map_block(124)
class RedstonelamponBlock(MapBlock):
    display_name = 'Redstone Lamp (Active)'
    name = 'redstoneLightActive'
    hardness = 0.3

@map_block(125)
class WooddoubleslabBlock(MapBlock):
    display_name = 'Wooden Double Slab'
    name = 'woodSlabDouble'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(126)
class WoodslabBlock(SlabBlock):
    display_name = 'Wooden Slab'
    name = 'woodSlab'
    hardness = 2

@map_block(127)
class CocoapodBlock(MapBlock):
    display_name = 'Cocoa Pod'
    name = 'cocoa'
    hardness = 0.2
    material = 'plant'

@map_block(128)
class SandstonestairBlock(StairBlock):
    display_name = 'Sandstone Stairs'
    name = 'stairsSandStone'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(129)
class EmeraldoreBlock(MapBlock):
    display_name = 'Emerald Ore'
    name = 'oreEmerald'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(130)
class EnderchestBlock(MapBlock):
    display_name = 'Ender Chest'
    name = 'enderChest'
    hardness = 22.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(131)
class TripwirehookBlock(NoCollisionBlock):
    display_name = 'Tripwire Hook'
    name = 'tripWireSource'

@map_block(132)
class TripwireBlock(NoCollisionBlock):
    display_name = 'Tripwire'
    name = 'tripWire'

@map_block(133)
class EmeraldBlock(MapBlock):
    display_name = 'Block of Emerald'
    name = 'blockEmerald'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (257, 278)

@map_block(134)
class SprucestairBlock(StairBlock):
    display_name = 'Spruce Wood Stairs'
    name = 'stairsWoodSpruce'

@map_block(135)
class BirchstairBlock(StairBlock):
    display_name = 'Birch Wood Stairs'
    name = 'stairsWoodBirch'

@map_block(136)
class JunglestairBlock(StairBlock):
    display_name = 'Jungle Wood Stairs'
    name = 'stairsWoodJungle'

@map_block(137)
class CommandBlock(MapBlock):
    display_name = 'Command Block'
    name = 'commandBlock'
    hardness = None
    diggable = False
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(138)
class BeaconBlock(MapBlock):
    display_name = 'Beacon'
    name = 'beacon'
    hardness = 3

@map_block(139)
class CobblewallBlock(FenceBlock):
    display_name = 'Cobblestone Wall'
    name = 'cobbleWall'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(140)
class FlowerpotBlock(MapBlock):
    display_name = 'Flower Pot'
    name = 'flowerPot'

@map_block(141)
class CarrotBlock(NoCollisionBlock):
    display_name = 'Carrots'
    name = 'carrots'

@map_block(142)
class PotatoBlock(NoCollisionBlock):
    display_name = 'Potatoes'
    name = 'potatoes'

@map_block(143)
class WoodbuttonBlock(NoCollisionBlock):
    display_name = 'Wooden Button'
    name = 'buttonWood'
    hardness = 0.5

@map_block(144)
class MobheadBlock(MapBlock):
    display_name = 'Mob Head'
    name = 'skull'
    hardness = 1

@map_block(145)
class AnvilBlock(MapBlock):
    display_name = 'Anvil'
    name = 'anvil'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(146)
class TrappedchestBlock(MapBlock):
    display_name = 'Trapped Chest'
    name = 'trappedChest'
    hardness = 2.5
    material = MCM_MAT_WOOD

@map_block(147)
class WeightedplatelightBlock(NoCollisionBlock):
    display_name = 'Weighted Pressure plate (Light)'
    name = 'pressurePlateWeightedLight'
    hardness = 0.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(148)
class WeightedplateheavyBlock(NoCollisionBlock):
    display_name = 'Weighted Pressure plate (Heavy)'
    name = 'pressurePlateWeightedHeavy'
    hardness = 0.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(149)
class ComparatoroffBlock(NoCollisionBlock):
    display_name = 'Redstone Comparator (Inactive)'
    name = 'redstoneComparatorInactive'

@map_block(150)
class ComparatoronBlock(NoCollisionBlock):
    display_name = 'Redstone Comparator (Active)'
    name = 'redstoneComparatorActive'

@map_block(151)
class LightsensorBlock(MapBlock):
    display_name = 'Daylight Sensor'
    name = 'daylightSensor'
    hardness = 0.2
    material = MCM_MAT_WOOD

@map_block(152)
class RedstoneBlock(MapBlock):
    display_name = 'Block of Redstone'
    name = 'redstoneBlock'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(153)
class NetherquartzoreBlock(MapBlock):
    display_name = 'Nether Quartz Ore'
    name = 'netherQuartzOre'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(154)
class HopperBlock(MapBlock):
    display_name = 'Hopper'
    name = 'hopper'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(155)
class QuartzBlock(MapBlock):
    display_name = 'Block of Quartz'
    name = 'quartzBlock'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(156)
class QuartzstairBlock(StairBlock):
    display_name = 'Quartz Stairs'
    name = 'quartzStairs'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(157)
class ActivatorrailBlock(NoCollisionBlock):
    display_name = 'Activator Rail'
    name = 'activatorRail'
    hardness = 0.7
    material = MCM_MAT_ROCK

@map_block(158)
class DropperBlock(MapBlock):
    display_name = 'Dropper'
    name = 'dropper'
    hardness = 3.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(159)
class StainedclayBlock(MapBlock):
    display_name = 'Stained Clay'
    name = 'stainedClay'
    hardness = 1.25
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(160)
class StainedglasspaneBlock(MapBlock):
    display_name = 'Stained Glass Pane'
    name = 'stainedGlassPane'
    hardness = 0.3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(161)
class AcacialeavesBlock(MapBlock):
    display_name = 'Acacia Leaves'
    name = 'acaciaLeaves'
    hardness = 0.2
    material = MCM_MAT_LEAVES

@map_block(162)
class AcaciawoodBlock(MapBlock):
    display_name = 'Acacia Wood'
    name = 'acaciaWood'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(163)
class AcaciastairBlock(StairBlock):
    display_name = 'Acacia Stairs'
    name = 'acaciaStairs'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(164)
class DarkoakstairBlock(StairBlock):
    display_name = 'Dark Oak Stairs'
    name = 'darkoakStairs'
    hardness = 2
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(165)
class SlimeBlock(MapBlock):
    display_name = 'Slime'
    name = 'slime'
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(166)
class BarrierBlock(MapBlock):
    display_name = 'Barrier'
    name = 'barrier'
    hardness = None
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(167)
class IrontrapdoorBlock(TrapdoorBlock):
    display_name = 'Iron Trapdoor'
    name = 'ironTrapdoor'
    hardness = 3
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(168)
class PrismarineBlock(MapBlock):
    display_name = 'Prismarine'
    name = 'prismarine'
    hardness = 1.5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(169)
class SealanternBlock(MapBlock):
    display_name = 'Sea Lantern'
    name = 'seaLantern'
    hardness = 0.3
    material = MCM_MAT_ROCK

@map_block(170)
class HaybaleBlock(MapBlock):
    display_name = 'Hay Bale'
    name = 'haybale'
    hardness = 0.5
    material = MCM_MAT_ROCK

@map_block(171)
class CarpetBlock(NoCollisionBlock):
    display_name = 'Carpet'
    name = 'carpet'
    material = MCM_MAT_WOOL

@map_block(172)
class HardenedclayBlock(MapBlock):
    display_name = 'Hardened Clay'
    name = 'hardenedClay'
    hardness = 1.25
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(173)
class CoalBlock(MapBlock):
    display_name = 'Coal'
    name = 'coal'
    hardness = 5
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(174)
class PackediceBlock(MapBlock):
    display_name = 'Packed Ice'
    name = 'packedIce'
    hardness = 0.5
    material = MCM_MAT_ROCK

@map_block(175)
class SunflowerBlock(NoCollisionBlock):
    display_name = 'Sunflower'
    name = 'sunflower'
    material = MCM_MAT_ROCK

@map_block(176)
class BannerfreeBlock(NoCollisionBlock):
    display_name = 'Free Standing Banner'
    name = 'bannerFree'
    hardness = 1
    stack_size = 1
    material = MCM_MAT_ROCK

@map_block(177)
class BannerwallBlock(NoCollisionBlock):
    display_name = 'Wall Mounted Banner'
    name = 'bannerWall'
    hardness = 1
    stack_size = 1
    material = MCM_MAT_ROCK

@map_block(178)
class LightsensorinvertedBlock(MapBlock):
    display_name = 'Inverted Daylight Sensor'
    name = 'daylightSensorInverted'
    hardness = 0.2
    material = MCM_MAT_WOOD

@map_block(179)
class RedsandstoneBlock(MapBlock):
    display_name = 'Red Sandstone'
    name = 'redSandstone'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(180)
class RedsandstonestairBlock(StairBlock):
    display_name = 'Red Sandstone Stairs'
    name = 'redSandstoneStairs'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(181)
class RedsandstonedoubleslabBlock(MapBlock):
    display_name = 'Red Sandstone Double Slab'
    name = 'redSandstoneDoubleSlab'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(182)
class RedsandstoneslabBlock(SlabBlock):
    display_name = 'Red Sandstone Slab'
    name = 'redSandstoneSlab'
    hardness = 0.8
    material = MCM_MAT_ROCK
    harvest_tools = (270, 274, 257, 278, 285)

@map_block(183)
class FencegatespruceBlock(GateBlock):
    display_name = 'Spruce Fence Gate'
    name = 'fenceGateSpruce'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(184)
class FencegatebirchBlock(GateBlock):
    display_name = 'Birch Fence Gate'
    name = 'fenceGateBirch'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(185)
class FencegatejungleBlock(GateBlock):
    display_name = 'Jungle Fence Gate'
    name = 'fenceGateJungle'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(186)
class FencegatedarkoakBlock(GateBlock):
    display_name = 'Dark Oak Fence Gate'
    name = 'fenceGateDarkOak'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(187)
class FencegateacaciaBlock(GateBlock):
    display_name = 'Acacia Fence Gate'
    name = 'fenceGateAcacia'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(188)
class FencespruceBlock(FenceBlock):
    display_name = 'Spruce Fence'
    name = 'fenceSpruce'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(189)
class FencebirchBlock(FenceBlock):
    display_name = 'Birch Fence'
    name = 'fenceBirch'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(190)
class FencejungleBlock(FenceBlock):
    display_name = 'Jungle Fence'
    name = 'fenceJungle'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(191)
class FencedarkoakBlock(FenceBlock):
    display_name = 'Dark Oak Fence'
    name = 'fenceDarkOak'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(192)
class FenceacaciaBlock(FenceBlock):
    display_name = 'Acacia Fence'
    name = 'fenceAcacia'
    hardness = 2
    material = MCM_MAT_WOOD

@map_block(193)
class DoorspruceBlock(DoorBlock):
    display_name = 'Spruce Door'
    name = 'doorSpruce'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

@map_block(194)
class DoorbirchBlock(DoorBlock):
    display_name = 'Birch Door'
    name = 'doorBirch'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

@map_block(195)
class DoorjungleBlock(DoorBlock):
    display_name = 'Jungle Door'
    name = 'DoorJungle'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

@map_block(196)
class DooracaciaBlock(DoorBlock):
    display_name = 'Acacia Door'
    name = 'doorAcacia'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

@map_block(197)
class DoordarkoakBlock(DoorBlock):
    display_name = 'Dark Oak Door'
    name = 'doorDarkOak'
    hardness = 3
    stack_size = 1
    material = MCM_MAT_WOOD

blocks = tuple(blocks[i] for i in range(len(blocks)))

biomes = {}
def map_biome(biome_id):
    def inner(cl):
        biomes[biome_id] = cl
        cl.biome_id = biome_id
        return cl
    return inner

def get_biome(biome_id):
    return biomes[biome_id]() if biome_id in biomes else None

class MapBiome:
    name = 'Map Biome'
    temperature = 0.0

@map_biome(0)
class OceanBiome(MapBiome):
    name = 'Ocean'
    temperature = 0.5

@map_biome(1)
class PlainsBiome(MapBiome):
    name = 'Plains'
    temperature = 0.8

@map_biome(2)
class DesertBiome(MapBiome):
    name = 'Desert'
    temperature = 2

@map_biome(3)
class ExtremeHillsBiome(MapBiome):
    name = 'Extreme Hills'
    temperature = 0.2

@map_biome(4)
class ForestBiome(MapBiome):
    name = 'Forest'
    temperature = 0.7

@map_biome(5)
class TaigaBiome(MapBiome):
    name = 'Taiga'
    temperature = 0.05

@map_biome(6)
class SwamplandBiome(MapBiome):
    name = 'Swampland'
    temperature = 0.8

@map_biome(7)
class RiverBiome(MapBiome):
    name = 'River'
    temperature = 0.5

@map_biome(8)
class HellBiome(MapBiome):
    name = 'Hell'
    temperature = 2

@map_biome(9)
class SkyBiome(MapBiome):
    name = 'Sky'
    temperature = 0.5

@map_biome(10)
class FrozenOceanBiome(MapBiome):
    name = 'Frozen Ocean'
    temperature = 0

@map_biome(11)
class FrozenRiverBiome(MapBiome):
    name = 'Frozen River'
    temperature = 0

@map_biome(12)
class IcePlainsBiome(MapBiome):
    name = 'Ice Plains'
    temperature = 0

@map_biome(13)
class IceMountainsBiome(MapBiome):
    name = 'Ice Mountains'
    temperature = 0

@map_biome(14)
class MushroomIslandBiome(MapBiome):
    name = 'Mushroom Island'
    temperature = 0.9

@map_biome(15)
class MushroomIslandShoreBiome(MapBiome):
    name = 'Mushroom Island Shore'
    temperature = 0.9

@map_biome(16)
class BeachBiome(MapBiome):
    name = 'Beach'
    temperature = 0.8

@map_biome(17)
class DesertHillsBiome(MapBiome):
    name = 'Desert Hills'
    temperature = 2

@map_biome(18)
class ForestHillsBiome(MapBiome):
    name = 'Forest Hills'
    temperature = 0.7

@map_biome(19)
class TaigaHillsBiome(MapBiome):
    name = 'Taiga Hills'
    temperature = 0.05

@map_biome(20)
class ExtremeTaigaHillsEdgeBiome(MapBiome):
    name = 'Extreme Hills Edge'
    temperature = 0.2

@map_biome(21)
class JungleBiome(MapBiome):
    name = 'Jungle'
    temperature = 1.2

@map_biome(22)
class JungleHillsBiome(MapBiome):
    name = 'Jungle Hills'
    temperature = 1.2

@map_biome(23)
class JungleEdgeBiome(MapBiome):
    name = 'Jungle Edge'
    temperature = 0.95

@map_biome(24)
class DeepOceanBiome(MapBiome):
    name = 'Deep Ocean'
    temperature = 0.5

@map_biome(25)
class StoneBeachBiome(MapBiome):
    name = 'Stone Beach'
    temperature = 0.2

@map_biome(26)
class ColdBeachBiome(MapBiome):
    name = 'Cold Beach'
    temperature = 0

@map_biome(27)
class BirchForestBiome(MapBiome):
    name = 'Birch Forest'
    temperature = 0.6

@map_biome(28)
class BirchForestHillsBiome(MapBiome):
    name = 'Birch Forest Hills'
    temperature = 0.6

@map_biome(29)
class RoofedForestBiome(MapBiome):
    name = 'Roofed Forest'
    temperature = 0.7

@map_biome(30)
class ColdTaigaBiome(MapBiome):
    name = 'Cold Taiga'
    temperature = 0

@map_biome(31)
class ColdTaigaHillsBiome(MapBiome):
    name = 'Cold Taiga Hills'
    temperature = 0

@map_biome(32)
class MegaTaigaBiome(MapBiome):
    name = 'Mega Taiga'
    temperature = 0.3

@map_biome(33)
class MegaTaigaHillsBiome(MapBiome):
    name = 'Mega Taiga Hills'
    temperature = 0.3

@map_biome(34)
class ExtremeHillsPlusBiome(MapBiome):
    name = 'Extreme Hills+'
    temperature = 0.2

@map_biome(35)
class SavannaBiome(MapBiome):
    name = 'Savanna'
    temperature = 1.0

@map_biome(36)
class SavannaPlateauBiome(MapBiome):
    name = 'Savanna Plateau'
    temperature = 1.0

@map_biome(37)
class MesaBiome(MapBiome):
    name = 'Mesa'
    temperature = 1.0

@map_biome(38)
class MesaPlateauFBiome(MapBiome):
    name = 'Mesa Plateau F'
    temperature = 1.0

@map_biome(39)
class MesaPlateauBiome(MapBiome):
    name = 'Mesa Plateau'
    temperature = 1.0

@map_biome(129)
class SunflowerPlainsBiome(MapBiome):
    name = 'Sunflower Plains'
    temperature = 0.8

@map_biome(130)
class DesertMBiome(MapBiome):
    name = 'Desert M'
    temperature = 2

@map_biome(131)
class ExtremeHillsMBiome(MapBiome):
    name = 'Extreme Hills M'
    temperature = 0.2

@map_biome(132)
class FlowerForestBiome(MapBiome):
    name = 'Flower Forest'
    temperature = 0.7

@map_biome(133)
class TaigaMBiome(MapBiome):
    name = 'Taiga M'
    temperature = 0.25

@map_biome(134)
class SwamplandMBiome(MapBiome):
    name = 'Swampland M'
    temperature = 0.8

@map_biome(140)
class IcePlainsSpikesBiome(MapBiome):
    name = 'Ice Plains Spikes'
    temperature = 0

@map_biome(149)
class JungleMBiome(MapBiome):
    name = 'Jungle M'
    temperature = 0.95

@map_biome(151)
class JungleEdgeMBiome(MapBiome):
    name = 'Jungle Edge M'
    temperature = 0.95

@map_biome(155)
class BirchForestMBiome(MapBiome):
    name = 'Birch Forest M'
    temperature = 0.6

@map_biome(156)
class BirchForestHillsMBiome(MapBiome):
    name = 'Birch Forest Hills M'
    temperature = 0.6

@map_biome(157)
class RoofedForestMBiome(MapBiome):
    name = 'Roofed Forest M'
    temperature = 0.7

@map_biome(158)
class ColdTaigaMBiome(MapBiome):
    name = 'Cold Taiga M'
    temperature = 0

@map_biome(160)
class MegaSpruceTaigaBiome(MapBiome):
    name = 'Mega Spruce Taiga'
    temperature = 0.25

@map_biome(161)
class MegaSpruceTaigaHillsBiome(MapBiome):
    name = 'Mega Spruce Taiga Hills'
    temperature = 0.25

@map_biome(162)
class ExtremeHillsPlusMBiome(MapBiome):
    name = 'Extreme Hills+ M'
    temperature = 0.2

@map_biome(163)
class SavannaMBiome(MapBiome):
    name = 'Savanna M'
    temperature = 1.0

@map_biome(164)
class SavannaPlateauMBiome(MapBiome):
    name = 'Savanna Plateau M'
    temperature = 1.0

@map_biome(165)
class MesaBRyceBiome(MapBiome):
    name = 'Mesa (Bryce)'
    temperature = 1.0

@map_biome(166)
class MesaPlateauFMBiome(MapBiome):
    name = 'Mesa Plateau F M'
    temperature = 1.0

@map_biome(167)
class MesaPlateauMBiome(MapBiome):
    name = 'Mesa Plateau M'
    temperature = 1.0
