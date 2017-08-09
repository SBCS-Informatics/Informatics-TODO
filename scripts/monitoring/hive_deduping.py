#!/usr/bin/env python
import sys, time, argparse, os, hashlib
from pwd import getpwuid
from multiprocessing import Pool

NUM_THREADS=8
WRITE_HASH_TO_FILE=1

##used for binary test. not fool proof but good enough for this use case
##taken from https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
def is_binary(filename):
    file_part = open(filename, 'rb').read(1024)
    return bool(file_part.translate(None, textchars))

##main function
def main():
    #time start
    t_zero = time.time()

    #usage
    if len(sys.argv)!=2:
        exit("usage: hive_deduping.py <root folder>")
    
    #check root path to make sure it exists
    if os.path.isdir(sys.argv[1]):
        print "DEDUPING %s"%sys.argv[1]
        root=sys.argv[1]
    else:
        exit("%s directory does not exist"%sys.argv[1])
    
    list_of_files = find_all_files(root)
    print len(list_of_files), "files"

    #for f in list_of_files:
    #    if is_binary(f):
    #        print f, "binary"
    #    else:
    #        print f, "NONbinary"
    
    
    list_of_hashes = multithread_run(hash_file, list_of_files)
    
    file_dict=dict()

    print round(time.time()-t_zero), "seconds"
    for f in list_of_hashes:
        if f[0] in file_dict.keys():
            file_dict[f[0]].append(f[2])
        else:
            file_dict[f[0]]=f[1:]
    
    duplicated_files=dict()

    for key in file_dict.keys():
        if len(file_dict[key]) > 2:
            duplicated_files[key]=file_dict[key]
    
    total_size,reduced_size = size_of_dups(duplicated_files)
    print total_size/1000000000, reduced_size/1000000000
    
    print round(time.time()-t_zero), "seconds"
    tmp_file_list = find_tmp_files(list_of_files)
    print len(tmp_file_list), "tmp files"
    print round(time.time()-t_zero), "seconds"

def multithread_run(func_to_run, args_list):
    pool = Pool(processes=NUM_THREADS)
    results_list = list()
    
    for i in pool.imap_unordered(func_to_run, args_list):
        if WRITE_HASH_TO_FILE:
            pass
        results_list.append(i)
    return results_list

def size_of_dups(dups):
    total_size=0
    reduced_size=0
    for key in dups.keys():
        reduced_size+=float(dups[key][0])
        total_size+=float(dups[key][0])*(len(dups[key])-1)
    return (total_size, reduced_size)

def get_uid(filename):
    return getpwuid(stat(filename).st_uid).pw_name

def find_all_files(root):
    list_of_files=list()
    for path, subdirs, files in os.walk(root):
        for name in files:
            if not os.path.islink(os.path.join(path, name)):
                list_of_files.append(os.path.join(path, name))
    return list_of_files

def find_tmp_files(file_list):
    tmp_files=list()
    for f in file_list:
        if "tmp" in f:
            tmp_files.append(f)
    return tmp_files

#SHA256 hash of file    
#Size of file in bytes
def hash_file(filename):
    return [hashlib.sha256(open(filename, 'rb').read()).hexdigest(), os.path.getsize(filename), filename]

if __name__ == "__main__":
    main()
