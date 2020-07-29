from PIL import Image

import math
import re
from functools import reduce

import population
import province
import vicmap


save_file = None

def split_dec(line):
    sides = line.split("=")
    return (sides[0].strip(), sides[1].strip())


def open_save():
    global save_file
    save_file = open("test_save.v2", "r")
    

def read_save():
    global save_file
    i = 0
    current_prov = None
    for line in save_file:
        i = i + 1
        if bool(re.search("^\d+=$", line)):
            current_prov = int(split_dec(line)[0])
            save_file.__next__()
            save_file.__next__()
            save_file.__next__()
            line = save_file.__next__()
            if line.strip() == "}":
                province.id_dict[current_prov].is_water = True
        elif bool(re.search(population.pop_regex, line.strip())):
            population.POP(save_file, current_prov, split_dec(line)[0])
    print(i)
    
def make_map(map_func):
    global test_map
    # Some poorly made maps have invalid colors, this uses the previous color as a backup.
    prev_color = None
    
    for x in range(vicmap.MAP_W):
        for y in range(vicmap.MAP_H):
            this_color = vicmap.pixel_map[x, y]
            if (vicmap.pixel_map[x, y] == (0, 0, 0)):
                this_color = prev_color
            else:
                prev_color = vicmap.pixel_map[x, y]
            
            this_prov = province.color_dict[this_color]
            
            test_map[x, vicmap.MAP_H - y - 1] = map_func(this_prov, x, y)


def pop_attr_map(attr):
    
    attr_dict = {
        "religion"  : population.religions,
        "kind"      : population.pop_types
    }
    attr_list = attr_dict[attr]
    
    def out_func(this_prov, x, y):
        out_colors = ((0, 0, 0),)
        if this_prov.is_water:
            return (255, 255, 255)
        rel_tuple = this_prov.most_populous(attr)
        out_colors = (attr_list[rel_tuple[0]], attr_list[rel_tuple[-1]])
        
        if len(out_colors) > 1 and (x + y) % 5 == 0:
            return out_colors[1]
        else:
            return out_colors[0]
    return out_func

def pop_attr_heatmap(attr, kind):
    
    most = province.get_most(attr, kind)
    
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        return (int(255 * (this_prov.get_amnt(attr, kind)/most)), 0, 0)
        
    return out_func


def pop_attr_percent_map(attr, kind):
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        if this_prov.total_pop == 0:
            return (0, 0, 0)
        return (int(255 * (this_prov.get_amnt(attr, kind)/this_prov.total_pop)), 0, 0)
        
    return out_func
    
def pop_average_savings():
    most = 0
    
    for prov in province.provinces:
        if not prov.is_water and prov.total_pop > 0:
            prov.avg_savings = sum([pop.money for pop in prov.POPs]) / prov.total_pop
            most = prov.avg_savings if prov.avg_savings > most else most
    print(most)
    
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        if this_prov.total_pop == 0:
            return (0, 0, 0)
        return (int(255 * (this_prov.avg_savings/most)), 0, 0)
    return out_func

def pop_magnitude_savings():
    most = 0
    for prov in province.provinces:
        if not prov.is_water and prov.total_pop > 0:
            prov.mag_savings = ((sum([pop.money for pop in prov.POPs]) / prov.total_pop) - mean_savings) / sd_savings
            most = prov.mag_savings if prov.mag_savings > most else most
    print(most)
    
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        if this_prov.total_pop == 0:
            return (0, 0, 0)
        
        
        
        if this_prov.mag_savings < 0:
            return (255, 0, 0)
        return (0, 255, 0)
    return out_func


def pop_total_savings():
    most = 0
    
    for prov in province.provinces:
        if not prov.is_water and prov.total_pop > 0:
            prov.total_savings = sum([pop.money for pop in prov.POPs])
            most = prov.total_savings if prov.total_savings > most else most
    
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        if this_prov.total_pop == 0:
            return (0, 0, 0)
        
        return (int(255 * (this_prov.total_savings/most)), 0, 0)
    return out_func

def population_heatmap():
    def out_func(this_prov, x, y):
        if this_prov.is_water:
            return (255, 255, 255)
        return (int(255*(this_prov.total_pop/province.largest_prov_pop)), 0, 0)
    return out_func

population.make_pop_regex()

print(population.pop_regex)

vicmap.load_map("C:\Program Files (x86)\Steam\steamapps\common\Victoria 2\mod\PDXMP-2\map\provinces.bmp")
province.load_provinces("C:\Program Files (x86)\Steam\steamapps\common\Victoria 2\mod\PDXMP-2\map\definition.csv")

open_save()
read_save()

for prov in province.provinces:
    prov.get_population()

global_population = 0
for prov in province.provinces:
    global_population += prov.total_pop

mean_savings = 0
for prov in province.provinces:
    mean_savings += sum([pop.money for pop in prov.POPs])
mean_savings = mean_savings / global_population

all_pops = []
for prov in province.provinces:
    all_pops += prov.POPs

sd_savings = math.sqrt(sum([((pop.money / pop.size - mean_savings)**2) * pop.size for pop in all_pops]) / global_population)

img = Image.new('RGB', (vicmap.MAP_W, vicmap.MAP_H), "BLACK")
test_map = img.load()

make_map(pop_attr_percent_map("religion", "sunni"))

img.save("map.png")
img.show()