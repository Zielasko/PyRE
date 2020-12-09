from struct import Struct
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

import FRPG.paramparser as pr
import FRPG.utils as dt
import FRPG.paramops as dop
import FRPG.formats as fm
import CE.ce as ce

from FRPG.utils import Logging_Level, log, set_LOG_LEVEL

param_path_default = r"../resources/GameParam/"
layout_path_default = r"../resources/Layouts/"
save_dir_default = r"../resources/savedParams/"

param_path = ""
layout_path = ""
save_dir = ""

param_name = ""
param_file_path = ""
layout_file_path = ""


def mod_param():
    log("\n\n---------- [Unpacking Param] -----------\n", Logging_Level.INFO)
    param = pr.parse_param(param_file_path,layout_path)


    if(replace_zeros!=0):
        log("[Replace Zeros] ->", Logging_Level.INFO)
        param = dop.replace_zero(param,replace_zeros)
    if(shuffle_param_ids):
        log("[Shuffle Ids] ->", Logging_Level.INFO)
        field_list_keep = []
        for field in fields_to_keep:
            field_index = pr.get_field_index(field,param.layout)
            field_list_keep.append(field_index)
        if(shuffle_safe):
            if(param.name=="BULLET_PARAM_ST"):
                param_pc_atk = pr.parse_param(param_path + "AtkParam_Pc.param",layout_path)
                param_npc_atk = pr.parse_param(param_path + "AtkParam_Npc.param",layout_path)
                pc_ids = param_pc_atk.data.keys()
                npc_ids = param_npc_atk.data.keys()
                if(len(self_ref_fields)>0):
                    log("[Add self references SAFE] ->")
                    param = dop.shuffle_bullet_ids_safe(param,field_list_keep,ids_to_keep,pc_ids,npc_ids,secondary_only,chance)
                else:
                    param = dop.shuffle_bullet_ids_safe(param,field_list_keep,ids_to_keep,pc_ids,npc_ids,secondary_only)
            else:
                log(f"Safe shuffle not implemented for {param.name}")
                return
        else:
            param = dop.shuffle_ids(param,field_list_keep,ids_to_keep,secondary_only)
    if(len(self_ref_fields)>0 and not shuffle_safe):
        log("[Add self references] ->")
        field_list_ref = []
        for field in self_ref_fields:
            index = pr.get_field_index(field,param.layout)
            field_list_ref.append(index)
        param = dop.add_random_self_refs(param,field_list_ref,chance)
    if(len(rand_bullet_mult_fields)>0):
        log("[Multiply random fields] ->")
        field_list_mult_ref = []
        for field in rand_bullet_mult_fields:
            index = pr.get_field_index(field,param.layout)
            field_list_mult_ref.append(index)
        param = dop.multiply_random(param,field_list_mult_ref,chance,mult_max,adjust_bullet_angle)
    if(make_bullets_visible>0 and param.name=="BULLET_PARAM_ST"):
        log("[Add SFX to invisible bullets] ->")
        param = dop.replace_zero_in_field(param,make_bullets_visible,1)
    if(len(restore)>0):
        log("[Restore fields] ->")
        field_list_res = []
        for field in restore:
            index = pr.get_field_index(field,param.layout)
            field_list_res.append(index)
        default_param = pr.parse_param(param_file_path,layout_path)
        param = dop.restore_fields(param,default_param,field_list_res) #TODO its probably better to deepcopy the original param
    if(len(copy_param)>0):
        log("[Copy fields] ->")
        field_list_ignore = []
        for field in copy_ignore:
            index = pr.get_field_index(field,param.layout)
            field_list_ignore.append(index)
            log("ignore: ", field)
        second_param = pr.parse_param(copy_param[0],copy_param[1])
        param = dop.copy_param_data(param,second_param,field_list_ignore)
    #paramb = dop.restore_fields(paramb,get_param(name),0)
    if(len(limit)>0):
        log("[Limiting values] ->")
        param = dop.limit_fields(param,limit_dict)

    log("\n\n---------- [Repacking Param] -----------\n")
    param_data = pr.pack_param(param, param_file_path)

    log("[Saving param]")
    saved_file = dt.save_file(param_data,save_dir + param_name + ".param")
    if(saved_file!=None):
        log("[Done saving]")
    else:
        log("Couldn't save packed param to file", Logging_Level.ERROR)
    return param


def main(name="Bullet",param_path="",layout_path="",save_dir=""):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    param_data = pr.pack_param(paramb, full_param_path)

    log("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    log("Done saving")
    return paramb

#paramb = main()

def get_param(name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)
    return paramb

def alter_params(name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.replaceZero(paramb,1)

    param_data = pr.pack_param(paramb, full_param_path)

    log("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    log("Done saving")
    return paramb

def shuffle_param_ids(name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)

    param_data = pr.pack_param(paramb, full_param_path)

    log("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    log("Done saving")
    return paramb

def mod_bullet_param(chance,name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)
    paramb = dop.add_random_self_refs(paramb,26,chance)
    paramb = dop.restore_fields(paramb,get_param(name),0)
    paramb = dop.limit_fields(paramb,{4:[0.1,5,1]})

    param_data = pr.pack_param(paramb, full_param_path)

    log("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    log("Done saving")
    return paramb

def mod_speffect_param(chance,name="SpEffectParam"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)
    paramb = dop.add_random_self_refs(paramb,78,chance) #replacespeffectId
    #paramb = dop.restore_fields(paramb,get_param(name),0)
    #paramb = dop.limit_fields(paramb,{4:[0.1,5,1]})

    param_data = pr.pack_param(paramb, full_param_path)

    log("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    log("Done saving")
    return paramb




""" parse console arguments """
print("[PyRE] - Version 0.9\n")

help_message = "What params shall i parse today?\n\n" \
                + "Default settings if not otherwise specified:\n"     \
                + f"Path to Param Directory:  {param_path_default}\n"   \
                + f"Path to Layout Directory: {layout_path_default}\n" \
                + f"Path to Output Directory: {save_dir_default}\n"
parser = ArgumentParser(description=help_message)
parser.formatter_class = RawDescriptionHelpFormatter
parser.add_argument("-n", "--name", "--param", dest="param_name", default="Bullet",
                    help="Name of the Param to use", metavar="name")
parser.add_argument("-p", "--path", dest="param_path", default=param_path_default,
                    help="Path to directory with param files (GameParam)", metavar="path")
parser.add_argument("-l", "--layout", dest="layout_path", default=layout_path_default,
                    help="Path to directory with xml Layout files", metavar="path")
parser.add_argument("-o", "--out", dest="out_path", default=save_dir_default,
                    help="Output Directory (file name is set automatically)", metavar="path")     
#Alternative
parser.add_argument("-fp", "--file", dest="param_filename", default="",
                    help="Param file to use (instead of path + name)", metavar="file")
parser.add_argument("-fl", "--file_layout", dest="layout_filename", default="",
                    help="Layout file to use (instead of path + name) NOT SUPPORTET YET", metavar="file")



parser.add_argument("-d", "--debug", dest="debug_level", action="store_const", 
                    const=True, default=False, help="Enable debug logging")
parser.add_argument("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="don't print status messages")
parser.add_argument("-v", "--verbosity","--logging_level",
                    dest="verbosity", type=int, default=2,
                    help="Logging level which controls the amount and detail of information printed")



parser.add_argument("--shuffle", 
                    dest="shuffle_param_ids", action="store_const",
                    const=True, default=False,help="Randomly shuffle all param ids")
parser.add_argument("-k", "--keep", 
                    dest="keep", nargs="+",
                    help="Param fields to keep unchanged (name or index)")
parser.add_argument("--keep_ids", 
                    dest="ids_to_keep", nargs="+", type=int,
                    help="IDs of Param entries to keep unchanged")
parser.add_argument("--shuffle_safe", 
                    dest="shuffle_safe", action="store_const",
                    const=True, default=False,
                    help="make sure to only assign ids to other ids with a similar atkId")
parser.add_argument("--secondary_only", 
                    dest="shuffle_secondary_only", action="store_const",
                    const=True, default=False,
                    help="only shuffle IDs that are spawned as a hitid by other bullets")
parser.add_argument("--limit", 
                    dest="limit", action="append", nargs="+", type=float,
                    help="[FIELD MIN MAX NEW_MIN NEW_MAX] Limits the value for the specified field. Can be used multiple times")


parser.add_argument("--random_self_refs", 
                    dest="self_refs", nargs="+",
                    help="Replace [chance * 100 %%] Zeros in the specified fields with references to the same param")
parser.add_argument("--chance", 
                    dest="chance", type=float, default=0.3,
                    help="chance [0-1] used in other options like --random_self_refs")
parser.add_argument("--random_bullet_multiplier", 
                    dest="rand_bullet_mult", nargs="+",
                    help="Multiply [chance * 100 %%] values in the specified fields by up to [mult_max]")
parser.add_argument("--mult_max", 
                    dest="mult_max", type=int, default=3,
                    help="maximum for rand_bullet_mult")
parser.add_argument("--adjust_bullet_angle", 
                    dest="adjust_bullet_angle", action="store_const",
                    const=True, default=False,
                    help="adjust bullet angle when multiplying bullet_num to fire in a fan shape")

parser.add_argument("--replace_zeros", 
                    dest="replace_zeros", default=0,
                    help="Replace all zeros in fields with the specified value")
parser.add_argument("--visible_bullets", 
                    dest="make_bullets_visible", type=int, default=0,
                    help="make all invisible bullets visible by replacing any 0 bullet SFX ID with the specified value (1 = debug sfx)")

parser.add_argument("--restore", 
                    dest="restore", nargs="+",
                    help="Param fields to restore AFTER all other modifications were applied (name or index)")

parser.add_argument("--copy", 
                    dest="copy_param", nargs="?",
                    help="Param to copy to this one [PATH_TO_PARAM] [PATH_TO_LAYOUT_PREFIX]")
parser.add_argument("--copy_ignore", 
                    dest="copy_ignore", nargs="+",
                    help="Param fields to ignore when copying (name or index)")


parser.add_argument("-i", "--interactive",
                    action="store_true", dest="interactive", default=False,
                    help="don't load or process any param files (use with interactive console)")

if(len(sys.argv)==1):
    sys.argv.append("--help")
    log(sys.argv)
args = parser.parse_args()
d_args = vars(args)

""" read arguments """
param_name = d_args["param_name"]
param_path = d_args["param_path"]
layout_path = d_args["layout_path"]
save_dir = d_args["out_path"]
# Alternative
param_file_path = d_args["param_filename"]
layout_file_path = d_args["layout_filename"]

set_LOG_LEVEL(d_args["verbosity"])

if(bool(d_args["debug_level"])):
    set_LOG_LEVEL(Logging_Level.DEBUG)
else:
    if(bool(d_args["quiet"])):
       set_LOG_LEVEL(Logging_Level.ERROR)




shuffle_param_ids = d_args["shuffle_param_ids"]
fields_to_keep = d_args["keep"] #TODO handle string names 
if(fields_to_keep==None):
    fields_to_keep = []
ids_to_keep = d_args["ids_to_keep"]
if(ids_to_keep==None):
    ids_to_keep = []
shuffle_safe = d_args["shuffle_safe"]
secondary_only = d_args["shuffle_secondary_only"]

limit = d_args["limit"]
if(limit==None):
    limit = []
limit_dict = {}
for i in range(len(limit)):
    limit_index = int(limit[i][0])
    limit_entry = [limit[i][1],limit[i][2],limit[i][3],limit[i][4]]
    limit_dict[limit_index] = limit_entry

self_ref_fields = d_args["self_refs"]
if(self_ref_fields==None):
    self_ref_fields = []
chance = d_args["chance"]

rand_bullet_mult_fields = d_args["rand_bullet_mult"]
if(rand_bullet_mult_fields==None):
    rand_bullet_mult_fields = []
mult_max = max(d_args["mult_max"],1)
adjust_bullet_angle = d_args["adjust_bullet_angle"]

replace_zeros = d_args["replace_zeros"]
make_bullets_visible = d_args["make_bullets_visible"]

restore = d_args["restore"]
if(restore==None):
    restore = []

copy_param = d_args["copy_param"]
copy_ignore = d_args["copy_ignore"]
if(copy_ignore==None):
    copy_ignore = []
if(copy_param==None):
    copy_param = []
else:
    log(copy_param)
    log(len(copy_param))
    if(len(copy_param)==3 and copy_param=="DS3"):
        log("Setup for copying DS3 Bullet Param")
        copy_param = [r"../../resources/DS3/" + param_name + ".param",layout_path_default]
        copy_ignore = [0,1,2,3,24,26,27,28,29,30,31,] #TODO generalise

    

INTERACTIVE = d_args["interactive"]

if(INTERACTIVE):
    log("\n\n[Interactive Mode]\n\n")
else:
    if(param_file_path==""):
        param_file_path = param_path + param_name +".param" #Layout is handled after parsing the header

    
    if(layout_file_path==""):
        layout_file_path = ""

    param = mod_param()
