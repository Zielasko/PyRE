""" Functions for manipulating param data """
import random
import copy

import FRPG.formats as fm
import FRPG.utils as dt
import FRPG.paramparser as pr




def replaceZero(param,replacement_value):
    """ Replaces all zeros in any row """
    print(f"replacing all 0 with {replacement_value} for param {param.name}")

    for key in param.data:
        print(f"ID: {key}")
        index = 0
        for row in param.layout:
                print(f"Row: {row.name}")
                print(f"Type: {row.variable_type}")
                value = param.data[key][index]
                if(value==0):
                    param.data[key][index]=replacement_value
                index += 1
    return param
    
def shuffle_ids(param,rows_to_keep,ids_to_keep):
    """ shuffle all ids for the specified param """
    print(f"Randomizing all ids for param {param.name}")
    print(f"Excluded Rows [{rows_to_keep})")
    print(f"Excluded IDs  [{ids_to_keep})")

    ids = list(param.data.keys())
    random.shuffle(ids)
    print(ids[0:10])

    param_data = param.data
    new_param_data = copy.deepcopy(param_data)
    index = 0
    for key in new_param_data:
        print(f"Swapping ID: {key} with ID: {ids[index]}")
        if(key in ids_to_keep):
            print(f"skipping {key}")
        else:
            new_param_data[key] = param_data[ids[index]]
        index += 1

    if(len(rows_to_keep)>0):
        for key in new_param_data:
            for row in rows_to_keep:
                print(f"restore row {row} for ID: {key}")
                new_param_data[key][row] = param_data[key][row]
    param.data = new_param_data
    return param



def add_random_self_refs(param,rows_to_change,chance=0.3):
    """ assign random ids to the specified row if the value is <0 and random > chance """
    print(f"Adding random id refs to some ids for param {param.name}")

    ids = list(param.data.keys())
    random.shuffle(ids)

    index = 0
    value_to_set = 0
    for key in param.data:
        random_chance = random.random()
        if(random_chance<=chance):
            for row in rows_to_change:
                if(param.data[key][row] > 1):
                    pass
                else:
                    value_to_set = ids[index]
                    if(value_to_set!=key):
                        index += 1
                        print(f"Set row {row} of ID: {key} to ID: {value_to_set}")
                        param.data[key][row] = ids[index]
    print(f"[{index}] references added")
    return param

def replace_zero_rows(param,dict_row_value):
    print(f"replacing all 0 in rows {dict_row_value.keys()} for param {param.name}")

    for key in param.data:
        print(f"ID: {key}")
        for row in dict_row_min_max.keys():
            print(f"Row: {row}")
            value = param.data[key][row]
            if(value==0):
                param.data[key][row]=dict_row_value[row]
    return param

def limit_rows(param,dict_row_min_max):
    """ param, {min,max,default} """
    print(f"Limiting rows {dict_row_min_max.keys()} for param {param.name}")

    for key in param.data:
        for row in dict_row_min_max.keys():
            value = param.data[key][row]
            if(dict_row_min_max[row][1] < value or value == -1):
                new_value = dict_row_min_max[row][3]
                param.data[key][row] = new_value
                print(f"clamped[{value} -> {new_value}]")
            if(value < dict_row_min_max[row][0] and value != -1):
                new_value = dict_row_min_max[row][2]
                param.data[key][row] = new_value
                print(f"clamped[{value} -> {new_value}]")
    return param

def restore_rows(param,default_param,rows_to_restore):
    print(f"Restoring rows {rows_to_restore} for param {param.name}")

    for key in param.data:
        for row in rows_to_restore:
            old_value = param.data[key][row]
            value = default_param.data[key][row]
            print(f"Restore Row: {row} [{old_value} -> {value}]")
            param.data[key][row]=value
    return param

def copy_param_data(param,second_param,rows_to_ignore):
    print(f"Copying rows for param {param.name}")
    print(f"Ignoring {rows_to_ignore}")

    ids2 = list(second_param.data.keys())
    id_index = 0
    for key in param.data:
        row_index = 0
        for row in param.layout:
            if(row_index in rows_to_ignore):
                pass
                #print(f"Ignoring row {row.name}")
            else:
                old_value = param.data[key][row_index]
                value = second_param.data[ids2[id_index]][row_index]
                #print(f"Restore Row: {row.name} [{old_value} -> {value}]")
                param.data[key][row_index]=value
            row_index +=1
        id_index +=1
    print(f"{id_index} IDs replaced")
    return param

def param_intersection(param1,param2):
    ids1 = lis(param1.data.keys())
    ids2 = list(param2.data.keys())
    intersection_ids = set(ids1) & set(ids2)
    return intersection_ids

def get_param_ids_with_value_in_row(param,row,values):
    ids = []
    for id in param.data.keys():
        if(param.data[id][row] in values):
            ids.append(id)
    return ids

def shuffle_bullet_ids_safe(param,rows_to_keep,ids_to_keep,atk_pc,atk_npc,chance=0):
    print(f"Randomizing all ids for param {param.name}")
    print(f"Excluded Rows [{rows_to_keep})")
    print(f"Excluded IDs  [{ids_to_keep})")

    atk_inter = atk_pc & atk_npc
    atk_pc_only = atk_pc - atk_npc
    atk_npc_only = atk_npc - atk_pc

    ids_pc = get_param_ids_with_value_in_row(param,0,atk_pc_only)
    ids_npc = get_param_ids_with_value_in_row(param,0,atk_npc_only)
    ids_inter = get_param_ids_with_value_in_row(param,0,atk_inter)


    random.shuffle(ids_pc)
    random.shuffle(ids_npc)
    random.shuffle(ids_inter)

    print("ids:")
    print(ids_pc[0:10])
    print(ids_npc[0:10])
    print(ids_inter[0:10])

    param_data = param.data
    new_param_data = copy.deepcopy(param_data)
    index = 0
    for id in new_param_data.keys():
        replacement_id = 0
        hit_id = 0
        if(id in ids_to_keep):
            print(f"skipping {key}")
        else:
            if(id in ids_inter):
                replacement_id = ids_inter[index%len(ids_inter)]
                hit_id = ids_inter[(index+1)%len(ids_inter)]
            else:
                if(id in ids_pc):
                    replacement_id = ids_pc[index%len(ids_pc)]
                    hit_id = ids_pc[(index+1)%len(ids_pc)]
                if(id in ids_npc):
                    replacement_id = ids_npc[index%len(ids_pc)]
                    hit_id = ids_npc[(index+1)%len(ids_npc)]
            print(f"Swapping ID: {id} with ID: {replacement_id}")
            new_param_data[id] = param_data[replacement_id]
            if(random.random()<=chance and new_param_data[id][26]<=0):
                print(f"Set hitId {hit_id} for id {id}")
                new_param_data[id][26] = hit_id

        index += 1

    if(len(rows_to_keep)>0):
        for id in new_param_data.keys():
            for row in rows_to_keep:
                print(f"restore row {row} for ID: {id}")
                new_param_data[id][row] = param_data[id][row]
    param.data = new_param_data
    return param



