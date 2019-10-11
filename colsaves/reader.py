import sys
import json

import tools

OCCUPATIONS = [
    "Farmer",          #0x00
    "Sugar planter",   #0x01
    "Tobacco planter", #0x02
    "Cotton planter",  #0x03
    "Fur trapper",     #0x04
    "Lumberjack",      #0x05
    "Ore miner",       #0x06
    "Silver miner",    #0x07
    "Fisherman",       #0x08
    "Distiller",       #0x09
    "Tobacconist",     #0x0A
    "Weaver",          #0x0B
    "Fur Trader",      #0x0C
    "Carpenter",       #0x0D
    "Blacksmith",      #0x0E
    "Gunsmith",        #0x0F
    "Preacher",        #0x10
    "Statesman",       #0x11
    "Teacher",         #0x12
    "unknown (0x13)",  #0x13
    "Pioneer",         #0x14
    "Vet. Soldier",    #0x15
    "Scout",           #0x16
    "Veteran dragoon", #0x17
    "Missionary",      #0x18
    "Ind. Servant",    #0x19
    "Criminal",        #0x1A
    "Indian convert",  #0x1B
    "Free colonis",    #0x1C
    "Armed brave",     #0x1D
    "Mounted brave",   #0x1E
    "unknown (0x1f)"   #0x1F
]

DIRECTIONS = [
"N", 
"E", 
"S", 
"W", 
"NW", 
"NE", 
"SE", 
"SW"
]

BUILDINGS = [
    "Stockade", "Fort", "Fortress", "Armory", "Magazine", "Arsenal", "Docks", "Drydock", 
    "Shipyard", "Town hall", "Town hall", "Town hall", "Schoolhouse", "College", "University", "Warehouse", 
    "Warehouse Exp", "Stable", "Custom house", "Printing press", "Newspaper", "Weavers house", " Weavers shop", "Textile mill", 
    "Tobacconists house", "Tobacconists shop", "Cigar factory", "Rum distillers house", "Rum distillers shop", "Rum factory", "Capitol", "Capitol Exp", 
    "Fur traders house", "Fur traders shop", "Fur factory", "Carpenters shop", "Lumber mill", "Church", "Cathedral", "Blacksmiths house",
    "Blacksmiths shop", "Iron works", "Artillery", "Wagon Train", "Caravel", "Merchantman", "Galleon", "Privateer", 
    "Frigate", "Nothing"
]

GOODS = [
"Food",         # 0x00
"Sugar",        # 0x01
"Tabacco",      # 0x02
"Cotton",       # 0x03
"Furs",         # 0x04
"Lumber",       # 0x05
"Ore",          # 0x06
"Silver",       # 0x07
"Horses",       # 0x08
"Rum",          # 0x09
"Cigars",       # 0x0A
"Cloth",        # 0x0B
"Coats",        # 0x0C
"Trade Goods",  # 0x0D
"Tools",        # 0x0E
"Muskets"       # 0x0F
]

NATIONS = [
"English",  #0x00
"French",   #0x01
"Spanish",  #0x02
"Dutch",    #0x03
"Inca",     #0x04
"Aztec",    #0x05
"Arawak",   #0x06
"Iroquios", #0x07
"Cherokee", #0x08
"Apache",   #0x09
"Sioux",    #0x0A
"Tupi",     #0x0B
]

UNITS = {
0 : "Colonist", 
1 : "Pioneer", 
2 : "Soldier", 

4 : "Veteran dragoon",
5 : "Scout",
6 : "Regular (Continental Army)", 
7 : "Cavalery (Republic Army)", 
8 : "Cavalery (Continental Army)", 
11: "Artillery", 
12: "Wagon Train",
13: "Caravel", 
14: "Merchantman", 
15: "Galleon", 
18: "Man-O-War (Continental Army)", 
19: "Brave",
20: "Armed Brave", 
21: "Mounted Brave", 
}


class Context:
    def __init__(self, file):
        self.file = file
        self.objects = []

class Tell:
    def read(self, context):
        return context.file.tell()


class String:
    def __init__(self, length):
        self.length = length

    def read(self, context):
        string = context.file.read(self.length).decode("utf-8")
        firstNul = string.find("\0")
        if firstNul >= 0:
            return string[:firstNul]
        return string

class Bits:
    """
     Extract :num_bits each from :num_bytes bytes. The length of the result array ist num_bytes // num_bits.
    """
    def __init__(self,  num_bytes, num_bits):
        self.num_bytes = num_bytes
        self.num_bits = num_bits
        
    def read(self, context):
        bytes = context.file.read(self.num_bytes)
        return list(tools.stream_bits(bytes, self.num_bits))

class Byte:
    def read(self, context):
        return tools.readu8(context.file)
        

class Bytes:
    def __init__(self, length):
        self.length = length

    def read(self, context):
        return context.file.read(self.length)

class Short:
    def read(self, context):
        return tools.read16(context.file)

class Word:
    def read(self, context):
        return tools.readu16(context.file)


class Int:
    def read(self, context):
        return tools.read32(context.file)

class Lookup:
    def __init__(self, array, reader, default=None):
        self.array = array
        self.reader = reader
        self.default = default
        
    def read(self, context):
        index = self.reader.read(context)
        return self.lookup_index(self.default, index)

    def lookup_index(self, default, index):
        if default is None:
            default = index
        try:
            return self.array[index]
        except IndexError:
            return default
        except KeyError:    
            return default
            

class LookupList(Lookup):
    def read(self, context):
        index_list = self.reader.read(context)
        return [self.lookup_index(self.default, index) for index in index_list]


class Loop:
    def __init__(self, count_function,  reader):
        self.count_function = count_function
        self.reader = reader
        
    def read(self, context):
        result = []

        for i in range(self.count_function(context)):
            context.loop_index = i;
            result.append(self.reader.read(context))

        context.loop_index = -1        
        return result

class Bean:
    def __init__(self, factory, **kwargs):
        self.factory = factory
        self.reader = kwargs

    def read(self, context):
        bean = self.factory()
        context.objects.append(bean)
        for name, reader in self.reader.items():
            result = reader.read(context)
            setattr(bean, name, result)
        
        context.objects.pop()
        # if the bean has an after_read() method, call it after reading all properties
        if hasattr(bean, 'after_read'):
            bean.after_read(context)

        return bean


class ColonistType(Byte):
    def read(self, context):
        byte = super().read(context)
        return OCCUPATIONS[byte]


class Player(Bean):
    def __init__(self):
        super().__init__(Player, 
            name = String(24), 
            continent = String(24), 
            word1 = Word(),  # "&00" to control the power, or "&01" to let AI control it. "&02" appears related to whether the power has withdrawn, and the byte before this one appears related to diplomacy, but I'm not sure yet.
            word2 = Word())

    def __serialize__(self):
        return tools.object_attributes_to_ordered_dict(self, ["name", "continent", "word1", "word2"])

class Colonist():
    def __serialize__(self):
        tile_string = ""
        if hasattr(self, "tile"):
            tile_string = " on tile {}".format(self.tile)
        return {"text":"{0} working as {1} for {2} rounds{3}".format(self.specialization, self.occupation, self.time, tile_string)}

class Colony(Bean):
    def __init__(self):
        super().__init__(Colony, 
            x = Byte(), 
            y = Byte(), 
            name = String(24), 
            nation = Lookup(NATIONS, Byte()),
            dummy1 = Bytes(4),
            colonists_num = Byte(),
            colonists_occupation = Loop(lambda context: context.objects[-1].colonists_num, ColonistType()),
            colonists_unused_occupation = Loop(lambda context: 32-context.objects[-1].colonists_num, Byte()),
            colonists_specialization = Loop(lambda context: context.objects[-1].colonists_num, ColonistType()),
            colonists_unused_specialization = Loop(lambda context: 32-context.objects[-1].colonists_num, Byte()),
            colonists_time = Bytes(16),
            tile_usage = Bytes(8),
            dummy2 = Bytes(12),
            buildings_bitset = Bytes(6),
            customs_house = Bytes(2),
            dummy3 = Bytes(6),
            hammers = Word(),
            current_production = Lookup(BUILDINGS, Byte(), BUILDINGS[-1]),
            dummy4 = Bytes(5),
            storage = Loop(lambda _: len(GOODS), Word()),
            dummy5 = Bytes(8),
            bells = Word(),
            data = Bytes(6),
            )

    def merge_colonist_data(self):
        self.colonists = []
        for i in range(self.colonists_num):
            colonist = Colonist()
            colonist.occupation = self.colonists_occupation[i]
            colonist.specialization = self.colonists_specialization[i]
            time = self.colonists_time[i//2]
            nibbles = [time >> 4, time & 0x0F]
            colonist.time = nibbles[1 - (i % 2)]
            self.colonists.append(colonist)

        for direction_index, colonist in enumerate(self.tile_usage):
            if colonist < len(self.colonists):
                self.colonists[colonist].tile = DIRECTIONS[direction_index]

        del self.colonists_occupation
        del self.colonists_unused_occupation
        del self.colonists_specialization
        del self.colonists_unused_specialization
        del self.colonists_time
        del self.tile_usage
        
    def merge_buildings_data(self):
        buildings_bits = list(tools.stream_bits(self.buildings_bitset))
        self.buildings = [BUILDINGS[building_index] for building_index, build_flag in enumerate(buildings_bits) if build_flag == 1]
        del self.buildings_bitset
        
    def merge_goods_data(self):
        self.goods = { GOODS[goods_index] : goods_count for goods_index, goods_count in enumerate(self.storage)}
        del self.storage
        customs_house_bits = list(tools.stream_bits(self.customs_house))
        self.customs_house = [GOODS[goods_index] for goods_index, flag in enumerate(customs_house_bits) if flag == 1]
        
        
    def after_read(self, _):
        self.merge_colonist_data()
        self.merge_buildings_data()
        self.merge_goods_data()
            
    def __serialize__(self):
        return tools.object_attributes_to_ordered_dict(self, ["x", "y", "name", "nation", "dummy1", 
            "colonists_num", 
            "colonists", 
            "dummy2", 
            "buildings",
            "customs_house", 
            "dummy3", 
            "hammers", 
            "current_production", 
            "dummy4", 
            "goods", 
            "dummy5",
            "bells",
            "data"])


class Unit(Bean):
    def __init__(self):
        super().__init__(Unit, 
            x = Byte(), 
            y = Byte(), 
            type = Lookup(UNITS, Byte()),
            nation_index = Byte(),
            dummy1 = Byte(),
            used_moves = Byte(),
            dummy2 = Bytes(6),
            num_cargo = Byte(), 
            cargo_types = LookupList(GOODS, Bits(3, 4)),
            cargo_amount = Bytes(6), 
            data = Bytes(6)
            )

    def after_read(self, context):
        self.id = context.loop_index
        # swap cargo types (ony when we have cargo)
        if self.num_cargo > 0:
            self.cargo_types[0], self.cargo_types[1] = self.cargo_types[1], self.cargo_types[0]
            self.cargo_types[2], self.cargo_types[3] = self.cargo_types[3], self.cargo_types[2]
            self.cargo_types[4], self.cargo_types[5] = self.cargo_types[5], self.cargo_types[4]

        self.cargo = [(cargo_type, self.cargo_amount[index]) for index, cargo_type in enumerate(self.cargo_types[:self.num_cargo])]
        
        self.nation = NATIONS[self.nation_index & 15]
        self.dummy0 = self.nation_index >> 4
        
        del self.num_cargo
        del self.cargo_types
        del self.cargo_amount

    def __serialize__(self):
        return tools.object_attributes_to_ordered_dict(self, ["id", "x", "y", "type", "nation", "dummy0", "dummy1", "used_moves", "dummy2", "cargo", "data"])


class Savegame:
    def __serialize__(self):
        return tools.object_attributes_to_ordered_dict(self, [
            "magic", "padding1", "num_units", "num_colonies", "padding2", "royal_force", "padding3", "pos_player", 
            #"players", 
            "padding4", "pos_colonies", 
            # "colonies", "units",
            "pos",
            # europe?
            "padding5", 
            "tax_rate", 
            "next_recruits", 
            "padding6",
            "current_bells", 
            "padding7", 
            "gold", 
            "padding8", 
            "goods_price", 
            "goods_unknown", 
            "goods_balance", 
            "goods_demand", 
            "padding9", 
            "padding10", 
            ])

    def __str__(self):
        return json.dumps(self, indent=3, cls=tools.Encoder)

    
format = Bean(Savegame,
    magic = String(8), 
    padding1 = Bytes(36), 
    num_units = Word(), 
    num_colonies = Word(), 
    padding2 = Bytes(58), 
    royal_force = Loop(lambda _: 4, Word()), 
    padding3 = Bytes(44), 
    pos_player = Tell(), 
    players = Loop(lambda _: 4, Player()), 
    padding4 = Bytes(24), 
    pos_colonies = Tell(), 
    colonies = Loop(lambda context: context.objects[-1].num_colonies, Colony()), 
    units = Loop(lambda context: context.objects[-1].num_units, Unit()), 
    pos = Tell(), 
    padding5 = Bytes(1), 
    tax_rate = Byte(), 
    next_recruits = Loop(lambda _: 3, Lookup(OCCUPATIONS, Byte()),), 
    padding6 = Bytes(7), 
    current_bells = Word(), 
    padding7 = Bytes(28), 
    gold = Word(), 
    padding8 = Bytes(32), 
    goods_price = Loop(lambda _: len(GOODS), Byte()), 
    goods_unknown = Loop(lambda _: len(GOODS), Short()), 
    goods_balance = Loop(lambda _: len(GOODS), Int()), 
    goods_demand = Loop(lambda _: len(GOODS), Int()), 
    padding9 = Bytes(64), 
    padding10 = Bytes(320), 
)

def read_savegame(filename):
    with open(filename, "rb") as file:
        context = Context(file)
        savegame = format.read(context)
        print(savegame)
        




def main():
    read_savegame(sys.argv[1])

if __name__ == "__main__":
    main()
