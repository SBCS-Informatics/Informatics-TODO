#!/usr/bin/env python
'''
Simple script to run bionano solve assembly 

Change the default paths to point to your files
Run with defaults or specify some parameters
Can only be run on the Univa Grid Engine part of Apocrita

Author: Adrian Larkeryd, 2017
'''

import sys, os, time
import subprocess
import argparse

#Defaults
PATH_TO_REFALIGNER="/data/home/btw977/bionano_solve/REFALIGNER/5678.6119relO/avx/"
PATH_TO_PIPELINECL="/data/home/btw977/bionano_solve/PIPELINE/Pipeline/pipelineCL.py"
PATH_TO_CLUSTERARGS="/data/autoScratch/monthly/btw977/bionano_assembly_test/clusterArguments_APOCRITA.xml"
PATH_TO_OPTARGS="/data/autoScratch/monthly/btw977/bionano_assembly_test/optArgs.xml"

#Date
time_string = time.strftime("%Y_%m_%d",time.localtime())

#The order that the optargs are supposed to be listed, and their defaults
optargs_order = ["FP", "FN", "sd", "sf", "sr"]
optargs_default = ["1.5", "0.15", "0.0", "0.2", "0.03"]

#Command line argument parsing
parser = argparse.ArgumentParser(description="Bionano assembly wrapper for Apocrita, written by Adrian Larkeryd, 2017")
parser.add_argument("input",
        help="the molecule .bnx input file")
parser.add_argument("output",
        help="the full path to the output directory desired")
parser.add_argument("--optargs", metavar=("FP", "FN", "sd", "sf", "sr"),
        help="optArgs in space separated list in order", nargs=5)
parser.add_argument("--optargs_file",
        help="path to the optargs file that is used (and changed if --optargs is specified)", default=PATH_TO_OPTARGS)
parser.add_argument("--refaligner",
        help="path to the refaligner binaries directory", default=PATH_TO_REFALIGNER)
parser.add_argument("--pipelineCL",
        help="path to the pipelineCL.py script", default=PATH_TO_PIPELINECL)
parser.add_argument("--clusterargs",
        help="path to the clusterargs xml", default=PATH_TO_CLUSTERARGS)
parser.add_argument("-v", "--verbose", 
        help="increase output verbosity", action="store_true")
parser.add_argument("--noscreen", 
        help="override the screen requirement", action="store_true")

args = parser.parse_args()

#create a logfile
logfile = open(args.input+"_"+time_string+".log", "w")
logfile.write("---NEW RUN---\n")

#If optargs were supplied, copy and edit the optArgs.xml file
if args.optargs:
    #copy optargs xml file 
    new_optargs_file = "optargs_"+args.input+"_"+time_string+".xml"
    subprocess.call(["cp",args.optargs_file, new_optargs_file], shell=False)
    
    #Set the new filename so that it is used in the run!
    args.optargs_file=new_optargs_file

    #log
    logtmp="cp {} {}".format(args.optargs_file, new_optargs_file)
    logfile.write(logtmp+"\n")
    
    if args.verbose:
        print logtmp
    
    for i in range(5):
        #do some sed stuff to replace the values in the optargs.xml file
        
        #check so that you put in numbers:
        try:
            tmp = float(args.optargs[i])
        except ValueError as e:
            print "ERROR:", e
            exit("ERROR: not a valid float number in optargs " + optargs_order[i])

        #\(.*tab="ASSEMBLE"\) was needed to only change the optargs that have to do with assembly!
        #\1 in the replacement puts the info right back
        default = '"-{}" val0="{}"\(.*tab="ASSEMBLE"\)'.format(optargs_order[i], optargs_default[i])
        replace = '"-{}" val0="{}"\\1'.format(optargs_order[i], args.optargs[i])
        subprocess.call(['sed', '-i', 's/{}/{}/g'.format(default,replace), new_optargs_file], shell=False)
        
        logtmp='sed -i s/{}/{}/g {}'.format(default, replace, new_optargs_file)
        logfile.write(logtmp+"\n")
        if args.verbose:
            print logtmp

command = "/share/apps/iryssolve/utils/drmaapywrapper.sh {} -l {} -a {} -b {} -t {} -C {} -T 32 -j 16".format(args.pipelineCL, args.output, args.optargs_file, args.input, args.refaligner, args.clusterargs)

#run command
if args.verbose:
    print command
try:
    screen_name = os.environ['STY']
    if args.verbose:
        print screen_name
except KeyError:
    if args.noscreen:
        print "OVERRIDING not in a screen"
        logfile.write("OVERRIDING not in a screen\n")
    else:
        logfile.write("Not in a screen session\n")
        exit("Not in a screen session")

logfile.write("RUNNING:\n"+command+"\n")
print command, "\n" 

#RUN
subprocess.call(command.split(), shell=False)
