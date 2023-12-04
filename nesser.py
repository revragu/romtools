#!/usr/bin/env python3

import sys
from hashlib import sha1, sha256, md5
from binascii import crc32
from ragu_file import readBytesfromFile
from ragu_ops import bytesum, clearBits, countBits

class WrongFormatError(Exception):
    def __init__(self,message="Not a valid NES ROM header,does not begin with \
    'NES'"):
        self.message=message
        super().__init__(self.message)

class DataNotFound(Exception):
    def __init__(self,message="Data not found"):
        self.message=message
        super().__init__(self.message)


class InvalidROMSize(Exception):
    def __init__(self,message="Not a valid ROM size"):
        self.message=message
        super().__init__(self.message)

class NotVSSystem(Exception):
    def __init__(self,message="Not a Vs system or Extended ROM"):
        self.message=message
        super().__init__(self.message)


class UnhandledError(Exception):
    def __init__(self,unk_error):
        self.message="Unhandled error: " + unk_error
        super().__init__(self.message)



class header:
    def __init__(self,input_bytes=False):
        self.raw=bindata()
        self.flags={}
        if input_bytes != False:
            self.loadBytes(input_bytes)


    def loadBytes(self, input_bytes):
        # first 16 bytes of rom data should be the the header
        self.raw.extract(input_bytes,16,"Header")
        
        # confirm by checking that NES<EOF> at start
        self.__validateNES__(self.raw.data)
        # populate flags dict
        self.flags=self.__getFlags__(self.raw.data)

    def convertFormat(self):
        try:
            if self.flags['header_format']:
                pass
        except:
            raise ValueError("Header is empty")

        if self.flags['header_format'] == 1:
            # convert to NES 2.0
            new_values=header()
            new_values.flags=self.__getMapperDefaults20__(self.flags)

    def __getMapperDefaults20__(self,flags):
        output_flags={}
        output_flags['header_format']=2
        output_flags['expansion_device']=1
        if flags['battery'] == 1:
            output_flags['nvram_size']=8192           
        if flags['chrrom_size'] == 0:
            output_flags['chrram_size']=8192
        if flags['mapper'] == 1:
            if flags['battery'] == 1:
                output_flags['nvram_size']=32768
            else:
                output_flags['prgram_size']=32768
        if flags['mapper'] == 4:
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 5:
            if flags['battery'] == 1:
                output_flags["nvram_size"]=131072
            else:
                output_flags['prgram_size']=131072
        if flags['mapper'] == 9:
            if flags['battery'] == 0 and flags['pc10'] == 1:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 10:
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192            
        if flags['mapper'] == 19:
            # this one has a bunch of things that can't really be guessed
            #
            # no battery, no WRAM: battery bit clear, PRG-RAM/PRG-NVRAM both
            # set to zero.
            #
            # battery but no WRAM: battery bit set, PRG-RAM/PRG-NVRAM both set 
            # to zero. The game writes its save data into the 128 byte internal
            # RAM.
            #
            # battery and WRAM: battery bit set, PRG-RAM set to zero and 
            # PRG-NVRAM set to 8192.
            # 
            # expansion sound vol set with submapper 3,4,5
            #
            # converted roms probably need some manual changes
            if flags['battery'] == 1:
                output_flags['prgnvram_size']=8192

        if flags['mapper'] == 23:
            # may be either VRC2 or VRC4. 
            # submapper 1: VRC4f
            # submapper 2: VRC4e
            # submapper 3: VRC2b
            # will probably be compatible without submapper?
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 24:
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 25:
            # see mapper 23
            # submapper 1: VRC4b
            # submapper 2: VRC4d
            # submapper 3: VRC2c
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 26:
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 34:
            # submapper 1: NINA-001
            # submapper 2: BNROM
            output_flags['prgram_size'] = 8192
        if flags['mapper'] == 48:
            # MMC3-like
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 69:
            if flags['battery'] == 1:
                output_flags['prgnvram_size']=524288
            else:
                output_flags['prgram_size']=524288
        if flags['mapper'] == 85:
            if flags['battery'] == 0:
                output_flags['prgram_size']=8192
        if flags['mapper'] == 163:
            output_flags['prgnvram_size']=8192




            



    def __getFlags__(self, data):
        # initialize properties
        flag_dict = {
        'header_format'            : False,
        'mirroring'                : False,
        'battery'                  : False,
        'trainer'                  : False,
        'fourscreen'               : False,
        'busconflicts_unofficial'  : False,
        'console_type'             : False,
        'expansion_device'         : False,
        'vssystem'                 : False,
        'vssystem_ppu'             : False,
        'vssystem_type'            : False,
        'ext_console_type'         : False,
        'pc10'                     : False,
        'tvsystem'                 : False,
        'tvsystem_unofficial'      : False,
        'timing'                   : False,
        'prgrom_lsb'               : False,
        'prgrom_msb'               : False,
        'prgrom_size'              : False,
        'prgram_unofficial'        : False,
        'prgram_shift'             : False,
        'prgram_size'              : False,
        'nvram_shift'              : False,
        'nvram_size'               : False,
        'chrrom_lsb'               : False,
        'chrrom_msb'               : False,
        'chrrom_size'              : False,
        'chrram'                   : False,
        'chrram_shift'             : False,
        'chrram_size'              : False,
        'chrnvram_shift'           : False,
        'chrnvram_size'            : False,
        'mapper_ln'                : False,
        'mapper_hn'                : False,
        'mapper_msb'               : False,
        'mapper'                   : False,
        'submapper'                : False,
        'miscroms'                 : False
        }



        # get header format
        flag_dict['header_format']=1
        if (data[7] & 12) == 8:
            flag_dict['header_format']=2

        # get prgrom & chrrom size. multiplied by constant 16k for NES1,
        # used as lsb and combined with msb for NES2
        flag_dict['prgrom_lsb']=data[4]
        flag_dict['chrrom_lsb']=data[5]
        # mirroring, 0 horizontal 1 vertical
        flag_dict['mirroring']=data[6] & 1
        # contains battery backed prg ram or other persistent memory
        flag_dict['battery']=(data[6] & 2) >> 1 
        # 512 byte trainer at $7000-$71FF
        flag_dict['trainer']=(data[6] & 4) >> 2 
        # ignore mirroring, use four-screen vram
        flag_dict['fourscreen']=(data[6] & 8) >> 3 
        # mapper low nybble
        flag_dict['mapper_ln']=(data[6] & 240) >> 4 
        # console type, broken down for 1.0 later - 0 nes, 1 vs system
        # 2 pc10, 3 extended
        flag_dict['console_type']=data[7] & 3
        # mapper high nybble
        flag_dict['mapper_hn']=(data[7] & 240) >> 4 
        # combine mapper low + high nybble
        flag_dict['mapper']=(flag_dict['mapper_hn'] << 4) + \
            flag_dict['mapper_ln'] 
        flag_dict['chrram']=0
        # get prgrom size multiplying by 16K (will be overwritten in 2.0 if msb
        # byte used)
        flag_dict['prgrom_size']=flag_dict['prgrom_lsb'] * 16384
        # get chrrom size and set chrram as 1 if size = 0 (will be overwritten 
        # in 2.0 if msb byte used)
        
        flag_dict['chrrom_size'],flag_dict['chrram']=\
            self.__getChrSize1__(flag_dict['chrrom_lsb'])

        # NES 2.0 specific
        # chr-ram is specified as a value, so chr-ram flag can be False
        flag_dict['chrram']=False
        if flag_dict['header_format'] == 2:
            flag_dict['mapper_msb']=data[8] & 15
            # combine mapper msb with mapper byte for 2.0 extended mapper
            flag_dict['mapper']=\
                (flag_dict['mapper_msb'] << 8) + flag_dict['mapper']
            flag_dict['submapper']=(data[8] & 240) >> 4
            flag_dict['prgrom_msb']=data[9] & 15
            flag_dict['chrrom_msb']=(data[9] & 240) >> 4
            # next 4 are number of shifts for each type of ram
            flag_dict['prgram_shift']=data[10] & 15
            flag_dict['nvram_shift']=(data[10] & 240) >> 4
            flag_dict['chrram_shift']=data[11] & 15
            flag_dict['chrnvram_shift']=(data[11] & 240) >> 4
            # 0 NTSC 1 PAL 2 multiple 3 Dendy
            flag_dict['timing']=data[12] & 3
            
            # misc roms
            flag_dict['miscroms']=data[14] & 3

            # expansion device
            flag_dict['expansion_device']=data[15] & 63
            
            # determine if vs system or extended console type, return 
            # ppu type/vs hw type if vs, extended console type if extended
            flag_dict['vssystem_ppu'],flag_dict['vssystem_type'],\
            flag_dict['ext_console_type']=\
                self.__getVSExt__(flag_dict['console_type'],\
                data[13])
                        
            # combines lsb and msb if msb > 0, otherwise use nes1.0 size
            if flag_dict['prgrom_msb'] > 0:
                flag_dict['prgrom_size']=\
                    self.__getSize2__(flag_dict['prgrom_lsb'],\
                    flag_dict['prgrom_msb'])
            if flag_dict['chrrom_msb'] > 0:
                flag_dict['chrrom_size']=\
                    self.__getSize2__(flag_dict['chrrom_lsb'], \
                    flag_dict['chrrom_msb'])
            # performs shifts on 64 to get the following size values
            flag_dict['prgram_size']=\
                self.__shiftSize2__(flag_dict['prgram_shift'])
            flag_dict['nvram_size']=\
                self.__shiftSize2__(flag_dict['nvram_shift'])
            flag_dict['chrram_size']=\
                self.__shiftSize2__(flag_dict['chrram_shift'])
            flag_dict['chrnvram_size']=\
                self.__shiftSize2__(flag_dict['chrnvram_shift'])
        # NES 1.0 specific
        else:
            # prgram size
            flag_dict['prgram_size']=data[8]
            # vs system
            flag_dict['vssystem']=flag_dict['console_type'] & 1
            # playchoice 10
            flag_dict['pc10']=(flag_dict['console_type'] & 2) >> 1
            # tv system, 0 ntsc 1 pal
            flag_dict['tvsystem']=data[9] & 1
            # unofficial 1.0 headers, not respected by everything
            # tv system, 0 ntsc 2 pal 1/3 dual
            flag_dict['tvsystem_unofficial']=data[10] & 3
            # prg ram, 0 present 1 not present
            flag_dict['prgram_unofficial']=(data[10] & 16) >> 4
            # bus conflicts , 0 no conflicts 1 conflicts
            flag_dict['busconflicts_unofficial']=(data[10] & 32) >> 5

        return(flag_dict)


    def __validateNES__(self,data):
        nes_head=data[0:4]
        if nes_head != b'NES\x1a':
            raise WrongFormatError()
        return(0)

    def __getNesFormat__(self,nes2_byte):
        # to be nes2, byte 7 pos 3 == 1, pos 2 == 0, 
        # so byte7 & 0x0C should == 0x08
        if nes2_byte & 12 == 8:
            return(2)
        else:
            return(1)

    def __getVSExt__(self,console_type,byte13):
        ppu_type=False
        hw_type=False
        ext_console_type=False
        if console_type == 1:
            ppu_type=byte13 & 15
            hw_type=(byte13 & 240) >> 4
        elif console_type == 3:
            ext_console_type=(byte13 & 15)

        return(ppu_type,hw_type,ext_console_type)

    def __getChrSize1__(self,base):
        chr_ram=0
        if base == 0:
            chr_ram=1
            return(0,chr_ram)
        chrrom_size=base * 8192
        return(chrrom_size,chr_ram)

    def __getSize2__(self,lsb,msb):
        msb=msb << 8
        return(msb + lsb)

    def __shiftSize2__(self,shift):
        if shift != 0:
            return(64 << shift)
        return(0)

class bindata:
    def __init__(self,data=b''):
        self.data=data

    # extracts data from 0 to size, fills data property of object with extract,
    # returns romdata - extract
    def extract(self,romdata,size,name="ROM"):
        if size > 0:
            try:
                self.data=romdata[0:size]
                romdata=romdata[size:-1]
            except:
                raise DataNotFound("Could not extract "+name)
        return(romdata)
    
    def hash(self,func_name="sha1"):
        if func_name != "crc32" and func_name != "bytesum":
            if func_name == "sha1":
                func=sha1(self.data)
            elif func_name == "sha256":
                func=sha256(self.data)
            elif func_name == "md5":
                func=md5(self.data)
            digest=func.hexdigest()
        elif func_name == "crc32":
            digest=crc32(self.data)
        elif func_name == "bytesum":
            digest=bytesum(self.data)

        return(digest)

    # take a value and insert it in a byte
    # figures out how many bits a value needs, clears the bits at specified
    # location, then shifts value to specified location and adds new value
    def modify_bits(self,value,bit_loc,byte_loc=0):
        # put data property into bytearray
        data_array=bytearray(self.data)
        # convert from bytes to int if given as a byte
        if isinstance(value,bytes):
            value=int.from_bytes(value,"little")
        
        # if the value and bits given as parameters are not integers, error
        if not isinstance(value,int) and not isinstance(bits,int):
            raise TypeError("Value and number of bits must be integers")
        
        # get num of bits required to store value
        bits=countBits(value)

        # determine if value will fit in byte, taking into account the number
        # of bits needed + the specified bit location
        if ((bits + bit_loc) < 0) or ((bits + bit_loc) > 7):
            raise ValueError("Bit location must be within a byte (8 bits)")
        
        # get the specified byte
        try:
            source_byte=data_array[byte_loc]
        except:
            raise IndexError("Not able to find byte at "+byte_loc)
      
        # determine mask for clearing bits, by taking 2 to the power of bits,
        # -1, then shift to position
        # 
        mask=(pow(2,bits) - 1) << bit_loc

        # clear bits using mask
        source_byte=clearBits(source_byte,mask)

        # shift value to bit pos and add value to cleared byte
        output_byte=source_byte + (value << bit_loc)

        # replace in array
        data_array[byte_loc]=output_byte

        # replace existing data property with updated byte array
        self.data=bytes(data_array)


class nes_romfile:
    def __init__(self,input_file):
        self.raw=bindata()
        try:
            self.raw.data=readBytesfromFile(input_file)
        except FileNotFoundError as e:
            raise FileNotFoundError(input_file + " not found")
        except Exception as e:
            raise UnhandledError(e)
        
        if len(self.raw.data) < 16:
            raise InvalidROMSize(input_file + " size is invalid")
        
        self.header=header(self.raw.data)

        # populate rom objects
        self.__populateRomObjects__(self.raw.data[16:],self.header.flags)

        #self.data=data(self.header.header_dict,romdata)



    def __populateRomObjects__(self,romdata,header):
        self.whole_rom=bindata(romdata)
        
        if header['prgrom_size'] == 0 or\
        header['prgrom_size'] == False:
            raise DataNotFound("PRG-ROM size not specified")

        start_pos=0

        # trainer
        if header['trainer'] == 1:
            self.trainer=bindata()
            romdata=self.trainer.extract(romdata,512,'Trainer')

        # prg-rom
        self.prgrom=bindata()
        romdata=self.prgrom.extract(romdata,header['prgrom_size'],"PRG-ROM")
        
        # chr-rom
        self.chrrom=bindata()
        romdata=self.chrrom.extract(romdata,header['chrrom_size'],"CHR-ROM")
        
        # get rest of rom as misc rom
        misc_size=len(romdata)
        if misc_size > 0:
            self.miscrom=bindata()
            romdata=self.miscrom.extract(romdata,-1,"Misc Rom")
            # romdata should be empty now, so we fill it with misc data
            romdata=self.miscrom.data
        

        # we can break out the extra roms from misc based on header
        # if PC10
        if header['console_type'] == 2:
            # pc10 inst
            self.pc10_instrom=bindata()
            romdata=self.pc10_instrom.extract(romdata,8192,"PC10 INST-ROM")
            
            # pc10 prom, may not be present
            if len(romdata) >= 32:
                self.pc10_prom=bindata()
                romdata=self.pc10_prom.extract(romdata,32,"PC10 PROM")
                promdata=self.pc10_prom.data
                self.pc10_prom_data=bindata()
                self.pc10_prom_cout=bindata()
                # turn the full prom into its constituent parts
                promdata=self.pc10_prom_data.extract(promdata,16,\
                    "PC10 PROM Data")
                promdata=self.pc10_prom_cout.extract(promdata,16,\
                    "PC10 PROM CounterOut")

        # if VT369, get embedded rom
        elif header['console_type'] == 3 and header['ext_console_type'] == 10\
            and len(romdata) >= 4:
                self.vt369=bindata()
                romdata=self.vt369.extract(romdata,4,"VT369 ROM")
            
        # if mapper86 submapper1, get speech rom
        elif header['mapper'] == 86 and header['submapper'] == 1 and\
            len(romdata) > 0:
                self.jf13_speech=bindata()
                romdata=self.jf13_speech.extract(romdata,-1,"JF13 Speech ROM")
        
        # if mapper 355, get pic16c54 protection microcontroller
        elif header['mapper'] == 355 and len(romdata) > 1:
            self.pic16c54=bindata()
            romdata=self.pic16c54.extract(romdata,-1,\
                "PIC16C54 Microcontroller")
            
        # anything else, it's extra rom
        if len(romdata) > 0:
            self.extra_rom=bindata()
            romdata=self.extra_rom.extract(romdata,-1,"Extra ROM")


    def printHeader(self):
        print(self.header.__validateNES__())

def main():
    pass

if __name__ == "__main__":
    main(sys.argv[1:])

#rom=nes_romfile("Mega Man 2 (USA).nes")
#rom=nesrom("rater.py")
#print(rom.header.header_bytes)
#print(rom.header.header_dict)
#print(rom.raw.modify_bits(15,0,1))