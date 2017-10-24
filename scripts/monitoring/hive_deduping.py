#!/usr/bin/env python
import sys, time, argparse, os, hashlib
from pwd import getpwuid
from multiprocessing import Pool

#DEFAULTS
NUM_THREADS=20
WRITE_HASH_TO_FILE=1

### MAIN ###
def main():
    #time start and date
    t_zero = time.time()
    date_string = time.strftime("%Y_%m_%d",time.localtime())

    #usage
    if len(sys.argv)<2:
        exit("usage: hive_deduping.py <root folder>")
    
    #check root path to make sure it exists
    if os.path.isdir(sys.argv[1]):
        print "DEDUPING %s"%sys.argv[1:]
        roots=sys.argv[1:]
    else:
        exit("%s directory does not exist"%sys.argv[1])
    
    list_of_files = []
    list_of_dirs = []
    for root in roots:
        #List all files and directories under the root directory provided
        tmp_files, tmp_dirs = find_all_files(root)
        list_of_files = list_of_files + tmp_files
        list_of_dirs = list_of_dirs + tmp_dirs
    
    print len(list_of_dirs), "directories"
    print len(list_of_files), "files"

    ### LOOK FOR DIRS WITH MORE THAN 100 ENTRIES IN THEM ###
    list_of_dirs_to_tar = list()
    nested_to_tar=dict()
    users_tar=list()
    for d in sorted(list_of_dirs):
        try: #Escape OSErrors caused by unreadable directories
            if len(os.listdir(d))>100:
                for dd in list_of_dirs_to_tar:
                    if dd+"/" in d:
                        if dd in nested_to_tar.keys():
                            nested_to_tar[dd].append(d)
                        else:
                            nested_to_tar[dd]=[d]
                user = get_uid(d)
                if user not in users_tar:
                    users_tar.append(user)
                list_of_dirs_to_tar.append(d)
        except OSError as e:
            print "ERROR: ", e
    for key in nested_to_tar.keys():
        for nested_dir in nested_to_tar[key]:
            #print key, nested_dir
            try:
                list_of_dirs_to_tar.remove(nested_dir)
            except ValueError as e:
                print "ERROR: ", e

    #print list_of_dirs_to_tar
    #print nested_to_tar

    
    #calculate checksum values and file size for all files
    #[[hash, filesize, filename], ...]
    t_hash_zero = time.time()
    list_of_hashes = multithread_run(hash_file, list_of_files)
    t_hash = time.time()-t_hash_zero
    print round(t_hash, 2), "s hash time"

    #file_dict will keep a hash and its corresponding files
    file_dict=dict()
    #files_to_compress will keep a list of all files that should be compressed: 
    #>100MB and nonbinary as defined by function is_binary
    files_to_compress=list()
    total_uncompressed_size=0 
    users_dedup=list()
    users_compress=list()

    
    
    #Go through all the hash values and see if there are duplicates
    #Also check if the files are binary and if not add to list
    for f in list_of_hashes:
        try: #Escape errors caused by unreadable files 
            user=get_uid(f[2])
        except OSError as e:
            print "ERROR: ", e
            continue
        if f[0] not in file_dict.keys():
            #if this hash is not already in the dict
            #add the hash, point to the filesize and the filename f[1:]
            file_dict[f[0]]=f[1:]
        else:
            #if hash is there already, this is a duplicate file
            #only need to add its filename f[2], 
            #already have the size
            file_dict[f[0]].append(f[2])
            #Going to store user too
            if user not in users_dedup:
                users_dedup.append(user)

        #Going to check file size and if file is binary in the same loop
        file_size=float(f[1])
        if file_size > 100000000: #Filesize > than 100MiB
            #Only check if its binary if its large enough to be on list
            if not is_binary(f[2]):
                #add to list
                total_uncompressed_size+=file_size
                files_to_compress.append([user, f[2]])
                #add user to list
                if user not in users_compress:
                    users_compress.append(user)

    #print files_to_compress, file_size/1000000000
    print "Approximate space that could be saved by compressing {} files: {} GiB".format(len(files_to_compress),total_uncompressed_size/1000000000*0.6)

    duplicated_files=dict()

    for key in file_dict.keys():
        if len(file_dict[key]) > 2:
            duplicated_files[key]=file_dict[key]
    
    total_size,reduced_size,num_to_dedup = size_of_dups(duplicated_files)
    print "Possible space to saved by deduping {} files: {} GiB".format(num_to_dedup, total_size/1000000000 - reduced_size/1000000000)
    
    tmp_file_list = find_tmp_files(list_of_files)
    print len(tmp_file_list), "tmp files"

    ###REPORT###
    #Open logfiles to write to

    if len(duplicated_files)>0:
        logfile = open("hive_deduping_duplicatedfiles_"+date_string+".log", "w")
        logfile_users=dict()
        for user in users_dedup:
            logfile_user="hive_deduping_duplicatedfiles_"+date_string+".log."+user
            logfile_users[user]=open(logfile_user, "w")

        for key in duplicated_files.keys():
            users_key = list() 
            for dupfile in sorted(duplicated_files[key][1:]):
                user = get_uid(dupfile)
                if user not in users_key:
                    users_key.append(user)
                logfile.write("{}\t{}\t{}\t{}\n".format(key, user, duplicated_files[key][0], dupfile))
            
            logfile.write("\n")
            for user_key in users_key:
                for dupfile in sorted(duplicated_files[key][1:]):
                    user = get_uid(dupfile)
                    logfile_users[user_key].write("{}\t{}\t{}\n".format(key, duplicated_files[key][0], dupfile))
                logfile_users[user_key].write("\n")
                
        #Close logfiles
        logfile.close() 
        for user in users_dedup:
            logfile_users[user].close()

    if len(files_to_compress)>0:
        logfile = open("hive_deduping_filestocompress_"+date_string+".log", "w")
        logfile_users=dict()
        for user in users_compress:
            logfile_user="hive_deduping_filestocompress_"+date_string+".log."+user
            logfile_users[user]=open(logfile_user, "w")
        
        for f in files_to_compress:
            logfile.write("{}\t{}\n".format(f[0],f[1]))
            logfile_users[f[0]].write("{}\n".format(f[1]))
        
        #Close logfiles
        for user in users_compress:
            logfile_users[user].close()
        logfile.close()

    if len(list_of_dirs_to_tar)>0:
        nested_to_tar
        logfile = open("hive_deduping_dirstotar_"+date_string+".log", "w")
        for user in users_tar:
            logfile_user="hive_deduping_dirstotar_"+date_string+".log."+user
            logfile_users[user]=open(logfile_user, "w")
        for d in list_of_dirs_to_tar:
            user = get_uid(d)
            logfile.write("{}\t{}\n".format(user, d))
            logfile_users[user].write("{}\n".format(d))
            if d in nested_to_tar.keys():
                for dd in nested_to_tar[d]:
                    user_nested = get_uid(dd)
                    logfile.write("\t{}\t{}\n".format(user_nested, dd))
                    logfile_users[user].write("\t{}\n".format(dd))
                    if not user==user_nested:
                        logfile_users[user_nested].write("{}\t{}\n".format(user_nested, dd))

        #Close logfiles
        for user in users_tar:
            logfile_users[user].close()
        logfile.close()




### FUNCTIONS ###

##used for binary test. not fool proof but good enough for this use case
##taken from https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
def is_binary(filename):
    file_part = open(filename, 'rb').read(1024)
    return bool(file_part.translate(None, textchars))

def multithread_run(func_to_run, args_list):
    result_list=list()
    for i in args_list:
        result_list.append(func_to_run(i))
    #return result_list
    pool = Pool(processes=NUM_THREADS)
    result_list = list()
    
    for i in pool.imap_unordered(func_to_run, args_list):
        if WRITE_HASH_TO_FILE:
            pass
        result_list.append(i)
    return result_list

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
    list_of_subdirs=list()
    for path, subdirs, files in os.walk(root):
        for name in files:
            if not os.path.islink(os.path.join(path, name)):
                list_of_files.append(os.path.join(path, name))
        for subdir in subdirs:
            list_of_subdirs.append(os.path.join(path, subdir))
    return list_of_files, list_of_subdirs

def find_tmp_files(file_list):
    tmp_files=list()
    for f in file_list:
        if "tmp" in f:
            tmp_files.append(f)
    return tmp_files

#SHA256 hash of file    
#Size of file in bytes
def hash_file(filename):
    try: #Escape any errors caused by unreadable files IOError is from reading the file OSError from getting its size
        return [hashlib.sha256(open(filename, 'rb').read()).hexdigest(), os.path.getsize(filename), filename]
    except (OSError, IOError) as e:
        print "ERROR: ", e
        return ["ERROR_IN_HASH", 0, filename]

if __name__ == "__main__":
    main()
