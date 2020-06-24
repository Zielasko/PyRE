import FRPG.formats as fm

class CE_Entry:
    description = ""
    signed = False
    bit_start = 0
    def __init__(self, description, variable_type,length=0,base_address=0,address_offset=0,*pointer_offsets):
        self.description = description
        self.variable_type = variable_type
        self.length = length
        self.base_address = base_address
        self.address_offset = address_offset
        self.offsets = pointer_offsets

def generate_continuous_offsets(number_of_entries,data_type,base_address=0,*offsets):
    entry_list = []
    for i in range(number_of_entries):
      entry = CE_Entry(f"{type_string[data_type.value]}_{i}", data_type.value, 0, base_address,i * type_size[data_type.value],*offsets)
      entry_list.append(entry)
    return entry_list

def entry_to_XML(entry,id=0):
    entry_string = "<CheatEntry>\n"
    entry_string += f"<ID>{id}</ID>\n" #the ID doesnt actually seem to matter and is replaced when pasting
    entry_string += f'<Description>"{entry.description}"</Description>\n'
    if(entry.signed):
        entry_string += f'<ShowAsSigned>1</ShowAsSigned>'
    entry_string += f"<VariableType>{type_string[entry.variable_type]}</VariableType>\n"
    if(entry.variable_type == Data_type.String.value):
        entry_string += f"<Length>{entry.length}</Length>\n"
        entry_string += f"<Unicode>1</Unicode>\n"
        entry_string += f"<CodePage>0</CodePage>\n"
        entry_string += f"<ZeroTerminate>1</ZeroTerminate>\n"
    if(entry.variable_type == Data_type.AoB.value):
        entry_string += f"<ByteLength>{entry.length}</ByteLength>\n"
    if(entry.variable_type == Data_type.Binary.value):
        entry_string += f"<BitStart>{entry.bit_start}</BitStart>\n"
        entry_string += f"<BitLength>{1}</BitLength>\n" #entry.length - use 1 instead since that seems to always be the correct value 
        entry_string += "<ShowAsBinary>0</ShowAsBinary>\n"
    address = ""
    if(entry.base_address!=0):
        address += f"0x{entry.base_address:x}"
    address += f" + 0x{entry.address_offset:x}"
    entry_string += f"<Address>{address}</Address>\n"
    if(len(entry.offsets)>0):
        entry_string += "<Offsets>\n"
        for offset in entry.offsets:
            entry_string += f"<Offset>{offset}</Offset>\n"
        entry_string += "</Offsets>\n"
    entry_string += "</CheatEntry>\n"
    return entry_string

def entry_list_to_XML(entry_list):
    xml = '<?xml version="1.0" encoding="utf-8"?>\n'
    xml += "<CheatTable>\n"
    xml += "<CheatEntries>\n"
    for i,entry in enumerate(entry_list):
        xml += entry_to_XML(entry,i)
    xml += "</CheatEntries>\n"
    xml += "</CheatTable>\n"
    return xml