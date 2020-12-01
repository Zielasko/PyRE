from struct import Struct
from enum import Enum

import FRPG.formats as fm
import FRPG.utils as dt
from FRPG.formats import Logging_Level, log #TODO cleanup imports

HEADER_END = 0x40

START_OF_PARAM_DATA_PTR = 0x30
NAME_OFFSET_PTR = 0x10


HEADER_FORMAT_STRING = "<8Q"
ID_OFFSET_FORMAT_STRING = "<3Q"


def create_param_from_layout(layout_path,name,entry_size):
    fields = fm.layout2ParamFields(layout_path)
    end_of_layout = fields[-1].offset+fields[-1].length+fm.type_size[fields[-1].variable_type] #TODO + 1 + 1 fix this something is off by one here
    if(end_of_layout + 2<entry_size):
        unknown_data_field = fm.Param_Field("Unknown", fm.Data_type.AoB.value,(end_of_layout),entry_size-end_of_layout) #create additional field for remaining unknown data
        fields.append(unknown_data_field)
    if(end_of_layout>entry_size):
        log("layout_doesnt match entry size read from param file", Logging_Level.WARN)
        log(f"layout size {end_of_layout} - entry_size {entry_size}", Logging_Level.WARN)
        return
    param = fm.Param(name,entry_size,fields)
    return param

def get_field_index(field,layout):
    index = 0
    try:
        index = int(field)
    except ValueError:
        for l_field in layout:
            if(l_field.name==field):
                break
            index += 1
    return index


def parse_param_header(data):
    """ unpack and parse the header of the param file """
    header_data = ""
    header_data = data[0:HEADER_END]
    log(header_data,Logging_Level.ALL)
    header_struct = Struct(HEADER_FORMAT_STRING)
    header = header_struct.unpack(header_data)

    return header


def parse_id_list(data):
    """ parse id - offset list """
    id_list = []
    id_list_struct = Struct(ID_OFFSET_FORMAT_STRING)
    number_of_ids = ((len(data)/8)/3)
    log(number_of_ids)
    if((number_of_ids-int(number_of_ids))>0.01):
        log("ERROR: ID data is not divisible by 3", Logging_Level.ERROR)
        return

    for i in range(int(number_of_ids)):
        current_offset = i*3*8
        current_data = data[current_offset:current_offset+3*8]
        c_id,c_offset,c_unkwn = id_list_struct.unpack(current_data)
        id_list.append((c_id,c_offset))
    return id_list


def parse_param(param_file_path,layout_path_prefix):
    """ read param file from disk, unpack and parse it """
    log("Unpacking Param ...")
    data = dt.open_file(param_file_path)

    header = parse_param_header(data)

    id_end = header[int(0x30/8)]
    entry_end = header[int(0x10/8)]

    id_data = data[HEADER_END:id_end]
    entry_data = data[id_end:entry_end]
    name_data = data[entry_end:]
    name = dt.convert_to_ascii_string(name_data)

    """ parse id - offset list """
    id_list = parse_id_list(id_data)

    entry_size = id_list[1][1] - id_list[0][1]

    if(layout_path_prefix==""):
        layout_path_prefix = "../../resources/Layouts/"
    layout_path = layout_path_prefix + name + ".xml"
    param = create_param_from_layout(layout_path,name,entry_size)
    param.ids = id_list

    data_list = {}

    """ parse data from param entries """
    current_offset = 0
    next_offset = 0
    for id in id_list:
        log(f"ID: {id}", Logging_Level.DEBUG,1)
        current_entry = []
        binary_counter = 0
        bit = 0
        current_total_offset = (id_end + current_offset)
        if(id[1] < (current_total_offset-entry_size)):
            log(f"ERROR: offset incorrect {current_total_offset} (expected: {id[1]} + {entry_size})", Logging_Level.ERROR)
            return
        for field in param.layout:
            log(f"Field: {field.name}", Logging_Level.DEBUG,1)
            log(f"Type: {field.variable_type}", Logging_Level.DEBUG,1)
            if(field.variable_type==fm.Data_type.Binary.value):
                bit = 2 ** binary_counter
                binary_counter +=1
                if(binary_counter>=8):
                    binary_counter = 0
                    next_offset +=1 #increase offset after 8 binary values
            else:
                if(binary_counter>0):
                    current_offset += 1 #increase offset if less than 8 binary values were defined
                next_offset = current_offset + fm.type_size[field.variable_type] + field.length #this can be handled in else since binary doesnt have a default size anyways

            data_format_string = "<"

            if(field.signed):
                if(field.variable_type==fm.Data_type.Byte.value):
                    data_format_string += "b"
                if(field.variable_type==fm.Data_type.Bytes_2.value):
                    data_format_string += "h"
                if(field.variable_type==fm.Data_type.Bytes_4.value):
                    data_format_string += "i"
                if(field.variable_type==fm.Data_type.Bytes_8.value):
                    data_format_string += "q"
            else:
                if(field.variable_type==fm.Data_type.Byte.value):
                    data_format_string += "B"
                if(field.variable_type==fm.Data_type.Bytes_2.value):
                    data_format_string += "H"
                if(field.variable_type==fm.Data_type.Bytes_4.value):
                    data_format_string += "I"
                if(field.variable_type==fm.Data_type.Bytes_8.value):
                    data_format_string += "Q"

            if(field.variable_type==fm.Data_type.Binary.value):
                    data_format_string += "B"
            if(field.variable_type==fm.Data_type.Float.value):
                    data_format_string += "f"
            if(field.variable_type==fm.Data_type.Double.value):
                    data_format_string += "d"
            if(field.variable_type==fm.Data_type.String.value):
                    data_format_string += f"{field.length}s"
            if(field.variable_type==fm.Data_type.AoB.value):
                    data_format_string += f"{field.length}c"

            current_field_struct = Struct(data_format_string)
            log(f"format: {data_format_string} : len: {len(entry_data[current_offset:next_offset])}", Logging_Level.DEBUG,1)
            log(f"data: {entry_data[current_offset:next_offset]}", Logging_Level.DEBUG,1)
            if(field.variable_type==fm.Data_type.Binary.value):
                if(current_offset==next_offset): #TODO maybe restructure this to make it less convoluted
                    val = current_field_struct.unpack(entry_data[current_offset:next_offset+1])[0]
                else:
                    val = current_field_struct.unpack(entry_data[current_offset:next_offset])[0]
                log(f"{val} & {bit} = {val & bit}", Logging_Level.DEBUG,1)
                val = min((val & bit),1)
            else:
                if(field.variable_type==fm.Data_type.AoB.value or field.variable_type==fm.Data_type.String.value):
                    if(len(entry_data[current_offset:next_offset])==0): # -- ERROR --
                        log("ERROR: no array data to unpack", Logging_Level.ERROR)
                        log(f"[ID {id}] -> (field {field.name})", Logging_Level.ERROR)
                        log(entry_data[current_offset-4:next_offset+4], Logging_Level.ERROR)
                        log(f"last value: {val}", Logging_Level.ERROR)
                        return
                    else:
                        val = current_field_struct.unpack(entry_data[current_offset:next_offset])
                else:
                    if(len(entry_data[current_offset:next_offset])==0): # -- ERROR --
                        log(f"ERROR: no data to unpack for format {data_format_string}", Logging_Level.ERROR)
                        log(f"[ID {id}] -> (field {field.name})", Logging_Level.ERROR)
                        log(entry_data[current_offset-4:next_offset+4], Logging_Level.ERROR)
                        log(f"last value: {val}", Logging_Level.ERROR)
                        return
                    else:
                        temp_val = current_field_struct.unpack(entry_data[current_offset:next_offset])
                        val = temp_val[0]
                        if(len(temp_val)>1):
                            log("ERROR: more than 1 return value while upacking", Logging_Level.ERROR)
                            return
            log(f"value: {val}\n", Logging_Level.ALL,1)
            current_offset = next_offset
            current_entry.append(val)
        data_list[id[0]] = current_entry
    param.data = data_list
    
  
    log("Finished unpacking Param")
    return param




def pack_param(param_in,original_param_file_path):
    """ read param file from disk, unpack and parse it """
    log("Repacking Param ...")
    param = param_in
    data = dt.open_file(original_param_file_path)

    header_data = data[0:HEADER_END]
    header = parse_param_header(data)

    id_end = header[int(0x30/8)]
    entry_end = header[int(0x10/8)]

    id_data = data[HEADER_END:id_end]
    entry_data = data[id_end:entry_end]
    name_data = data[entry_end:]
    name = dt.convert_to_ascii_string(name_data)

    entry_size = param.entry_size

    new_param_file = header_data
    new_param_file += id_data

    """ get unknown offset from file """
    unknown_offset = data[HEADER_END+2*8:HEADER_END+3*8]
    #print(f"unknown offset: {unknown_offset}")

    """ parse data from param entries """
    current_offset = 0
    next_offset = 0

    #new_param_file += entry_data

    param_data_list = []
    for index in range(int(len(param.data)/800)+1):
        param_data_list.append(b'')
    #param_data1 = b''
    #param_data2 = b''
    #param_data3 = b''
    
    for param_index,key in enumerate(param.data):
        log(f"ID: {key}", Logging_Level.DEBUG,1)
        binary_counter = 0
        bit = 0
        current_binary_value = 0
        new_entry_data = ""
        field_index = 0
        for field in param.layout:
            data_format_string = "<"
            new_entry_data = b''
            log(f"Field: {field.name}", Logging_Level.DEBUG,2)
            log(f"Type: {field.variable_type}", Logging_Level.DEBUG,12)
            if(field.variable_type==fm.Data_type.Binary.value):
                prev_binary_value = current_binary_value
                flag_value = param.data[key][field_index]
                assert(flag_value<=1)
                current_binary_value += (2 ** binary_counter) * flag_value
                log(f"current_binary_value {current_binary_value} = (prev){prev_binary_value} + (2 ** {binary_counter}) * {param.data[key][field_index]}", Logging_Level.DEBUG,2)
                binary_counter +=1
                if(binary_counter>=8):
                    data_format_string += "B"
                    log(f"PACK FORMAT: {data_format_string}", Logging_Level.DEBUG,2)
                    log(f"value: {value}", Logging_Level.DEBUG,2)
                    current_field_struct = Struct(data_format_string)
                    new_entry_data = current_field_struct.pack(current_binary_value)
                    log(f"Repacked: {new_entry_data}\n", Logging_Level.DEBUG,2)
                    binary_counter = 0
                    current_binary_value = 0
                    next_offset +=1 #increase offset after 8 binary values
            else:
                if(binary_counter>0):
                    data_format_string += "B"
                    current_field_struct = Struct(data_format_string)
                    new_entry_data = current_field_struct.pack(current_binary_value)
                    log(f"Current Binary Value: {current_binary_value}", Logging_Level.DEBUG,2)
                    binary_counter = 0
                    current_binary_value = 0
                    log("Failed successfully", Logging_Level.ERROR)
                    log("Less than 8 successive binaries occured", Logging_Level.ERROR)
                    return
                if(field.signed):
                    if(field.variable_type==fm.Data_type.Byte.value):
                        data_format_string += "b"
                    if(field.variable_type==fm.Data_type.Bytes_2.value):
                        data_format_string += "h"
                    if(field.variable_type==fm.Data_type.Bytes_4.value):
                        data_format_string += "i"
                    if(field.variable_type==fm.Data_type.Bytes_8.value):
                        data_format_string += "q"
                else:
                    if(field.variable_type==fm.Data_type.Byte.value):
                        data_format_string += "B"
                    if(field.variable_type==fm.Data_type.Bytes_2.value):
                        data_format_string += "H"
                    if(field.variable_type==fm.Data_type.Bytes_4.value):
                        data_format_string += "I"
                    if(field.variable_type==fm.Data_type.Bytes_8.value):
                        data_format_string += "Q"

                if(field.variable_type==fm.Data_type.Float.value):
                    data_format_string += "f"
                if(field.variable_type==fm.Data_type.Double.value):
                    data_format_string += "d"
                if(field.variable_type==fm.Data_type.String.value):
                    data_format_string += f"{field.length}s"
                if(field.variable_type==fm.Data_type.AoB.value):
                    data_format_string += f"{field.length}c"

                current_field_struct = Struct(data_format_string)
                value = param.data[key][field_index]
                log(f"PACK FORMAT: {data_format_string}", Logging_Level.DEBUG,2)
                log(f"value: {value}", Logging_Level.DEBUG,2)
                log(f"Key: {key} Value {field_index}", Logging_Level.DEBUG,2)
                if(field.variable_type==fm.Data_type.AoB.value):
                    new_entry_data = current_field_struct.pack(*value)
                else:
                    new_entry_data = current_field_struct.pack(value)
                log(f"Repacked: {new_entry_data}", Logging_Level.DEBUG,2)
            field_index += 1
            param_data_list[int(param_index/800)] += new_entry_data
        #pass
        log(f"[{param_index}/{len(param.data)}] : [{len(new_param_file)}]", Logging_Level.INFO, 0, '\r')
    for pdata in param_data_list:
        new_param_file += pdata
    new_param_file += name_data
    log("Finished packing Param", Logging_Level.INFO)
    return new_param_file



    