from struct import Struct

import FRPG.formats as fm
import FRPG.utils as dt

HEADER_END = 0x40

START_OF_PARAM_DATA_PTR = 0x30
NAME_OFFSET_PTR = 0x10


HEADER_FORMAT_STRING = "<8Q"
ID_OFFSET_FORMAT_STRING = "<3Q"

DEBUG_LOGGING_LEVEL = 0
log_unpack = 0
log_repack = 1



def create_param_from_layout(layout_path,name,entry_size):
    rows = fm.layout2ParamRows(layout_path)
    end_of_layout = rows[-1].offset+rows[-1].length+fm.type_size[rows[-1].variable_type] #TODO + 1 + 1 fix this something is off by one here
    if(end_of_layout + 2<entry_size):
        unknown_data_row = fm.Param_Row("Unknown", fm.Data_type.AoB.value,(end_of_layout),entry_size-end_of_layout) #create additional row for remaining unknown data
        rows.append(unknown_data_row)
    if(end_of_layout>entry_size):
        print("layout_doesnt match entry size read from param file")
        print(f"layout size {end_of_layout} - entry_size {entry_size}")
        return
    param = fm.Param(name,entry_size,rows)
    return param

def get_row_index(row,layout):
    index = 0
    try:
        index = int(row)
    except ValueError:
        for l_row in layout:
            if(l_row.name==row):
                break
            index += 1
    return index


def parse_param_header(data):
    """ unpack and parse the header of the param file """
    header_data = ""
    header_data = data[0:HEADER_END]
    if(DEBUG_LOGGING_LEVEL>2):
        print(header_data)
    header_struct = Struct(HEADER_FORMAT_STRING)
    header = header_struct.unpack(header_data)

    return header


def parse_id_list(data):
    """ parse id - offset list """
    id_list = []
    id_list_struct = Struct(ID_OFFSET_FORMAT_STRING)
    number_of_ids = ((len(data)/8)/3)
    print(number_of_ids)
    if((number_of_ids-int(number_of_ids))>0.01):
        print("ERROR: ID data is not divisible by 3")
        return

    for i in range(int(number_of_ids)):
        current_offset = i*3*8
        current_data = data[current_offset:current_offset+3*8]
        c_id,c_offset,c_unkwn = id_list_struct.unpack(current_data)
        id_list.append((c_id,c_offset))
    return id_list


def parse_param(param_file_path,layout_path_prefix):
    """ read param file from disk, unpack and parse it """
    print("Unpacking Param ...")
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
        if(DEBUG_LOGGING_LEVEL > 1 and log_unpack > 0):
            print(f"ID: {id}")
        current_entry = []
        binary_counter = 0
        bit = 0
        current_total_offset = (id_end + current_offset)
        if(id[1] < (current_total_offset-entry_size)):
            print(f"ERROR: offset incorrect {current_total_offset} (expected: {id[1]} + {entry_size})")
            return
        for row in param.layout:
            if(DEBUG_LOGGING_LEVEL>1 and log_unpack > 0):
                print(f"Row: {row.name}")
                print(f"Type: {row.variable_type}")
            if(row.variable_type==fm.Data_type.Binary.value):
                bit = 2 ** binary_counter
                binary_counter +=1
                if(binary_counter>=8):
                    binary_counter = 0
                    next_offset +=1 #increase offset after 8 binary values
            else:
                if(binary_counter>0):
                    current_offset += 1 #increase offset if less than 8 binary values were defined
                next_offset = current_offset + fm.type_size[row.variable_type] + row.length #this can be handled in else since binary doesnt have a default size anyways

            data_format_string = "<"

            if(row.signed):
                if(row.variable_type==fm.Data_type.Byte.value):
                    data_format_string += "b"
                if(row.variable_type==fm.Data_type.Bytes_2.value):
                    data_format_string += "h"
                if(row.variable_type==fm.Data_type.Bytes_4.value):
                    data_format_string += "i"
                if(row.variable_type==fm.Data_type.Bytes_8.value):
                    data_format_string += "q"
            else:
                if(row.variable_type==fm.Data_type.Byte.value):
                    data_format_string += "B"
                if(row.variable_type==fm.Data_type.Bytes_2.value):
                    data_format_string += "H"
                if(row.variable_type==fm.Data_type.Bytes_4.value):
                    data_format_string += "I"
                if(row.variable_type==fm.Data_type.Bytes_8.value):
                    data_format_string += "Q"

            if(row.variable_type==fm.Data_type.Binary.value):
                    data_format_string += "B"
            if(row.variable_type==fm.Data_type.Float.value):
                    data_format_string += "f"
            if(row.variable_type==fm.Data_type.Double.value):
                    data_format_string += "d"
            if(row.variable_type==fm.Data_type.String.value):
                    data_format_string += f"{row.length}s"
            if(row.variable_type==fm.Data_type.AoB.value):
                    data_format_string += f"{row.length}c"

            current_row_struct = Struct(data_format_string)
            if(DEBUG_LOGGING_LEVEL>1 and log_unpack > 0):
                print(f"format: {data_format_string} : len: {len(entry_data[current_offset:next_offset])}")
                print(f"data: {entry_data[current_offset:next_offset]}")
            if(row.variable_type==fm.Data_type.Binary.value):
                if(current_offset==next_offset): #TODO maybe restructure this to make it less convoluted
                    val = current_row_struct.unpack(entry_data[current_offset:next_offset+1])[0]
                    #print(f"ping {current_offset}")
                else:
                    val = current_row_struct.unpack(entry_data[current_offset:next_offset])[0]
                    #print(f"pong {current_offset}")
                if(DEBUG_LOGGING_LEVEL>1 and log_repack > 0): # -- DEBUG --    
                    print(f"{val} & {bit} = {val & bit}")
                val = min((val & bit),1)
            else:
                if(row.variable_type==fm.Data_type.AoB.value or row.variable_type==fm.Data_type.String.value):
                    #print("AOB")
                    if(len(entry_data[current_offset:next_offset])==0): # -- ERROR --
                        print("ERROR: no array data to unpack")
                        print(f"[ID {id}] -> (row {row.name})")
                        print(entry_data[current_offset-4:next_offset+4])
                        print(f"last value: {val}")
                        return
                    else:
                        val = current_row_struct.unpack(entry_data[current_offset:next_offset])
                else:
                    if(len(entry_data[current_offset:next_offset])==0): # -- ERROR --
                        print(f"ERROR: no data to unpack for format {data_format_string}")
                        print(f"[ID {id}] -> (row {row.name})")
                        print(entry_data[current_offset-4:next_offset+4])
                        print(f"last value: {val}")
                        return
                    else:
                        temp_val = current_row_struct.unpack(entry_data[current_offset:next_offset])
                        val = temp_val[0]
                        if(len(temp_val)>1):
                            print("ERROR: more than 1 return value while upacking")
                            return
            if(DEBUG_LOGGING_LEVEL>0 and log_unpack > 0):
                print(f"value: {val}\n\n")
            current_offset = next_offset
            current_entry.append(val)
        data_list[id[0]] = current_entry
    param.data = data_list
    
  
    print("Finished unpacking Param")
    return param




def pack_param(param_in,original_param_file_path):
    """ read param file from disk, unpack and parse it """
    print("Repacking Param ...")
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
        if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0):
            print(f"ID: {key}")
        binary_counter = 0
        bit = 0
        current_binary_value = 0
        new_entry_data = ""
        row_index = 0
        for row in param.layout:
            data_format_string = "<"
            new_entry_data = b''
            if(DEBUG_LOGGING_LEVEL>1 and log_repack > 0): # -- DEBUG --
                print(f"Row: {row.name}")
                print(f"Type: {row.variable_type}")
            if(row.variable_type==fm.Data_type.Binary.value):
                prev_binary_value = current_binary_value
                flag_value = param.data[key][row_index]
                assert(flag_value<=1)
                current_binary_value += (2 ** binary_counter) * flag_value
                if(DEBUG_LOGGING_LEVEL>1 and log_repack > 0): # -- DEBUG --
                    print(f"current_binary_value {current_binary_value} = (prev){prev_binary_value} + (2 ** {binary_counter}) * {param.data[key][row_index]}")
                binary_counter +=1
                if(binary_counter>=8):
                    data_format_string += "B"
                    if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0):# -- DEBUG --
                        print(f"PACK FORMAT: {data_format_string}")
                        print(f"value: {value}")
                    current_row_struct = Struct(data_format_string)
                    new_entry_data = current_row_struct.pack(current_binary_value)
                    if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0): # -- DEBUG --
                        print(f"Repacked: {new_entry_data}\n")
                    binary_counter = 0
                    current_binary_value = 0
                    next_offset +=1 #increase offset after 8 binary values
            else:
                if(binary_counter>0):
                    data_format_string += "B"
                    current_row_struct = Struct(data_format_string)
                    new_entry_data = current_row_struct.pack(current_binary_value)
                    if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0):# -- DEBUG --
                        print(f"Current Binary Value: {current_binary_value}\n")
                    binary_counter = 0
                    current_binary_value = 0
                    print("Failed successfully")
                    print("Less than 8 successive bianries occured")
                    return
                if(row.signed):
                    if(row.variable_type==fm.Data_type.Byte.value):
                        data_format_string += "b"
                    if(row.variable_type==fm.Data_type.Bytes_2.value):
                        data_format_string += "h"
                    if(row.variable_type==fm.Data_type.Bytes_4.value):
                        data_format_string += "i"
                    if(row.variable_type==fm.Data_type.Bytes_8.value):
                        data_format_string += "q"
                else:
                    if(row.variable_type==fm.Data_type.Byte.value):
                        data_format_string += "B"
                    if(row.variable_type==fm.Data_type.Bytes_2.value):
                        data_format_string += "H"
                    if(row.variable_type==fm.Data_type.Bytes_4.value):
                        data_format_string += "I"
                    if(row.variable_type==fm.Data_type.Bytes_8.value):
                        data_format_string += "Q"

                if(row.variable_type==fm.Data_type.Float.value):
                    data_format_string += "f"
                if(row.variable_type==fm.Data_type.Double.value):
                    data_format_string += "d"
                if(row.variable_type==fm.Data_type.String.value):
                    data_format_string += f"{row.length}s"
                if(row.variable_type==fm.Data_type.AoB.value):
                    data_format_string += f"{row.length}c"

                current_row_struct = Struct(data_format_string)
                value = param.data[key][row_index]
                if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0): # -- DEBUG --
                    print(f"PACK FORMAT: {data_format_string}")
                    print(f"value: {value}")
                    print(f"Key: {key} Value {row_index}")
                if(row.variable_type==fm.Data_type.AoB.value):
                    #print(*value)
                    new_entry_data = current_row_struct.pack(*value)
                else:
                    new_entry_data = current_row_struct.pack(value)
                if(DEBUG_LOGGING_LEVEL>0 and log_repack > 0):          # -- DEBUG --
                    print(f"Repacked: {new_entry_data}\n")
            row_index += 1
            param_data_list[int(param_index/800)] += new_entry_data
        #pass
        print(f"[{param_index}/{len(param.data)}] : [{len(new_param_file)}]", end = '\r')
    for pdata in param_data_list:
        new_param_file += pdata
    new_param_file += name_data
    print("Finished packing Param")
    return new_param_file



    