from enum import Enum
import xml.etree.ElementTree as ET

class Data_type(Enum):
    Binary = 1
    Byte = 2
    Bytes_2 = 3
    Bytes_4 = 4
    Bytes_8 = 5
    Float = 6
    Double = 7
    String = 8
    AoB = 9

class Param_Row:
    name = "UNDEFINED"
    signed = False
    bit = 0
    variable_type = Data_type.AoB.value
    def __init__(self, name, variable_type,offset,length=0,signed=False,bit=0,default=0):
        self.name = name
        self.variable_type = variable_type
        self.offset = offset
        self.length = length
        self.signed = signed
        self.bit = bit

class Param:
    name = "UNDEFINED"
    entry_size = 0
    layout = []
    ids = [] #{id : offset}
    data = [] #{id : [values]}

    def __init__(self,name,entry_size,layout):
        self.name = name
        self.entry_size = entry_size
        self.layout = layout




    

type_string = {Data_type.Binary.value: "Binary", 
               Data_type.Byte.value: "Byte", 
               Data_type.Bytes_2.value: "2 Bytes", 
               Data_type.Bytes_4.value: "4 Bytes", 
               Data_type.Bytes_8.value: "8 Bytes", 
               Data_type.Float.value: "Float", 
               Data_type.Double.value: "Double", 
               Data_type.String.value: "String", 
               Data_type.AoB.value: "Array of Byte"}

type_size = {Data_type.Binary.value: 0, 
             Data_type.Byte.value: 1, 
             Data_type.Bytes_2.value: 2, 
             Data_type.Bytes_4.value: 4, 
             Data_type.Bytes_8.value: 8, 
             Data_type.Float.value: 4, 
             Data_type.Double.value: 8, 
             Data_type.String.value: 0, 
             Data_type.AoB.value: 0}

#TODO add support for Paramdex paramdefs

def read_layout_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    return (tree,root)

def parse_layout_xml(path): 
    tree,root = read_layout_xml(path)
    layout_entry_list = []
    for entry in root:
        e_name = entry.find("name").text
        e_type,e_size,e_signed = parse_type_string(entry.find("type").text) #read data type and get static size for that type

        e_default = 0
        default_node = entry.find("default") #dummy entries dont seem to have default defined
        if(default_node != None):
            e_default = entry.find("default").text

        e_length = 0
        size_node = entry.find("size") #aob length
        if(size_node != None): #if the entry has a defined size (dummy and probably string) save the value for determining the offset later
            e_length = int(size_node.text)

        layout_entry_list.append({"name" : e_name, "type" : e_type, "size" : e_size, "signed" : e_signed, "default" : e_default, "length" : e_length})
    return (layout_entry_list,tree)

def layout2CE(path):
    layout_entry_list,tree = parse_layout_xml(path)
    ce_entry_list = []
    total_offset = 0
    binary_counter = 0
    for layout_entry in layout_entry_list:
        c_entry = CE_Entry(layout_entry["name"], layout_entry["type"], layout_entry["length"], 0, total_offset)
        if(layout_entry["type"]==Data_type.Binary.value):
            c_entry.bit_start = binary_counter
            binary_counter +=1
            if(binary_counter>=8):
                binary_counter = 0
                total_offset +=1
        else:
            if(binary_counter>0):
                total_offset += 1
            total_offset += layout_entry["size"]
            c_entry.signed=layout_entry["signed"]
        ce_entry_list.append(c_entry)
            
    return ce_entry_list

def layout2ParamRows(path):
    layout_entry_list,tree = parse_layout_xml(path)
    row_list = []
    total_offset = 0
    binary_counter = 0
    for layout_entry in layout_entry_list:
        row = Param_Row(layout_entry["name"], layout_entry["type"],total_offset,layout_entry["length"],layout_entry["signed"])
        if(layout_entry["type"]==Data_type.Binary.value):
            row.bit = binary_counter
            binary_counter +=1
            if(binary_counter>=8):
                binary_counter = 0
                total_offset +=1
        else:
            if(binary_counter>0):
                total_offset += 1
            total_offset += layout_entry["size"]
        row_list.append(row)
            
    return row_list



def parse_type_string(input_string):
    t_string = input_string
    e_type = Data_type.String.value
    signed = False
    size = 0
    if(t_string[0:6]=="fixstr"):
        print("ERROR: fixstr not implemented yet")
        size = int(int(t_string[5:])/8)
        return e_type,size,False
    if(t_string[0:5]=="dummy"):
        size = int(int(t_string[5:])/8)
        e_type = Data_type.AoB.value
        return e_type,size,False
    elif(t_string[0]=="f"):
        size = int(int(t_string[1:])/8)
        if(size==4):
            e_type = Data_type.Float.value
        elif(size==8):
            e_type = Data_type.Double.value
        else:
            print("ERROR unknown floatingpoint size")
        return e_type,size,False
    elif t_string[0] == "b":
        return Data_type.Binary.value,0,False
    else:
        if(t_string[0]=="s"):
            signed = True
        size = int(int(t_string[1:])/8)
        if(size==1):
            e_type = Data_type.Byte.value
        if(size==2):
            e_type = Data_type.Bytes_2.value
        if(size==4):
            e_type = Data_type.Bytes_4.value
        if(size==8):
            e_type = Data_type.Bytes_8.value
    return e_type,size,signed

def print_layout(param):
    for i,row in enumerate(param.layout):
        print(f"[{i}]: {row.name} : {row.variable_type}")