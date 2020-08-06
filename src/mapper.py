from PIL import Image

import math
import re
import tkinter as tk
from tkinter import filedialog, ttk
import threading

import population
import province
import vicmap


mod_dir_loc = ""
mod_dir = None
save_file_entry = None
save_file_loc = ""
save_file = None

map_type_entry = None
map_type = ""

global_population = 0
mean_savings = 0
sd_savings = 0
all_pops = []
test_map = None
progress = None

def split_dec(line):
    sides = line.split("=")
    return (sides[0].strip(), sides[1].strip())


def open_save(location):
    global save_file
    save_file = open(location, "r")
    

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
    

def load_UI():
    
    global progress, map_type_entry, save_file_entry, mod_dir
    
    window = tk.Tk()
    window.title("Victoria 2 Mapper")
    window.iconbitmap('Victoria2.ico')
    
    save_file_entry = tk.Entry(width=100)
    mod_dir = tk.Entry(width=100)
    
    def set_mod_dir():
        global mod_dir_loc
        mod_dir_loc = tk.filedialog.askdirectory()
        mod_dir.insert(0, mod_dir_loc)
    
    ld_mod = tk.Button(text="Choose Mod", command=set_mod_dir)
    
    def set_save_file():
        global save_file_loc
        save_file_loc = tk.filedialog.askopenfilename()
        save_file_entry.insert(0, save_file_loc)
    
    ld_save = tk.Button(text="Choose Save", command=set_save_file)
    
    map_type_entry = tk.Entry(width = 100)
    
    make_button = tk.Button(text="Make Map", command=threading.Thread(target=make_map).start)
    
    progress = tk.ttk.Progressbar()
    
    tk.Label(text="Save File:").grid(row = 0, column = 0, padx=3, pady=3)
    save_file_entry.grid(row = 0, column = 1, padx=3, pady=3)
    ld_save.grid(row = 0, column = 2, padx=3, pady=3)
    
    tk.Label(text="Mod Directory:").grid(row = 1, column = 0, padx=3, pady=3)
    mod_dir.grid(row = 1, column = 1, padx=3, pady=3)
    ld_mod.grid(row = 1, column = 2, padx=3, pady=3)
    
    tk.Label(text="Parameters:").grid(row = 2, column = 0, padx=3, pady=3)
    map_type_entry.grid(row = 2, column = 1, padx=3, pady=3)
    
    make_button.grid(row = 3, column = 1, padx=3, pady=3)
    progress.grid(row = 4, column = 1, padx=3, pady=3)
    window.mainloop()

# Map Function #

def draw_map(map_func):
    global test_map
    # Some poorly made maps have invalid colors, this uses the previous color as a backup.
    prev_color = None # Previous color used on the province map
    prev_draw = None 
    
    for x in range(vicmap.MAP_W):
        for y in range(vicmap.MAP_H):
            this_color = vicmap.pixel_map[x, y]
            if (this_color == (0, 0, 0)):
                this_color = prev_color
            this_prov = province.color_dict[this_color]
            test_map[x, vicmap.MAP_H - y - 1] = map_func(this_prov, x, y)
            prev_color = this_color


def pop_attr_map(attr):
    
    attr_dict = {
        "religion"  : population.religions,
        "culture"   : population.cultures,
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


def make_map():
    global global_population, mean_savings, sd_savings, all_pops, test_map, progress, save_file_loc, mod_dir_loc
    
    
    # Intertpret what kind of map the user wants.
    map_types = {
        "population" : (population_heatmap, 0),
        
        "total_savings" : (pop_total_savings, 0),
        "average_savings" : (pop_average_savings, 0),
        "magnitude_savings" : (pop_magnitude_savings, 0),
        
        "attr_percent" : (pop_attr_percent_map, 2),
        "attr_heatmap" : (pop_attr_heatmap, 2),
        "attr" : (pop_attr_map, 1)
    }
    
    params = map_type_entry.get().split(sep=' ')
    
    map_type_func = map_types[params[0]][0]
    map_type_param_amnt = map_types[params[0]][1]
    
    map_type_func_params = None
    
    if map_type_param_amnt == 0:
        map_type_func_params = ()
    else:
        map_type_func_params = tuple(params[1:1+map_type_param_amnt])
    
    
    population.make_pop_regex()
    progress.text = "Loading Files..."
    vicmap.load_map(mod_dir_loc + "/map/provinces.bmp")
    province.load_provinces(mod_dir_loc + "/map/definition.csv")
    population.load_culture(mod_dir_loc + "/common/cultures.txt")
    # print(population.cultures)
    
    progress.text = "Reading Save..."
    
    open_save(save_file_loc)
    read_save()
    
    progress.text = "Doing Stats..."
    
    for prov in province.provinces:
        prov.get_population()
    
    for prov in province.provinces:
        all_pops += prov.POPs
    
    global_population = sum([prov.total_pop for prov in province.provinces])
    
    mean_savings += sum([pop.money for pop in all_pops]) / global_population
    
    sd_savings = math.sqrt(sum([((pop.money / pop.size - mean_savings)**2) * pop.size for pop in all_pops]) / global_population)
    
    img = Image.new('RGB', (vicmap.MAP_W, vicmap.MAP_H), "BLACK")
    test_map = img.load()
    
    progress.text = "Drawing Map..."
    
    draw_map(map_type_func(*map_type_func_params))

    img.save("map.png")
    img.show()

load_UI()



