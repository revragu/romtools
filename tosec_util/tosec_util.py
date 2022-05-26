#!/usr/bin/env python3

import sys,os,binascii,hashlib,json,xmltodict





def CRC32_from_file(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return ("%08X" % buf).lower()

def MD5_from_file(filename):
    hash_md5=hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return (hash_md5.hexdigest()).lower()

def SHA1_from_file(filename):
    hash_sha1=hashlib.sha1()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha1.update(chunk)
    return (hash_sha1.hexdigest()).lower()

def test_collision(hash_list):
    if hash_list.len() > 1:
        return(True)
    return(False)

class roms:
    def __init__(self,input_path):
        self.path=input_path
        self.processDirs()
        self.sortRoms()

    def processDirs(self):
        self.rom_list=[]
        for r, d, f in os.walk(self.path):
            for file in f:
                
                full_path=os.path.join(r,file)
                file_size=os.path.getsize(full_path)
                file_sha1=SHA1_from_file(full_path)
                file_dict={
                    "filename" : file,
                    "full_path" : full_path,
                    "sha1" : file_sha1
                }
                self.rom_list.append(file_dict)
    
    def sortRoms(self):
        self.rom_dict={}
        for d in self.rom_list:
            try:  
                self.rom_dict["sha1"].append(d)
            except:
                self.rom_dict["sha1"]=[d]

    def show_all(self):
        if not self.rom_dict:
            return(self.rom_list)
        else:
            return(self.rom_dict)

    def getByHash(self,hash):
        try:
            return(self.rom_dict[hash])
        except:
            return(False)


class tosec_dat:
    def __init__(self):
        self.script_path=os.path.dirname(os.path.realpath(__file__))
        self.dat_path=(self.script_path + "/dat")
        self.datfiles=[]
        self.processDats()


    def processDats(self):
        for r, d, f in os.walk(self.dat_path):
            for file in f:
                current_dat={}
                full_path=os.path.join(r,file)
                with open(full_path,'r') as datfile:
                    current_dat=xmltodict.parse(datfile.read())
                self.datfiles.append(current_dat)
                
    def getDatByName(self,dat_name):
        for dat_file in self.datfiles:
            if dat_file["datafile"]["header"]["name"] == dat_name:
                return(dat_file["datafile"]["game"])

    def len(self):
        return(self.datfiles["datafile"].len())
    
    def output_all(self):
        return(self.datfiles)



rom_obj=roms('/mnt/share/roms/MSX/tosec/MSX TurboR [TOSEC]')
dat_list=tosec_dat()


export_list=[]





#for datfile in dat_list.show_all():



print(json.dumps(dat_list.output_all(),indent=4))

rom_collection=rom_obj.show_all()

with open('result.json', 'w') as fp:
    json.dump(rom_collection, fp, indent=4, sort_keys=True)
            
        


