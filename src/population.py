
import province
import re

pop_types = {
    "aristocrats"   : (11, 40, 93), 
    "artisans"      : (127, 3, 3), 
    "bureaucrats"   : (136, 136, 136), 
    "capitalists"   : (18, 129, 10), 
    "clergymen"     : (234, 227, 40), 
    "clerks"        : (240, 240, 240), 
    "craftsmen"     : (12, 157, 162), 
    "farmers"       : (75, 193, 237), 
    "labourers"     : (189, 57, 36), 
    "officers"      : (119, 98, 34), 
    "serfs"         : (63, 80, 62), 
    "slaves"        : (17, 17, 17), 
    "soldiers"      : (200, 187, 157),
    
    ""              : (0, 0, 0)
}

pop_regex = ""


def rgbf(r, g, b):
    return (int(r*255), int(g*255), int(b*255))
    
religions = {
    "catholic"      : rgbf(0.8, 0.8, 0.0),
    "protestant"    : rgbf(0.0, 0.0, 0.7),
    "orthodox"      : rgbf(0.7, 0.5, 0.0),
    "coptic"        : rgbf(0.0, 0.5, 0.7),
    
    "sunni"         : rgbf(0.0, 0.6, 0.0),
    "shiite"        : rgbf(0.0, 0.8, 0.0),
    "jewish"        : rgbf(0.3, 0.5, 0.3),
    
    "mahayana"      : rgbf(0.8, 0.3, 0.0),
    "gelugpa"       : rgbf(0.0, 0.3, 0.8),
    "theravada"     : rgbf(0.8, 0.0, 0.8),
    "hindu"         : rgbf(0.0, 0.8, 0.8),
    "shinto"        : rgbf(0.8, 0.0, 0.0),
    "sikh"          : rgbf(0.3, 0.8, 0.0),
    
    "animist"       : rgbf(0.5, 0.0, 0.0),
    
    "mormon"        : rgbf(0.0, 0.0, 0.5),
    "ibadi"         : rgbf(0.1, 0.4, 0.6),
    "druze"         : rgbf(0.7, 0.8, 0.6),
    "yazidi"        : rgbf(0.4, 0.0, 1.0),
    
    "taiping"       : rgbf(0.5, 0.5, 0.0),
    "assyrian"      : rgbf(0.0, 0.5, 0.7),
    "zoroastrian"   : rgbf(0.7, 0.2, 0.1),
    "jain"          : rgbf(0.0, 0.1, 0.0),
    "inti"          : rgbf(0.6, 0.7, 0.6),
    "fetishist"     : rgbf(0.419, 0.247, 0.627),
    
    ""              : rgbf(0.0, 0.0, 0.0) # Empty religion -- Something fucked up
}

cultures = {
    ""              : (0, 0, 0)
}

def split_dec(line):
    sides = line.split("=")
    return (sides[0].strip(), sides[1].strip())

def make_pop_regex():
    global pop_types, pop_regex
    pop_regex = "^("
    pop_keys = list(pop_types.keys())
    for i in range(len(pop_keys)-2):
        pop_regex += pop_keys[i] + "|"
    pop_regex += pop_keys[len(pop_keys)-2]
    pop_regex += ")="

def load_culture(cultures_loc):
    cultures_file = open(cultures_loc, "r")
    bracket_stack = 0
    current_culture = ""
    for line in cultures_file:
        if bracket_stack == 1:
            t_line = line[0:line.find('#')].strip()
            if re.search("{", t_line):
                current_culture = split_dec(t_line)[0]
        elif bracket_stack == 2:
            t_line = line[0:line.find('#')].strip()
            if re.search("color", t_line):
                cultures[current_culture] = tuple(map(int, filter( lambda x: x!="",t_line[t_line.find("{")+1 : t_line.find("}")].split(sep=" "))))
        
        if re.search("{", line):
            bracket_stack += 1
        if re.search("}", line):
            bracket_stack -= 1

class POP:
    
    def __init__(self, fiter, current_prov, kind):
        self.kind = kind
        fiter.__next__()
        line = fiter.__next__()
        self.pop_id = int(split_dec(line)[1])
        line = fiter.__next__()
        self.size = int(split_dec(line)[1])
        line = fiter.__next__()
        self.culture = split_dec(line)[0]
        self.religion = split_dec(line)[1]
        line = fiter.__next__()
        self. money = float(split_dec(line)[1])
        province.id_dict[current_prov].POPs.append(self)
        if (province.id_dict[current_prov].is_water):
            province.id_dict[current_prov].is_water = False
    
    def __str__(self):
        return f"{self.pop_id}: {self.kind} {self.culture}, {self.religion} (${self.money})\t{self.size}"