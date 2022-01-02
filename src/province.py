import csv
import re
import operator

provinces = []
color_dict = {}
id_dict = {}

largest_prov_pop = 0

class Province:
    color = (0, 0, 0)
    name = "Bad_Name"
    
    def get_population(self):
        global largest_prov_pop
        self.total_pop = sum([pop.size for pop in self.POPs])
        if self.total_pop > largest_prov_pop:
            largest_prov_pop = self.total_pop
            
    def get_amnt(self, attr, kind):
        amnt = 0
        for pop in self.POPs:
            amnt += pop.size if (getattr(pop, attr) == kind) else 0
        return amnt
        
    def most_populous(self, attr):
        res_dict = {}
        
        if self.is_water:
            return ("",)
        
        for pop in self.POPs:
            found_attr = getattr(pop, attr)
            if found_attr in res_dict:
                res_dict[found_attr] += pop.size
            else:
                res_dict[found_attr] = pop.size
        
        if len(res_dict) == 0:
            return ("",)
        res_out = (max(res_dict, key=res_dict.get),)
        if len(res_dict) > 1:
            second_largest = sorted(res_dict.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)[1]
            if second_largest[1] > (.33 * self.total_pop):
                res_out = (max(res_dict, key=res_dict.get), second_largest[0])
            else:
                res_out = (max(res_dict, key=res_dict.get),)
        return res_out
    
    def __init__(self, info_arr):
        global color_dict
        global id_dict
        self.prov_id = int(info_arr[0])
        
        self.POPs = []
        self.total_pop = 0
        self.battle_deaths = 0
        
        # In base vic2's defines.csv Zouar has a color with a . at the end for some reason?
        self.color = (int(info_arr[1]), int(info_arr[2]), int(info_arr[3].replace('.', '')))
        self.name = info_arr[4]
        self.is_water = False
        color_dict[self.color] = self
        id_dict[self.prov_id] = self
        
    def __str__(self):
        return f"{self.prov_id}: {self.color}, {self.name}, {self.is_water}"
        

def split_dec(line):
    sides = line.split("=")
    return (sides[0].strip(), sides[1].strip())
    
def make_battle(fiter):
    fiter.__next__()
    fiter.__next__()
    location = id_dict[int(split_dec(fiter.__next__())[1])]
    belligerents = 0
    while belligerents < 2:
        line = fiter.__next__()
        if bool(re.search("losses", line)):
            belligerents += 1
            location.battle_deaths += int(split_dec(line)[1])

def load_provinces(location):
    global provinces
    prov_file = open(location, encoding='iso-8859-1')
    prov_csv = csv.reader(prov_file, delimiter=';')
    prov_csv.__next__() # Skip header
    provinces = [Province(row) for row in prov_csv]
    
def get_most(attr, kind):
    most = 0
    for prov in provinces:
        amnt = prov.get_amnt(attr, kind)
        if amnt > most:
            most = amnt
    return most

