""" Functions for manipulating param data """
import random
import copy

import FRPG.formats as fm
import FRPG.utils as dt
import FRPG.paramparser as pr
from FRPG.utils import Logging_Level, log


def replaceZero(param,replacement_value):
    """ Replaces all zeros in any field """
    log(f"replacing all 0 with {replacement_value} for param {param.name}", Logging_Level.INFO)

    for key in param.data:
        log(f"ID: {key}", Logging_Level.INFO)
        index = 0
        for field in param.layout:
                log(f"Field: {field.name}", Logging_Level.INFO)
                log(f"Type: {field.variable_type}", Logging_Level.INFO)
                value = param.data[key][index]
                if(value==0):
                    param.data[key][index]=replacement_value
                index += 1
    return param

def replace_zero_in_field(param,replacement_value, field):
    """ Replaces all zeros in specific field """
    log(f"replacing all 0 in field {field}  with {replacement_value} for param {param.name}", Logging_Level.INFO)

    for key in param.data:
        if(param.data[key][field]==0):
            param.data[key][field]=replacement_value
            log(f"ID: {key}", Logging_Level.INFO)
    return param

def replace_zero_fields(param,dict_field_value):
    log(f"replacing all 0 in fields {dict_field_value.keys()} for param {param.name}")

    for key in param.data:
        log(f"ID: {key}")
        for field in dict_field_min_max.keys():
            log(f"Field: {field}")
            value = param.data[key][field]
            if(value==0):
                param.data[key][field]=dict_field_value[field]
    return param

def limit_fields(param,dict_field_min_max,ignore_inf=False):
    """ param, {min,max,default} 
        treats -1 as max"""
    log(f"Limiting fields {dict_field_min_max.keys()} for param {param.name}")

    for key in param.data:
        for field in dict_field_min_max.keys():
            value = param.data[key][field]
            if(dict_field_min_max[field][1] < value or (abs(value + 1.0) < 0.01 and not ignore_inf)):
                new_value = dict_field_min_max[field][3]
                param.data[key][field] = new_value
                log(f"clamped[{value} -> {new_value}]")
            if(value < dict_field_min_max[field][0] and abs(value + 1.0) > 0.01):
                new_value = dict_field_min_max[field][2]
                param.data[key][field] = new_value
                log(f"clamped[{value} -> {new_value}]")
    return param

def shuffle_ids(param,fields_to_keep,ids_to_keep,secondary_only):
    """ shuffle all ids for the specified param """
    log(f"Randomizing all ids for param {param.name}", Logging_Level.INFO)
    log(f"Excluded Fields [{fields_to_keep})", Logging_Level.INFO)
    log(f"Excluded IDs  [{ids_to_keep})", Logging_Level.INFO)

    ids = list(param.data.keys())
    random.shuffle(ids)
    log(ids[0:10], Logging_Level.DEBUG)

    secondary_ids = []
    if(secondary_only):
        secondary_ids = get_secondary_bullet_ids(param)
        log(f"secondary Hit IDs:{secondary_ids}")
        log(f"{len(secondary_ids)} of {len(param.data.keys())} bullets have hit ids", Logging_Level.DEBUG)

    param_data = param.data
    new_param_data = copy.deepcopy(param_data)
    index = 0
    for key in new_param_data:
        if(key in ids_to_keep or (secondary_only and key not in secondary_ids)):
            log(f"skipping {key}", Logging_Level.INFO)
        else:
            new_param_data[key] = param_data[ids[index]]
            log(f"Swapping ID: {key} with ID: {ids[index]}", Logging_Level.INFO)
        index += 1

    if(len(fields_to_keep)>0):
        for key in new_param_data:
            for field in fields_to_keep:
                log(f"restore field {field} for ID: {key}", Logging_Level.INFO)
                new_param_data[key][field] = param_data[key][field]
    param.data = new_param_data

    loops = check_loops(param,26) #TODO maybe add this as a flag

    return param



def add_random_self_refs(param,fields_to_change,chance=0.3):
    """ assign random ids to the specified field if the value is <0 and random > chance """
    log(f"Adding random id refs to some ids for param {param.name}")

    ids = list(param.data.keys())
    random.shuffle(ids)

    index = 0
    value_to_set = 0
    for key in param.data:
        random_chance = random.random()
        if(random_chance<=chance):
            for field in fields_to_change:
                if(param.data[key][field] > 1):
                    pass
                else:
                    value_to_set = ids[index]
                    if(value_to_set!=key):
                        index += 1
                        log(f"Set field {field} of ID: {key} to ID: {value_to_set}", Logging_Level.INFO)
                        param.data[key][field] = ids[index]
    log(f"[{index}] references added")
    return param

def multiply_random(param,fields_to_change,chance=0.3,mult_max=3, adjust_bullet_angle=False):
    """ multiply specified field for random entries if the value is <0 and random > chance """
    log(f"Mult random for param {param.name}\nMult_max{mult_max} Field{fields_to_change}", Logging_Level.INFO)

    SHOOT_ANGLE = 34
    SHOOT_ANGLE_INTERVAL = 35

    index = 0
    value_to_set = 0
    for key in param.data:
        random_chance = random.random()
        if(random_chance<=chance):
            for field in fields_to_change:
                b_multiplier = random.randint(1,mult_max)
                temp_value_to_set = int(param.data[key][field] * b_multiplier)
                log(f"Set field {field} of ID: {key} to value: {value_to_set}")
                value_to_set = max(min(temp_value_to_set,32767),-32768)
                if(value_to_set>50):
                    log(f"\n[WARNING] num_shoot > 50\n NUM:{value_to_set} (ORIGINAL: {param.data[key][field]})ID: {key}\n", Logging_Level.WARN)
                    if(value_to_set != temp_value_to_set):
                        log(f"num_shoot value outside of short", Logging_Level.WARN)
                    log(f"Value set to 50", Logging_Level.WARN)
                    value_to_set = int(50)
                param.data[key][field] = value_to_set
                if(adjust_bullet_angle and param.name=="BULLET_PARAM_ST"):
                    if(field==32):
                        old_shoot_angle = param.data[key][SHOOT_ANGLE]
                        new_shoot_angle = 0
                        old_shoot_angle_interval = param.data[key][SHOOT_ANGLE_INTERVAL]
                        if(b_multiplier%2==1):
                            if(old_shoot_angle==0):
                                new_shoot_angle = int(-3 *(b_multiplier-1)/2)
                            else:
                                new_shoot_angle = int(old_shoot_angle + (old_shoot_angle *(b_multiplier-1)/2))
                            param.data[key][SHOOT_ANGLE] = max(min(new_shoot_angle,32767),-32768)
                            if(old_shoot_angle_interval==0):
                                param.data[key][SHOOT_ANGLE_INTERVAL] = int(3)
                            #else: param.data[key][SHOOT_ANGLE_INTERVAL] = old_shoot_angle_interval
                        else:
                            #keep one shot centered
                            if(old_shoot_angle_interval==0):
                                param.data[key][SHOOT_ANGLE_INTERVAL] = int(3)
                        log(f"Adjusted angles to {param.data[key][SHOOT_ANGLE]} : {param.data[key][SHOOT_ANGLE_INTERVAL]}", Logging_Level.DEBUG)
    return param

def restore_fields(param,default_param,fields_to_restore):
    log(f"Restoring fields {fields_to_restore} for param {param.name}")

    for key in param.data:
        for field in fields_to_restore:
            old_value = param.data[key][field]
            value = default_param.data[key][field]
            log(f"Restore Field: {field} [{old_value} -> {value}]")
            param.data[key][field]=value
    return param

def copy_param_data(param,second_param,fields_to_ignore):
    log(f"Copying fields for param {param.name}")
    log(f"Ignoring {fields_to_ignore}")

    ids2 = list(second_param.data.keys())
    id_index = 0
    for key in param.data:
        field_index = 0
        for field in param.layout:
            if(field_index in fields_to_ignore):
                pass
                #log(f"Ignoring field {field.name}", Logging_Level.DEBUG)
            else:
                old_value = param.data[key][field_index]
                value = second_param.data[ids2[id_index]][field_index]
                #log(f"Restore Field: {field.name} [{old_value} -> {value}]", Logging_Level.DEBUG)
                param.data[key][field_index]=value
            field_index +=1
        id_index +=1
    log(f"{id_index} IDs replaced")
    return param

def param_intersection(param1,param2):
    ids1 = lis(param1.data.keys())
    ids2 = list(param2.data.keys())
    intersection_ids = set(ids1) & set(ids2)
    return intersection_ids

def get_param_ids_with_value_in_field(param,field,values):
    ids = []
    for id in param.data.keys():
        if(param.data[id][field] in values):
            ids.append(id)
    return ids

def get_secondary_bullet_ids(param):
    ids = []
    for id in param.data.keys():
        current_hit_id = param.data[id][26];
        if(current_hit_id>0 and current_hit_id not in ids):
            ids.append(id)
    return ids

def shuffle_bullet_ids_safe(param,fields_to_keep,ids_to_keep,atk_pc,atk_npc,secondary_only,chance=0):
    log(f"Randomizing all ids for param {param.name} (Safe Mode)")
    log(f"Excluded Fields [{fields_to_keep})")
    log(f"Excluded IDs  [{ids_to_keep})")

    atk_inter = atk_pc & atk_npc
    atk_pc_only = atk_pc - atk_npc
    atk_npc_only = atk_npc - atk_pc

    ids_pc = get_param_ids_with_value_in_field(param,0,atk_pc_only)
    ids_npc = get_param_ids_with_value_in_field(param,0,atk_npc_only)
    ids_inter = get_param_ids_with_value_in_field(param,0,atk_inter)

    secondary_ids = []
    if(secondary_only):
        secondary_ids = get_secondary_bullet_ids(param)
        log(f"secondary Hit IDs:{secondary_ids}", Logging_Level.DEBUG)
        log(f"{len(secondary_ids)} of {len(param.data.keys())} bullets have hit ids", Logging_Level.DEBUG)


    random.shuffle(ids_pc)
    random.shuffle(ids_npc)
    random.shuffle(ids_inter)

    log("ids:")
    log(ids_pc[0:10])
    log(ids_npc[0:10])
    log(ids_inter[0:10])

    param_data = param.data
    new_param_data = copy.deepcopy(param_data)
    index = 0
    for key in new_param_data:
        replacement_id = 0
        hit_id = 0
        if(key in ids_to_keep):
            log(f"skipping {key}")
        else:
            if(key in ids_inter):
                replacement_id = ids_inter[index%len(ids_inter)]
                hit_id = ids_inter[(index+1)%len(ids_inter)]
            else:
                if(key in ids_pc):
                    replacement_id = ids_pc[index%len(ids_pc)]
                    hit_id = ids_pc[(index+1)%len(ids_pc)]
                if(key in ids_npc):
                    replacement_id = ids_npc[index%len(ids_npc)]
                    hit_id = ids_npc[(index+1)%len(ids_npc)]
            if((not secondary_only) or (key in secondary_ids)):
                new_param_data[key] = param_data[replacement_id]
                log(f"Swapping ID: {key} with ID: {replacement_id}")
            if(random.random()<=chance): # and new_param_data[key][26]<=0):
                log(f"Set hitId {hit_id} for id {key}")
                new_param_data[key][26] = hit_id
        index += 1

    if(len(fields_to_keep)>0):
        for key in new_param_data:
            for field in fields_to_keep:
                log(f"restore field {field} for ID: {key}")
                new_param_data[key][field] = param_data[key][field]
    param.data = new_param_data

    log("\n\nCHECK FOR LOOPS 1\n\n")
    param = check_loops(param,26,secondary_ids,True) #TODO maybe add this as a flag
    log("\n\nCHECK FOR LOOPS AGAIN 2\n\n")
    param = check_loops(param,26,secondary_ids,True)
    log("\n\nCHECK FOR LOOPS AGAIN 3\n\n")
    param = check_loops(param,26)


    return param

def check_loops(param, field, secondary_ids=[], fix_loops=False):
    ids_checked = []
    current_chain = []
    current_id = 0
    discovered_loops = []
    longest_loop = []
    for id in param.data.keys():
        current_id = id
        if(current_id in ids_checked): #if one id was checked, all later in the chain were
            log(f"ID {current_id} was already checked (Skipped)", Logging_Level.DEBUG)
        else:
            while param.data[current_id][field] > 0:
                if(current_id in current_chain):
                    log(f"Infinite Loop [LEN {len(current_chain)}] detected for IDs:\n{current_chain}\n",Logging_Level.DEBUG)
                    discovered_loops.append(current_chain) #additionally save a list of all loops lists
                    if(len(current_chain)>len(longest_loop)):
                        longest_loop = current_chain
                    break
                else:
                    current_chain.append(current_id)
                    current_id = param.data[current_id][field]
            ids_checked.extend(current_chain)
            current_chain = []
            if(id not in ids_checked):
                ids_checked.append(id)
    if(len(discovered_loops)>0):
        log(f"Number of Loops discovered: {len(discovered_loops)}")
        log(f"Longest Loop [LEN {len(longest_loop)}]: {longest_loop}")
    else:
        log("\n\n\n\n---- [No loops found] ----\n\n\n\n")
    if(fix_loops):
        for loop in discovered_loops:
            for l_id in loop:
                if(l_id in secondary_ids or len(secondary_ids)<1):
                    param.data[l_id][field] = -1
                    log(f"set hitid for id {l_id} to -1")
                    break
        log(f"fixed {len(discovered_loops)} loops")
    return param

