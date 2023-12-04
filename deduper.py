#!/usr/bin/env python3

import sys,os,getopt,re,shutil,binascii,multiprocessing,signal
from pathlib import Path
from hashlib import md5

def usage():
    print("./deduper.py -s [scan path] -t [target path]")

def getSources(path):
    if path.is_file():
        return(md5(open(path,'rb').read()).hexdigest())

def getTargets(path):
    if path.is_file():
        return({"path": path, "md5": md5(open(path,'rb').read()).hexdigest()})

class deduper:
    def __init__(self,cpus=0):
        max_cpus=int(multiprocessing.cpu_count()) - 1
        if cpus == 0 or cpus > max_cpus:
            self.cpus=max_cpus
        elif max_cpus <= 0 or cpus > max_cpus:
            self.cpus=1
        
        self.source_set=set()
        self.target_paths=[]


    def scanSource(self,source_path):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool_obj = multiprocessing.Pool(processes=self.cpus)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            source_catalog=pool_obj.map(getSources,Path(source_path).rglob('*'))
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Aborted")
        except Exception as e:
            raise Exception(e)

        self.source_set=set(source_catalog)
    
    def scanTarget(self,target_path):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool_obj = multiprocessing.Pool(processes=self.cpus)
        signal.signal(signal.SIGINT, original_sigint_handler)

        try:
            self.target_paths=pool_obj.map(getTargets,Path(target_path).rglob('*'))
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Aborted")
        except Exception as e:
            raise Exception(e)


    def delDups(self):
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        pool_obj = multiprocessing.Pool(processes=self.cpus)
        signal.signal(signal.SIGINT, original_sigint_handler)

        pool_obj.map(self.delDup,self.target_paths)

    def delDup(self,file):

        try:
            if file["md5"] in self.source_set:
                print("Deleting: " + str(file["path"]) )
                os.remove(file["path"])
        except:
            pass


    def uniqCheck(self,uniq_path,file):
        uniq_files=[u for u in os.listdir(uniq_path) if Path(os.path.join(uniq_path,u)).is_file()]
        
        if os.path.basename(file) not in uniq_files:
            return(file)
        else:
            filename, ext=os.path.splitext(file)
            iter_match=re.sub(r'.*_([0-9]+)$',r'\1',str(filename))
            filename_base=re.sub(r'_[0-9]+$',r'',str(filename))
            
            try:
                iter=int(iter_match) + 1
                iter_str="_"+str(iter)
            except:
                iter_str="_0"
            filename_out=filename_base+iter_str+ext
            filename_out=self.uniqCheck(uniq_path,filename_out)
            return(filename_out)



    def copyUniq(self,uniq_path):
        for f in self.target_paths:
            try:
                if f["md5"] not in self.source_set:
                    print("checking for duplicate filename")
                    out_file=os.path.basename(self.uniqCheck(uniq_path,f['path']))
                    print("Copying to " + str(uniq_path) + ": " + str(f['path']) )
                    out_path=os.path.join(uniq_path,out_file)
                    shutil.copy(f['path'],Path(out_path))
            except:
                pass



def getUniq(source_pathname,target_pathname,uniq_pathname):
    dedup_obj=deduper()
    dedup_obj.scanSource(source_pathname)
    dedup_obj.scanTarget(target_pathname)
    dedup_obj.copyUniq(uniq_pathname)
    sys.exit(0)

def getDel(source_pathname,target_pathname):
    dedup_obj=deduper()
    dedup_obj.scanSource(source_pathname)
    dedup_obj.scanTarget(target_pathname)
    dedup_obj.delDups()
    sys.exit(0)

def main(argv):
    cpus=int(multiprocessing.cpu_count()) - 1
    if cpus <= 0:
        cpus=1

    source_pathname=''
    target_pathname=''
    uniq_pathname=''
    delete_paths=''
    scan_catalog=[]

    try:
        opts, args = getopt.getopt(argv,"hs:t:c:u:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-s"):
            source_pathname = arg
        elif opt in ("-t"):
            target_pathname = arg
        elif opt in ("-c"):
            cpus = int(arg)
        elif opt in ("-u"):
            uniq_pathname = arg

    if source_pathname == '' or target_pathname == '':
        usage()
        raise Exception("Pathnames not defined")

    if uniq_pathname != '':
        getUniq(source_pathname,target_pathname,uniq_pathname)

    getDel(source_pathname,target_pathname)


if __name__ == "__main__":
   main(sys.argv[1:])