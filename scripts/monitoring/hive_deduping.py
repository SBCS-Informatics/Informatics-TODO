#!/usr/bin/env python
import sys, time, argparse, os, hashlib
from pwd import getpwuid
from multiprocessing import Pool

NUM_THREADS=8
WRITE_HASH_TO_FILE=1

date_string = time.strftime("%Y_%m_%d",time.localtime())

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
    
    
    #list of hash values, the file and its file size
    #[[hash, filesize, filename], ...]
    list_of_hashes = multithread_run(hash_file, list_of_files)
    
    #file_dict will keep a hash and its corresponding files
    file_dict=dict()
    #files_to_compress will keep a list of all files that should be compressed: 
    #>100MB and nonbinary as defined by function is_binary
    files_to_compress=list()
    total_uncompressed_size=0 
    
    print round(time.time()-t_zero), "seconds"
    
    
    #Go through all the hash values and see if there are duplicates
    #Also check if the files are binary and if not add to list
    for f in list_of_hashes:
        if f[0] not in file_dict.keys():
            #if this hash is not already in the dict
            #add the hash, point to the filesize and the filename f[1:]
            file_dict[f[0]]=f[1:]
        else:
            #if hash is there already, this is a duplicate file
            #only need to add its filename f[2], 
            #already have the size
            file_dict[f[0]].append(f[2])
        
        #Going to check file size and if file is binary in the same loop
        file_size=float(f[1])
        if file_size > 100000000: #Filesize > than 100MiB
            #Only check if its binary if its large enough to be on list
            if not is_binary(f[2]):
                #add to list
                total_uncompressed_size+=file_size
                files_to_compress.append([get_uid(f[2]), f[2]])

    #print files_to_compress, file_size/1000000000
    print "Approximate space that could be saved by compressing {} files: {} GiB".format(len(files_to_compress),total_uncompressed_size/1000000000*0.6)

    duplicated_files=dict()

    for key in file_dict.keys():
        if len(file_dict[key]) > 2:
            duplicated_files[key]=file_dict[key]
    
    total_size,reduced_size,num_to_dedup = size_of_dups(duplicated_files)
    print "Possible space to saved by deduping {} files: {} GiB".format(num_to_dedup, total_size/1000000000 - reduced_size/1000000000)
    
    print round(time.time()-t_zero), "seconds"
    tmp_file_list = find_tmp_files(list_of_files)
    print len(tmp_file_list), "tmp files"
    print round(time.time()-t_zero), "seconds"

    ###REPORT###
    #Open logfiles to write to

    if len(duplicated_files)>0:
        logfile = open("hive_deduping_duplicatedfiles_"+date_string+".log", "w")
        for key in duplicated_files.keys():
            users = list() 
            for dupfile in sorted(duplicated_files[key][1:]):
                user = get_uid(dupfile)
                logfile.write("{}\t{}\t{}\n".format(key, user, dupfile))

                if user not in users:
                    users.append(user)
                logfile_user="hive_deduping_duplicatedfiles_"+date_string+".log."+user
                if os.path.exists(logfile_user):
                    append_write = 'a' # append if already exists
                else:
                    append_write = 'w' # make a new file if not
                logfile_user = open(logfile_user, append_write)
                logfile_user.write("{}\t{}\t{}\n".format(key, user, dupfile))
                logfile_user.close()
            for user in users:
                logfile_user="hive_deduping_duplicatedfiles_"+date_string+".log."+user
                logfile_user = open(logfile_user, "a")
                logfile_user.write("\n")
                logfile_user.close()
                
            logfile.write("\n")
        logfile.close() 

    if len(files_to_compress)>0:
        logfile = open("hive_deduping_filestocompress_"+date_string+".log", "w")
        logfile_user = open("hive_deduping_filestocompress_"+date_string+".log."+user, "w")
        
        logfile.write(str(files_to_compress))
        logfile.close()



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
    num_files=0
    for key in dups.keys():
        reduced_size+=float(dups[key][0])
        total_size+=float(dups[key][0])*(len(dups[key])-1)
        num_files+=len(dups[key])-1
    return (total_size, reduced_size, num_files)

def get_uid(filename):
    return getpwuid(os.stat(filename).st_uid).pw_name

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
