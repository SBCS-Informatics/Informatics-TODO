#!/usr/bin/env python
# Script to load latest versions of listed software tools
# by way of module load.
#
# Author: Adrian Larkeryd, 2016
#
# List of softwares:

import sys, time, os
import subprocess

list_of_softwares = [
        "bowtie2", 
        "bwa", 
        "hmmer",
        "samtools",
        "bamtools", 
        "bedtools",
        "blast+",
        "htop",
        "parallel",
        "bcftools",
        "SOAP",
        "bowtie",
        "mrbayes",
        "velvet",
        "R",
        "muscle", 
        "clustal",
        "RAxML"
        ] 

dict_of_versions = dict()

os.system("modulecmd bash avail -l 2> /data/SBCS-Informatics/test/moduleloadtest")

f=open("/data/SBCS-Informatics/test/moduleloadtest", "r")

for line in f.readlines():
    line_split = line.split()
    if len(line_split)>1:
        module_entry = line_split[0].split("/", 1)
        software_name = module_entry[0]
        if software_name in list_of_softwares:
            if software_name in dict_of_versions:
                dict_of_versions[software_name].append(module_entry[1])
            else:
                dict_of_versions[software_name] = [module_entry[1]]


for software in dict_of_versions.keys():
    if len(dict_of_versions)>1:
        latest = dict_of_versions[software][0]
        for version in dict_of_versions[software]:
            if version > latest:
                latest = version
        print "module load %s/%s"%(software, latest)
        #os.system("modulecmd bash load %s/%s"%(software, latest))
        #result = subprocess.check_output("modulecmd bash load %s/%s"%(software, latest), stderr=subprocess.STDOUT, shell=True)
        #print result
    else:
        print "module load %s/%s"%(software, dict_of_versions[software])
        #os.system("modulecmd bash load %s/%s"%(software, dict_of_versions[software]))
        #result = subprocess.check_output("modulecmd bash load %s/%s"%(software, dict_of_versions[software]), stderr=subprocess.STDOUT, shell=True)
        #print result
    del list_of_softwares[list_of_softwares.index(software)]

if len(list_of_softwares) != 0:
    print "leftovers", list_of_softwares
