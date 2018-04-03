#!/usr/bin/env python
from __future__ import division
import time, os, requests, argparse, subprocess

#Counting the time
t_zero = time.time()

#Command line argument parsing
parser = argparse.ArgumentParser(description="Singularity software grabber from quay.io Biocontainers for Apocrita, written by Adrian Larkeryd, 2018")
parser.add_argument("software_list",
        help="textfile with one software on each line, all lowercase [REQUIRED]")
parser.add_argument("--verbose", "-v",
        help="verbose mode", action="store_true")
args = parser.parse_args()
 
#Grab all the software that were in the file
software = [line.rstrip() for line in open(args.software_list, "r")]

#Open a file that will be used to write some shell commands in. This file will later be ran by subprocess from this script
shellscript_file = open(args.software_list + ".sh", "w")
#First thing in the shellscript file is that singularity will have to be loaded
shellscript_file.write("module load singularity/2.4.2\n")
if args.verbose:
    print "module load singularity/2.4.2"

#Will contain container names
containers = list()
#Will contain eventual misses in the search, eg software that wasnt available in Biocontainers or misspelled names
software_unavailable = list()

#Go through all software
for soft in software:
    
    if soft == "" or soft[0] == "#": #NOTE: works because of lazy python, will not check second bit if first is true
         continue #Comment line should not be used

    if args.verbose:
        print "\n#Checking tags for {}".format(soft)
        print "#GET request for URL: {}".format('https://quay.io/api/v1/repository/biocontainers/{}/tag/'.format(soft))

    #Do a GET request to the quay.io API to get all tags associated with a tool name under the organisation biocontainers
    resp = requests.get('https://quay.io/api/v1/repository/biocontainers/{}/tag/'.format(soft))
    
    #Check if there was a response to the GET req
    try:
        soft_json = resp.json()
    except ValueError as e:
        #No response at all, not sure what happens here?? Just move on to the next line
        software_unavailable.append(soft)
        continue

    #Catch any KeyErrors as they mean the request was unsuccessful
    try:
        newest_tag = soft_json["tags"][0]
    except KeyError as e:
        #This is problably due to a faulty software name as opposed to the previous ValueError
        print "#{} ERROR: {} when trying to get tags for software {}".format(soft_json["status"], soft_json["error_type"], soft)
        software_unavailable.append(soft)
        continue
    latest_tag = newest_tag

    #Write comment to the shell script
    shellscript_file.write("\n#{}\n".format(soft))

    #Will contain tags that could not be compared (probably due to strange version names with non-digits like 1.1a)
    cant_compare_list = list()

    #Go through all tags that are available with the software
    for tag in soft_json["tags"]:
        tname = tag["name"]

        latest_tname = latest_tag["name"]

        #Tags come in the form 1.1.1--otherinformation
        #where the part after the -- usually contains information on other software installed in the container, often python versions
        #Splitting it up and will only compare based on numbers in the first part
        ltnsplit = latest_tname.split("--")
        nsplit = tname.split("--")

        #If the split resulted in anything other than two strings, the tag is in another format and cannot be compared to other tags
        if len(ltnsplit) != 2:
            cant_compare_list.append(latest_tag)
            continue
        if len(nsplit) != 2:
            cant_compare_list.append(tag)
            continue

        #From here we are working only with the first part of the tag
        #Split it up on dots
        vone = ltnsplit[0].split(".")
        vtwo = nsplit[0].split(".")

        #Then compare each dot-bit of the two tags (latest and the one in the loop)
        for i in range(min(len(vone), len(vtwo))):
            if vone[i] == vtwo[i]: #Same number in thit dot-bit, move on to the next one
                continue
            try:
                if int(vone[i]) > int(vtwo[i]): #If vone is later version than vtwo, dont do anything, vone is already listed as latest
                    break
                else: #If vtwo is later verison, change it so that this one is now listed as latest
                    latest_tag = tag 
                    break
            except ValueError as e: 
                #If there was a ValueError here it is due to the fact that the string cannot be converted to an integer
                #probably because of a version dot-bit like 1a
                cant_compare_list.append(tag)

    #Print the singularity command to the shell script
    if newest_tag == latest_tag: #If the newest tag is the same as the latest version, dont bother with the rest
        if args.verbose:
            print "singularity pull docker://quay.io/biocontainers/{}:{}".format(soft, latest_tag["name"])
        shellscript_file.write("singularity pull docker://quay.io/biocontainers/{}:{}\n".format(soft, latest_tag["name"]))
        containers.append("{}-{}.simg".format(soft, latest_tag["name"]))
    else: 
        #If the latest version and newest version isnt the same, print some alternatives, but still download only the one that was found to be latest
        #The alternatives are:
        #1. The newest tag
        #2. All tags that could not be compared for different reasons
        if args.verbose:
            print "singularity pull docker://quay.io/biocontainers/{}:{}".format(soft, latest_tag["name"])
            print "#Alternative (most recent tag submission):\tsingularity pull docker://quay.io/biocontainers/{}:{}".format(soft, newest_tag["name"])
        shellscript_file.write("singularity pull docker://quay.io/biocontainers/{}:{}\n".format(soft, latest_tag["name"]))
        containers.append("{}-{}.simg".format(soft, latest_tag["name"]))
        
        shellscript_file.write("#Alternative (most recent tag submission):\tsingularity pull docker://quay.io/biocontainers/{}:{}\n".format(soft, newest_tag["name"]))
        for tag in cant_compare_list:
            if args.verbose:
                print "#Alternative (name that was hard to compare):\tsingularity pull docker://quay.io/biocontainers/{}:{}".format(soft, tag["name"])
            shellscript_file.write("#Alternative (name that was hard to compare):\tsingularity pull docker://quay.io/biocontainers/{}:{}\n".format(soft, tag["name"]))

#Finished writing to the shell script, close it before running it
shellscript_file.close()
print "Starting container download..."
#Run the shell script which now contain all the singularity pull calls
subprocess.call(["bash", args.software_list+".sh"], shell=False)

#Print summary information if verbose
if args.verbose:
    #Do some calculations on the container sizes. 
    smallest_container = 2**50
    largest_container = 0
    total_size = 0
    for container in containers:
        statinfo = os.stat(container)
        size = statinfo.st_size/(2**30)
        total_size += size
        if size > largest_container:
            largest_container = size
        if size < smallest_container:
            smallest_container = size

    print "\n\nComplete! Pulled these containers:"
    for i in containers: 
        print i
    print "\nTotal size of all containers {}G, ranging from {}G to {}G".format(round(total_size, 3), round(smallest_container, 3), round(largest_container, 3))
    print "{}s total runtime to download {} containers".format(round(time.time()-t_zero, 2), len(containers))

if software_unavailable:
    print "\n\nWARNING, these tools could not be found:"
    for i in software_unavailable: 
        print i


