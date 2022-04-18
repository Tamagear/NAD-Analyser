from __future__ import division
from matplotlib import pyplot as plt
from prettytable import PrettyTable
from datetime import datetime
import os
import sys

invalid_sets = 0
        
path = r'D:\Projekte\NotAnotherDungeon\Pickrate Analysis\Analyser\userdata'
analyser_data_path = r'D:\Projekte\NotAnotherDungeon\Pickrate Analysis\Analyser\analyserdata'
result_save_path = r'D:\Projekte\NotAnotherDungeon\Pickrate Analysis\Analyser\output'
ignore_alexandrett = True #Set to False to also get Alexandrett's pick rates (which should be always 0).
show_plot = False #Set to True to display a plot of the faction popularity.
top_flop_count = 5 #Get the best/worst n heroes according to percentage pick and see rate.
sort_argument = "Hero Name"
faction_count = 8

os.chdir(path)

now_time = datetime.now()
now = now_time.strftime("%d.%m.%Y, %H:%M:%S")
final_filename = now_time.strftime("%d_%m_%Y_%H_%M_%S")
sys.stdout = open(result_save_path+"\output_"+final_filename+".txt", "w")

def read_file(file_path):
    xs = []
    invalid = False
    with open(file_path, 'r') as file:
        splitted = file.read().split(';')
        for tup in splitted:
            res = parse_dataset(tup)
            if res is not None:
                xs.append(res)
            else:
                invalid = True;
                break
    return (xs, invalid)
        
def parse_dataset(x):
    try:
        splitted = x.split(',')
        select = int(splitted[0])
        see = int(splitted[1])
        return (select, see)
    except:
        return None
    
def read_hero_names(file_path):
    xs = []
    with open(file_path, 'r') as file:
        splitted = file.read().split('\n')
        for entry in splitted:
            en = entry.split(',')
            factions = []
            i = 1
            while (i<len(en)):
                factions.append(int(en[i]))
                i+=1
            xs.append((en[0], factions))
    return xs

valid_data = []

for file in os.listdir():
    if file.endswith('.txt'):
        file_path=f'{path}/{file}'   
        (ls, invalid) = read_file(file_path)
        if (invalid):
            invalid_sets += 1
        else:
            valid_data.append(ls)
        
hero_data = []
for ls in valid_data:
    i = 0
    while(i<len(ls)):
        (select, see) = ls[i]
        if i < len(hero_data):
            (cur_select, cur_see) = hero_data[i]
            hero_data[i] = (cur_select + select, cur_see + see)
        else:
            difference = len(hero_data) - i + 1
            while(difference > 0):
                hero_data.append((0,0))
                difference-=1
            hero_data[i] = (select, see)
        i+=1

hero_names = []
hero_factions = []
os.chdir(analyser_data_path)
for file in os.listdir():
    if file.endswith('cardnames.txt'):
        file_path=f'{analyser_data_path}/{file}'   
        xs = read_hero_names(file_path)
        for x in xs:
            hero_names.append(x[0])
            hero_factions.append(x)

table = PrettyTable()
table.field_names = ["Hero Name", "Pick Rate (%)", "Select", "See"]
table.align = "r"
table.align["Hero Name"] = "l"

final_list = []
final_absolute_list = []

i = ignore_alexandrett
while (i<len(hero_data)):
    (select, see) = hero_data[i]
    percentage = select/see*100 if see > 0 else 0.0
    final_list.append((percentage, hero_names[i]))
    final_absolute_list.append((see, hero_names[i]))
    table.add_row([hero_names[i], "{:.3f}".format(percentage) + "%", select, see])
    i+=1
       
final_list.sort(reverse=True)
final_absolute_list.sort(reverse=True)

print("Displaying Analysis results:", now)
print("Invalid Data Sets:",invalid_sets,"of",invalid_sets+len(valid_data),"({:.2f}".format((invalid_sets/(invalid_sets+len(valid_data))*100) if invalid_sets > 0 else 0), "%)")
print("Hero Data")
print(table.get_string(sortby=sort_argument))

print("\nMost used Heroes (%)")
i = 0
while i < top_flop_count:
    print(i+1,":",final_list[i][1], "({:.2f}".format(final_list[i][0]), "%)")
    i+=1
    
print("\nLeast used Heroes (%)")
i = len(final_list)-1
while i > len(final_list)-top_flop_count - 1:
    print(len(final_list) - i, ":", final_list[i][1], "({:.2f}".format(final_list[i][0]), "%)")
    i-=1
    
print("\nMost seen Heroes")
i = 0
while i < top_flop_count:
    print(i+1,":",final_absolute_list[i][1], f"({final_absolute_list[i][0]})")
    i+=1
    
print("\nLeast seen Heroes")
i = len(final_absolute_list)-1
while i > len(final_absolute_list)-top_flop_count - 1:
    print(len(final_absolute_list) - i, ":", final_absolute_list[i][1], f"({final_absolute_list[i][0]})")
    i-=1
    
print("\nFaction popularity")
final_factions = []
i = 0
while i < faction_count:
    final_factions.append([])
    i+=1

for hero_data in hero_factions:
    for fact in hero_data[1]:
        for hd in final_list:
            if (hd[1] is hero_data[0]):
                final_factions[fact].append(hd[0])

faction_names = ["Traveller's Association", "Kingdom Infantriell", "Gazama Forest Union", \
                 "Empire Fractile", "Criminal Underworld", "Heir of the Demon Lord", \
                 "Golden Church", "Ravenfury"]

faction_table = PrettyTable()
faction_table.field_names = ["Faction", "Popularity"]
faction_table.align["Faction"] = "l"
faction_table.align["Popularity"] = "r"
    
faction_popularity = []
i = 0
for xs in final_factions:
    res = 0.0
    for x in xs:
        res += x
    try:
        res /= len(xs)
    except ZeroDivisionError:
        res = 0.0
        
    faction_popularity.append((faction_names[i],res))
    faction_table.add_row([faction_names[i],"{:.2f}".format(res) + "%"]) 
    i+=1

print(faction_table)

#Histogramm
if show_plot:
    xs = []
    ys = []
    for x,y in faction_popularity:
        xs.append(x)
        ys.append(y)
        
    plt.bar([x for x in xs], ys)
    plt.axis([min(xs), max(xs), 0, max(ys)+10])
    plt.xlabel("Faction")
    plt.ylabel("Popularity")
    plt.title("Faction Popularity")
    plt.show();
    
end_now = datetime.now() - now_time
print("\nFinished analysis in ", end_now, "seconds.\n\n---End Of File---")
sys.stdout.close()

print("Done.")