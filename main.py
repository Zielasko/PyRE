from struct import Struct
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import sys

import FRPG.paramparser as pr
import FRPG.utils as dt
import FRPG.paramops as dop
import FRPG.formats as fm
import CE.ce as ce

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
    print("\n\n---------- [Unpacking Param] -----------\n")
    param = pr.parse_param(param_file_path,layout_path)


    if(replace_zeros!=0):
        print("[Replace Zeros] ->")
        param = dop.replaceZero(param,replace_zeros)
    if(shuffle_param_ids):
        print("[Shuffle Ids] ->")
        row_list_keep = []
        for row in rows_to_keep:
            row_index = pr.get_row_index(row,param.layout)
            row_list_keep.append(row_index)
        if(shuffle_safe):
            if(param.name=="BULLET_PARAM_ST"):
                param_pc_atk = pr.parse_param(param_path + "AtkParam_Pc.param",layout_path)
                param_npc_atk = pr.parse_param(param_path + "AtkParam_Npc.param",layout_path)
                pc_ids = param_pc_atk.data.keys()
                npc_ids = param_npc_atk.data.keys()
                if(len(self_ref_rows)>0):
                    print("[Add self references SAFE] ->")
                    param = dop.shuffle_bullet_ids_safe(param,row_list_keep,ids_to_keep,pc_ids,npc_ids,chance)
                else:
                    param = dop.shuffle_bullet_ids_safe(param,row_list_keep,ids_to_keep,pc_ids,npc_ids)
            else:
                print(f"Safe shuffle not implemented for {param.name}")
                return
        else:
            param = dop.shuffle_ids(param,row_list_keep,ids_to_keep)
    if(len(self_ref_rows)>0 and not shuffle_safe):
        print("[Add self references] ->")
        row_list_ref = []
        for row in self_ref_rows:
            index = pr.get_row_index(row,param.layout)
            row_list_ref.append(index)
        param = dop.add_random_self_refs(param,row_list_ref,chance)
    if(len(restore)>0):
        print("[Restore rows] ->")
        row_list_res = []
        for row in restore:
            index = pr.get_row_index(row,param.layout)
            row_list_res.append(index)
        default_param = pr.parse_param(param_file_path,layout_path)
        param = dop.restore_rows(param,default_param,row_list_res) #TODO its probably better to deepcopy the original param
    if(len(copy_param)>0):
        print("[Copy rows] ->")
        row_list_ignore = []
        for row in copy_ignore:
            index = pr.get_row_index(row,param.layout)
            row_list_ignore.append(index)
            print("ignore: ", row)
        second_param = pr.parse_param(copy_param[0],copy_param[1])
        param = dop.copy_param_data(param,second_param,row_list_ignore)
    #paramb = dop.restore_rows(paramb,get_param(name),0)
    if(len(limit)>0):
        print("[Limiting values] ->")
        param = dop.limit_rows(param,limit_dict)

    print("\n\n---------- [Repacking Param] -----------\n")
    param_data = pr.pack_param(param, param_file_path)

    print("[Saving param]")
    saved_file = dt.save_file(param_data,save_dir + param_name + ".param")
    if(saved_file!=None):
        print("[Done saving]")
    else:
        print("Could't save packed param to file")
    return param


def main(name="Bullet",param_path="",layout_path="",save_dir=""):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    param_data = pr.pack_param(paramb, full_param_path)

    print("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    print("Done saving")
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

    print("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    print("Done saving")
    return paramb

def shuffle_param_ids(name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)

    param_data = pr.pack_param(paramb, full_param_path)

    print("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    print("Done saving")
    return paramb

def mod_bullet_param(chance,name="Bullet"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)
    paramb = dop.add_random_self_refs(paramb,26,chance)
    paramb = dop.restore_rows(paramb,get_param(name),0)
    paramb = dop.limit_rows(paramb,{4:[0.1,5,1]})

    param_data = pr.pack_param(paramb, full_param_path)

    print("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    print("Done saving")
    return paramb

def mod_speffect_param(chance,name="SpEffectParam"):
    full_param_path = param_path + name +".param"
    paramb = pr.parse_param(full_param_path)

    paramb = dop.shuffle_ids(paramb)
    paramb = dop.add_random_self_refs(paramb,78,chance) #replacespeffectId
    #paramb = dop.restore_rows(paramb,get_param(name),0)
    #paramb = dop.limit_rows(paramb,{4:[0.1,5,1]})

    param_data = pr.pack_param(paramb, full_param_path)

    print("Saving param")
    saved_file = dt.save_file(param_data,save_dir + name + ".param")
    print("Done saving")
    return paramb




""" parse console arguments """
print("[PyRE] - Version 0.1\n")

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



parser.add_argument("-d", "--debug", dest="debug_level", default=0, help="Enable debug logging")


parser.add_argument("--shuffle", 
                    dest="shuffle_param_ids", action="store_const",
                    const=True, default=False,help="Randomly shuffle all param ids")
parser.add_argument("-k", "--keep", 
                    dest="keep", nargs="+",
                    help="Param rows to keep unchanged (name or index)")
parser.add_argument("--keep_ids", 
                    dest="ids_to_keep", nargs="+", type=int,
                    help="IDs of Param entries to keep unchanged")
parser.add_argument("--shuffle_safe", 
                    dest="shuffle_safe", action="store_const",
                    const=True, default=False,
                    help="make sure to only assign ids to other ids with a similar atkId")
parser.add_argument("--limit", 
                    dest="limit", action="append", nargs="+", type=float,
                    help="[ROW MIN MAX NEW_MIN NEW_MAX] Limits the value for the specified row. Can be used multiple times")


parser.add_argument("--random_self_refs", 
                    dest="self_refs", nargs="+",
                    help="Replace [chance * 100 %%] Zeros in the specified rows with references to the same param")
parser.add_argument("--chance", 
                    dest="chance", type=float, default=0.3,
                    help="chance [0-1] used in other options like --random_self_refs")

parser.add_argument("--replace_zeros", 
                    dest="replace_zeros", default=0,
                    help="Replace all zeros in rows with the specified value")

parser.add_argument("--restore", 
                    dest="restore", nargs="+",
                    help="Param rows to restore AFTER all other modifications were applied (name or index)")

parser.add_argument("--copy", 
                    dest="copy_param", nargs="?",
                    help="Param to copy to this one [PATH_TO_PARAM] [PATH_TO_LAYOUT_PREFIX]")
parser.add_argument("--copy_ignore", 
                    dest="copy_ignore", nargs="+",
                    help="Param rows to ignore when copying (name or index)")


parser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=True,
                    help="don't print status messages") #TODO
parser.add_argument("-i", "--interactive",
                    action="store_true", dest="interactive", default=False,
                    help="don't load or process any param files (use with interactive console)")

if(len(sys.argv)==1):
    sys.argv.append("--help")
    print(sys.argv)
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


DEBUG_LOGGING_LEVEL = d_args["debug_level"]
pr.DEBUG_LOGGING_LEVEL = DEBUG_LOGGING_LEVEL

shuffle_param_ids = d_args["shuffle_param_ids"]
rows_to_keep = d_args["keep"] #TODO handle string names 
if(rows_to_keep==None):
    rows_to_keep = []
ids_to_keep = d_args["ids_to_keep"]
if(ids_to_keep==None):
    ids_to_keep = []
shuffle_safe = d_args["shuffle_safe"]

limit = d_args["limit"]
if(limit==None):
    limit = []
limit_dict = {}
for i in range(len(limit)):
    limit_index = int(limit[i][0])
    limit_entry = [limit[i][1],limit[i][2],limit[i][3],limit[i][4]]
    limit_dict[limit_index] = limit_entry

self_ref_rows = d_args["self_refs"]
if(self_ref_rows==None):
    self_ref_rows = []
chance = d_args["chance"]

replace_zeros = d_args["replace_zeros"]

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
    print(copy_param)
    print(len(copy_param))
    if(len(copy_param)==3 and copy_param=="DS3"):
        print("Setup for copying DS3 Bullet Param")
        copy_param = [r"../../resources/DS3/" + param_name + ".param",layout_path_default]
        copy_ignore = [0,1,2,3,24,26,27,28,29,30,31,] #TODO generalise

    


VERBOSE = d_args["verbose"]
INTERACTIVE = d_args["interactive"]

if(INTERACTIVE):
    print("\n\n[Interactive Mode]\n\n")
else:
    if(param_file_path==""):
        param_file_path = param_path + param_name +".param" #Layout is handled after parsing the header

    
    if(layout_file_path==""):
        layout_file_path = ""

    param = mod_param()
