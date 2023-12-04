#!/usr/bin/env python3

import sys,getopt

from nesser import nes_romfile
from ragu_file import printJson

def usage():
    print("nes_reader.py: prints header info from nes rom")
    print("-h - this message")
    print("-i - input nes rom")

def getTrue(val):
    if val == 0:
        return(False)
    elif val == 1:
        return(True)
    raise IndexError("Value must be 1 or 0: "+val)


def getMirroring(rh):
    if rh["mirroring"] == 0:
        return("H")
    elif rh["mirroring"] == 1:
        return("V")
    else:
        raise IndexError("Mirroring not Horizontal or Vertical "+\
            rh["mirroring"])


def get20Flags(rh):
    expansion_list=[
        "Unspecified",
        "Standard NES/Famicom controllers",
        "NES Four Score/Satellite with two additional standard controllers",
        "Famicom Four Players Adapter with two additional standard controllers",
        "Vs. System",
        "Vs. System with reversed inputs",
        "Vs. Pinball (Japan)",
        "Vs. Zapper",
        "Zapper ($4017)",
        "Two Zappers",
        "Bandai Hyper Shot Lightgun",
        "Power Pad Side A",
        "Power Pad Side B",
        "Family Trainer Side A",
        "Family Trainer Side B",
        "Arkanoid Vaus Controller (NES)",
        "Arkanoid Vaus Controller (Famicom)",
        "Two Vaus Controllers plus Famicom Data Recorder",
        "Konami Hyper Shot Controller",
        "Coconuts Pachinko Controller",
        "Exciting Boxing Punching Bag (Blowup Doll)",
        "Jissen Mahjong Controller",
        "Party Tap",
        "Oeka Kids Tablet",
        "Sunsoft Barcode Battler",
        "Miracle Piano Keyboard",
        "Pokkun Moguraa (Whack-a-Mole Mat and Mallet)",
        "Top Rider (Inflatable Bicycle)",
        "Double-Fisted (Requires or allows use of two controllers by one player)",
        "Famicom 3D System",
        "Doremikko Keyboard",
        "R.O.B. Gyro Set",
        "Famicom Data Recorder (don't emulate keyboard)",
        "ASCII Turbo File",
        "IGS Storage Battle Box",
        "Family BASIC Keyboard plus Famicom Data Recorder",
        "Dongda PEC-586 Keyboard",
        "Bit Corp. Bit-79 Keyboard",
        "Subor Keyboard",
        "Subor Keyboard plus mouse (3x8-bit protocol)",
        "Subor Keyboard plus mouse (24-bit protocol)",
        "SNES Mouse ($4017.d0)",
        "Multicart",
        "Two SNES controllers replacing the two standard NES controllers",
        "RacerMate Bicycle",
        "U-Force",
        "R.O.B. Stack-Up",
        "City Patrolman Lightgun",
        "Sharp C1 Cassette Interface",
        "Standard Controller with swapped Left-Right/Up-Down/B-A",
        "Excalibor Sudoku Pad",
        "ABL Pinball",
        "Golden Nugget Casino extra buttons"
    ]

    ext_console_list=[
        "Regular NES/Famicom/Dendy","Vs. System",
        "Playchoice 10",
        "Regular Famiclone with Decimal Mode support",
        "Regular NES/Famicom with EPSM module/plug-through cartridge",
        "V.R. Technology VT01 with red/cyan STN palette",
        "V.R. Technology VT02",
        "V.R. Technology VT03",
        "V.R. Technology VT09",
        "V.R. Technology VT32",
        "V.R. Technology VT369",
        "UMC UM6578",
        "reserved",
        "reserved",
        "reserved",
        "reserved"
    ]

    vs_type_list=[
        "RP2C03B",
        "RP2C03G",
        "RP2C04-0001",
        "RP2C04-0002",
        "RP2C04-0003",
        "RP2C04-0004",
        "RC2C03B",
        "RC2C03C",
        "RC2C05-01 ($2002 AND $?? =$1B)",
        "RC2C05-02 ($2002 AND $3F =$3D)",
        "RC2C05-03 ($2002 AND $1F =$1C)",
        "RC2C05-04 ($2002 AND $1F =$1B)",
        "RC2C05-05 ($2002 AND $1F =unknown)",
        "reserved",
        "reserved",
        "reserved"
    ]

    vs_ppu_list=[
        "Vs. System (normal)",
        "Vs. System (RBI Baseball protection)",
        "Vs. System (TKO Boxing protection)",
        "Vs. System (Super Xevious protection)",
        "Vs. Ice Climber Japan protection",
        "Vs. Dual System (normal)",
        "Vs. Dual System (Raid on Bungeling Bay protection)"
    ]


    twooh_flags={}
    twooh_flags['RAM']={}
    twooh_flags['Misc Roms']={}
    twooh_flags['TV System']={}
    twooh_flags['RAM']["PRG-RAM Size"]=rh["prgram_size"]
    twooh_flags["Mapper"]={"Number": rh["mapper"],\
        "Submapper": rh["submapper"]}
    twooh_flags['RAM']["CHR-RAM Size"]=rh["chrram_size"]
    twooh_flags['RAM']["NVRAM Size"]=rh["nvram_size"]
    twooh_flags['RAM']["CHR-NVRAM Size"]=rh["chrnvram_size"]
    twooh_flags['Misc Roms']["Number"]=rh["miscroms"]
    if rh["timing"] == 0:
        twooh_flags['TV System']["Timing"]="NTSC"
    elif rh["timing"] == 1:
        twooh_flags['TV System']["Timing"]="PAL"
    elif rh["timing"] == 2:
        twooh_flags['TV System']["Timing"]="Multiple"
    elif rh["timing"] == 3:
        twooh_flags['TV System']["Timing"]="Dendy"
    else:
        raise ValueError("Timing value out of range: "+rh["timing"])

    try:
        twooh_flags["Expansion Device"]=expansion_list[rh["expansion_device"]]
    except:
        raise ValueError("Expansion out of range: ",rh["expansion_device"])

    if rh["console_type"] == 0 or rh["ext_console_type"] == 0:
        twooh_flags["Extended Console"]={"Regular NES/Famicom/Dendy":True}
    elif rh["console_type"] == 1 or rh["ext_console_type"] == 1:
        try:
            rh["Extended Console"]={"Vs. System": {
                    "Type": vs_type_list[rh["vssystem_type"]],
                    "PPU": vs_ppu_list[rh["vssystem_ppu"]]
                }
            }
        except:
            raise ValueError("Determined console was Vs. System, but Type or \
                PPU in header invalid")
    elif rh["console_type"] == 2 or rh["ext_console_type"] == 2:
        twooh_flags["Extended Console"]={"Playchoice 10":True}
    else:
        try:
            rh["Extended Console"]=ext_console_list[rh["ext_console_type"]]
        except:
            raise ValueError("Console at location "+rh["ext_console_type"]+\
                " not extended console type")


    return(twooh_flags)

def get10Flags(rh):
    ines_dict={}
    ines_dict['RAM']={}
    ines_dict['TV System']={}
    ines_dict["Mapper"]={"Number": rh["mapper"]}

    if rh["tvsystem"] == 0:
        ines_dict['TV System']["Timing"]="NTSC"
    elif rh["tvsystem"] == 1:
        ines_dict['TV System']["Timing"]="PAL"


    if (rh["tvsystem"] == 0 and rh["tvsystem_unofficial"] != 0) or\
    rh["tvsystem_unofficial"] > 0:
        if rh["tvsystem_unofficial"] == 0:
            ines_dict['TV System']["Timing (Unofficial)"] = "NTSC"
        elif rh["tvsystem_unofficial"] == 2:
            ines_dict['TV System']["Timing (Unofficial)"] = "PAL"
        elif rh["tvsystem_unofficial"] == 1 or rh["tvsystem_unofficial"] == 3:
            ines_dict['TV System']["Timing (Unofficial)"] = "Dual"
        else:
            raise IndexError(rh["tvsystem_unofficial"]+" out of range for TV \
                system (unoffical) index")

    if rh["vssystem"] == 1:
        ines_dict["Extended Console"]={"Vs System":True}
    elif rh["pc10"] == 1:
        ines_dict["Extended Console"]={"Playchoice 10":True}
    else:
        ines_dict["Extended Console"]={"Regular NES/Famicom/Dendy":True}

    ines_dict["RAM"]["PRG-RAM (Unofficial)"]=getTrue(rh["prgram_unofficial"])
    ines_dict["Bus Conflicts (Unofficial)"]=\
        getTrue(rh["busconflicts_unofficial"])
    return(ines_dict)

def getCommonFlags(rh):
    common_flags={}
    common_flags["ROMS"]={}
    common_flags["ROMS"]["Whole ROM"]={}
    common_flags["ROMS"]["PRG-ROM"]={}
    common_flags["ROMS"]["CHR-ROM"]={}
    if rh["header_format"] == 1:
        common_flags["Header Format"]="iNES"
    elif rh["header_format"] == 2:
        common_flags["Header Format"]="NES 2.0"
    else:
        raise IndexError("Header format not iNES or NES 2.0: "+rh["header_format"])

    if rh["fourscreen"] == 0:
        common_flags["Mirroring"]=getMirroring(rh)
    elif rh["fourscreen"] > 0 and rh["fourscreen"] < 2:
        common_flags["Mirroring"]="Four Screen"
    else:
        raise IndexError("Fourscreen mirroring set but not valid: "+\
            rh["fourscreen"])
   
    common_flags["Battery"]=getTrue(rh["battery"])
    common_flags["Trainer"]=getTrue(rh["trainer"])
    common_flags["ROMS"]["PRG-ROM"]["Size"]=rh["prgrom_size"]
    common_flags["ROMS"]["CHR-ROM"]["Size"]=rh["chrrom_size"]
    return(common_flags)

def parseHeader(rh):
    header_dict={}
    header_dict=getCommonFlags(rh)
    # NES 2.0
    if rh["header_format"] == 2:
        header_dict.update(get20Flags(rh))
        return(header_dict)
    elif rh["header_format"] == 1:
        header_dict.update(get10Flags(rh))
        return(header_dict)


def parseRom(rom,get_rom):
    rom_dict={}
    if get_rom == True:
        rom_dict["ROM Object"]=rom
    rom_dict.update(parseHeader(rom.header.flags))

    rom_dict["Raw Header"]=rom.header.raw.data

    rom_dict["ROMS"]["Whole ROM"]["Size"]=len(rom.raw.data)

    main_roms=["whole_rom","prgrom","chrrom","trainer","pc10_prom_data",\
        "pc10_prom_cout","vt369","jf13_speech","pic16c54","extra_rom"]

    for r in main_roms:
        hash={}
        try:
            romdata=getattr(rom,r)
            hash["Size"]=len(romdata.data)
            if hash["Size"] != 0:
                hash["Bytesum"]=romdata.hash('bytesum')
                hash["CRC32"]=romdata.hash('crc32')
                hash["MD5"]=romdata.hash('md5')
                hash["SHA1"]=romdata.hash('sha1')
                hash["SHA256"]=romdata.hash('sha256')
            
                if r == "whole_rom":
                    rom_dict["ROMS"]["Whole ROM"].update(hash)
                elif r == "prgrom":
                    rom_dict["ROMS"]["PRG-ROM"].update(hash)
                elif r == "chrrom":
                    rom_dict["ROMS"]["CHR-ROM"].update(hash)
                elif r == "trainer":
                    rom_dict["ROMS"]["Trainer"].update(hash)
                elif r == "pc10_prom_data":
                    rom_dict["ROMS"]["PC10 PROM Data"].update(hash)
                elif r == "pc10_prom_cout":
                    rom_dict["ROMS"]["PC10 PROM COut"].update(hash)
                elif r == "vt369":
                    rom_dict["ROMS"]["VT369 ROM"].update(hash)
                elif r == "jf13_speech":
                    rom_dict["ROMS"]["JF13 Speech ROM"].update(hash)
                elif r == "pic16c54":
                    rom_dict["ROMS"]["pic16c54 ROM"].update(hash)
                else:
                    rom_dict["ROMS"]["Extra ROM"].update(hash)
        except:
            pass

    
    return(rom_dict)

def nesinfo(input_file, get_rom):
    rom_dict={}
    try:
        rom=nes_romfile(input_file)
    except FileNotFoundError:
        raise FileNotFoundError("Input file "+input_file+" not found")
    except PermissionError:
        raise PermissionError("Unable to read input file "+input_file\
        +"due to permissions restrictions")
    except Exception as e:
        raise Exception(e)

    rom_dict["Input ROM"]=input_file
    rom_dict.update(parseRom(rom,get_rom))
    return(rom_dict)


def main(argv):
    get_rom=False
    try:
        opts, args = getopt.getopt(argv,"hi:r:")
    except getopt.GetoptError:
        usage()
        raise(getopt.GetoptError("Invalid option "+opts))
    if len(opts) == 0:
        print("No options defined")
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        elif opt == "-i":
            input_file = arg
        # pull rom object into parsed dict
        elif opt == "-r":
            get_rom=True


    rom_dict=nesinfo(input_file, get_rom)
    printJson(rom_dict)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])