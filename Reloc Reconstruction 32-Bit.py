import binascii
#code_start = 0x011D1000
#code_end = 0x011D2000
#data_refs = 0x011D2000
#data_refs_end = 0x011D4000
code_start = AskAddr(0,"Please enter start VA of the code.")
if (code_start > 0):
    code_end = AskAddr(0,"Please enter end VA of the code.")
    if (code_end > 0):
        data_refs = AskAddr(0,"Please enter start VA of the data.")
        if (data_refs > 0):
            data_refs_end = AskAddr(0,"Please enter end VA of the data.")
            if (data_refs_end > 0):
                result = []
                image_base = idaapi.get_imagebase()
                file = open(GetInputFile(),"rb")
                #MakeUnknown(x,(data_refs_end-data_refs),DOUNK_DELNAMES)
                x = data_refs
                while (x < data_refs_end):
                    physical_addr = x-image_base
                    file.seek(physical_addr)
                    read_bytes = struct.unpack("<L",file.read(4))[0]
                    if (read_bytes >  image_base and read_bytes < data_refs_end):
                        name = Name(read_bytes)
                        if x not in result:
                            #print "From %x %s" % (read_bytes,name)
                            result.append(x)
                    x =x + 1
                x = data_refs
                while (x < data_refs_end):
                    for ref in XrefsTo(x, 0):
                        if ref.frm < data_refs_end:
                            y = ref.frm
                            exit = False
                            while (y < ref.frm+4 and exit == False):
                                file.seek(y-image_base)
                                two_bytes = struct.unpack("<H",file.read(2))[0]
                                if ((image_base>>16) == two_bytes):
                                    entry = y-2
                                    if entry not in result:
                                        print "referenced %x" % entry
                                        exit = True
                                        result.append(entry)
                                y = y+1
                    x =x +1
                x = idaapi.get_imagebase()
                while (x < code_end):
                    flags = GetFlags(x);
                    if(isCode(flags) and x not in result):
                        first = GetOperandValue (x,0)
                        second = GetOperandValue (x,1)
                        third = GetOperandValue (x,2)
                        #print "addr %x f %x s %x t %s" % (x,first,second,third)
                        add_to_result = False
                        #print "%x" % first
                        if((first <= code_end and first >= image_base) or (second <= code_end and second >= image_base) or (third <= code_end and third >= image_base)):
                            add_to_result = True
                        if((first <= data_refs_end and first >= data_refs) or (second <= data_refs_end and second >= data_refs) or (third <= data_refs_end and third >= data_refs)):
                            add_to_result = True
                        if (add_to_result == True):
                            end = x + 20
                            exit =  False
                            y = x
                            while (y< end and exit == False):
                                file.seek(y-image_base)
                                two_bytes = struct.unpack("<H",file.read(2))[0]
                                if(two_bytes == (image_base>>16)):
                                    print "%x %x" % (y-2,two_bytes)
                                    print "%x - %s - %x" % (y-2,GetDisasm(y),add_to_result)
                                    if (y-2) not in result:
                                        result.append(y-2)
                                        exit = True
                                y =y+1
                            #print str(hex(y))[2:-1] 
                    #print GetDisasm(x)
                    x =x +ItemSize(x)    
                print "***Starting The Creation Of The \".Reloc\" Binary Section.***"
                file = open("reloc.bin","wb")
                code_section_rvas = []
                data_section_rvas = []
                x = 0
                while (x < len(result)):
                    if(result[x] >= code_start and result[x] <= code_end):
                        code_section_rvas.append(result[x]-image_base)
                    elif(result[x] > data_refs and result[x] < data_refs_end):
                        data_section_rvas.append(result[x]-image_base)
                    x =x + 1
                code_section_rvas.sort()
                data_section_rvas.sort()
                code_section_rvas.append(0x0000)
                data_section_rvas.append(0x0000)
                for entry in code_section_rvas:
                    print "%x" % (entry)
                for entry in data_section_rvas:
                    print "%x" % (entry)
                print "Length of data is:%d" % len(data_section_rvas)
                print "Length of code is:%d" % len(code_section_rvas)
                if(file):
                    file.write(struct.pack("<L",code_start-image_base))
                    file.write(struct.pack("<L",((len(code_section_rvas))*2+8)))
                    for entry in code_section_rvas:
                        if(entry != 0x0):
                            file.write(struct.pack("<H",entry+(code_end-image_base)))
                        else:
                            file.write(struct.pack("<H",entry))
                    file.write(struct.pack("<L",data_refs-image_base))
                    file.write(struct.pack("<L",((len(data_section_rvas))*2+8)))
                    for entry in data_section_rvas:
                        if(entry != 0x0):
                            file.write(struct.pack("<H",entry+(data_refs-code_start)))
                        else:
                            file.write(struct.pack("<H",entry))
                else:
                    print "###Opening \"reloc.bin\" Failed.###"
                if(file):
                    file.close()
            else:
                print "Please enter the VA of the end of the data section."
        else:
            print "Please enter the VA of the start of the data section."
    else:
        print "Please enter the VA of the end of the code section."
else:
    print "Please enter the VA of the start of the code section."