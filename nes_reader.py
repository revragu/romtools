#!/usr/bin/env python3

import sys,getopt

from nesser import nes_romfile

def usage():
    print("nes_reader.py: prints header info from nes rom")
    print("-h - this message")
    print("-i - input nes rom")

def getHeaderFormat(val):
    if val == 1:
        return("iNES")
    elif val == 2:
        return("NES 2.0")
    raise ValueError("Header format not iNES or NES 2.0: "+val)

def getMirroring(rh):
    if rh["fourscreen"] == 0:
        if rh["mirroring"] == 0:
            return("H")
        elif rh["mirroring"] == 1:
            return("V")
        else:
            raise ValueError("Mirroring not Horizontal or Vertical "+\
                rh["mirroring"])
    elif rh["fourscreen"] > 0 and rh["fourscreen"] < 2:
        return("Four Screen")
    else:
        raise ValueError("Fourscreen mirroring set but not valid: "+\
            rh["fourscreen"])

def get20Timing(t):
    if t == 0:
        return("NTSC")
    elif t == 1:
        return("PAL")
    elif t == 2:
        return("Multiple")
    elif t == 3:
        return("Dendy")
    raise ValueError("Timing value out of range: "+t)

def getExpansion(e):
    expansion_list=["Unspecified","Standard NES/Famicom controllers","NES \
    Four Score/Satellite with two additional standard controllers","Famicom \
    Four Players Adapter with two additional standard controllers","Vs. \
    System","Vs. System with reversed inputs","Vs. Pinball (Japan)","Vs. \
    Zapper","Zapper ($4017)","Two Zappers","Bandai Hyper Shot Lightgun",\
    "Power Pad Side A","Power Pad Side B","Family Trainer Side A","Family \
    Trainer Side B","Arkanoid Vaus Controller (NES)","Arkanoid Vaus \
    Controller (Famicom)","Two Vaus Controllers plus Famicom Data Recorder",\
    "Konami Hyper Shot Controller","Coconuts Pachinko Controller","Exciting \
    Boxing Punching Bag (Blowup Doll)","Jissen Mahjong Controller","Party \
    Tap","Oeka Kids Tablet","Sunsoft Barcode Battler","Miracle Piano \
    Keyboard","Pokkun Moguraa (Whack-a-Mole Mat and Mallet)","Top Rider \
    (Inflatable Bicycle)","Double-Fisted (Requires or allows use of two \
    controllers by one player)","Famicom 3D System","Doremikko Keyboard",\
    "R.O.B. Gyro Set","Famicom Data Recorder (don't emulate keyboard)","ASCII \
    Turbo File","IGS Storage Battle Box","Family BASIC Keyboard plus Famicom \
    Data Recorder","Dongda PEC-586 Keyboard","Bit Corp. Bit-79 Keyboard",\
    "Subor Keyboard","Subor Keyboard plus mouse (3x8-bit protocol)","Subor \
    Keyboard plus mouse (24-bit protocol)","SNES Mouse ($4017.d0)",\
    "Multicart","Two SNES controllers replacing the two standard NES \
    controllers","RacerMate Bicycle","U-Force","R.O.B. Stack-Up","City \
    Patrolman Lightgun","Sharp C1 Cassette Interface","Standard Controller \
    with swapped Left-Right/Up-Down/B-A","Excalibor Sudoku Pad","ABL Pinball",\
    "Golden Nugget Casino extra buttons"]

    try:
        return(expansion_list[e])
    except:
        raise ValueError("Expansion out of range: ",e)

def getTrue(val):
    if val == 0:
        return(False)
    elif val == 1:
        return(True)
    raise ValueError("Value must be 1 or 0")

def parseHeader(rh):
    header_dict={}
    header_dict["Header Format"] = getHeaderFormat(rh["header_format"])
    header_dict["Mirroring"] = getMirroring(rh)
    header_dict["Battery"]=getTrue(rh["battery"])
    header_dict["Trainer"]=getTrue(rh["trainer"])
    header_dict["PRG-ROM Size"]=rh["prgrom_size"]
    header_dict["CHR-ROM Size"]=rh["chrrom_size"]
    # NES 2.0
    if rh["header_format"] == 2:
        header_dict["Mapper"]=[{"Number": rh["mapper"],\
            "Submapper": rh["submapper"]}]
        header_dict["CHR-RAM Size"]=rh["chrram_size"]
        header_dict["NVRAM Size"]=rh["nvram_size"]
        header_dict["CHR-NVRAM Size"]=rh["chrnvram_size"]
        header_dict["TV System Timing"]=get20Timing(rh["timing"])
        header_dict["Number of Misc Roms"]=rh["miscroms"]
        header_dict["Expansion Device"]=getExpansion(rh["expansion_device"])

    return(header_dict)

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:")
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
        elif opt in ("-i"):
            input_file = arg
            
            try:
                rom=nes_romfile(input_file)    
            except FileNotFoundError:
                raise FileNotFoundError("Input file "+input_file+" not found")
            except PermissionError:
                raise PermissionError("Unable to read input file "+input_file+" due to permissions restrictions")
            except Exception as e:
                raise Exception(e)

    print(parseHeader(rom.header.flags))

if __name__ == "__main__":
    main(sys.argv[1:])