biomes = {}


def map_biome(biome_id):
    def inner(cl):
        biomes[biome_id] = cl
        cl.biome_id = biome_id
        return cl

    return inner


def get_biome(biome_id):
    return biomes[biome_id]() if biome_id in biomes else None


class MapBiome(object):
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
