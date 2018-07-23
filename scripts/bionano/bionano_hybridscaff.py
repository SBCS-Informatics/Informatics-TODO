#!/usr/bin/env python
'''
Simple script to run bionano solve hybrid scaffold

Author: Adrian Larkeryd, 2017
'''

import sys, os, time
import subprocess
import argparse
import re

#Defaults
PATH_TO_REFALIGNER="/data/home/btw977/bionano_solve/RefAligner/6700.6902rel/sse/RefAligner"
CONFIG_FILE="/data/home/btw977/bionano_configs/TGH_config_apoc.xml"

PATH_TO_SINGLE = "/data/home/btw977/bionano_solve/HybridScaffold/08212017/hybridScaffold.pl"
PATH_TO_DUAL = "/data/home/btw977/bionano_solve/HybridScaffold/08212017/runTGH.R"

#Date
time_string = time.strftime("%Y_%m_%d",time.localtime())

#Command line argument parsing
parser = argparse.ArgumentParser(description="Bionano assembly wrapper for Apocrita, written by Adrian Larkeryd, 2017")

parser.add_argument("-n", "--sequence",
        help="the NGS fasta or cmap sequence file")
parser.add_argument("-o", "--output",
        help="output folder")
parser.add_argument("-r", "--refaligner",
        help="path to refaligner program", default=PATH_TO_REFALIGNER)
parser.add_argument("-v", "--verbose", 
        help="verbose output", action="store_true")
parser.add_argument("--qsub", 
        help="submit job to the queue", action="store_true")
parser.add_argument("-t", "--threads",
        help="Maximum number of threads to use in computations [32]", default="32")
parser.add_argument("--additional_args", 
        help="any additional arguments you want to send to the pipeline, please put these in quotes", default="")

#Create parsing groups to separate options
parser_single = parser.add_argument_group('Single enzyme', 'Run a single enzyme hybrid scaffold')
parser_dual = parser.add_argument_group('Dual enzyme', 'Run a dual enzyme hybrid scaffold')

##single enzyme arugments
parser_single.add_argument("-s", "--single",
        help="run a single enzyme hybrid scaffold", action="store_true")
parser_single.add_argument("-b", "--bionano_cmap",
        help="input BioNano CMAP assembly")
parser_single.add_argument("-c", "--merge_config",
        help="merge configuration file [REQUIRED]")
parser_single.add_argument("-B", "--conflict_filter_B",
        help="conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]")
parser_single.add_argument("-N", "--conflict_filter_N",
        help="conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]")
parser_single.add_argument("-M", "--conflict_file",
        help="Input a conflict resolution file indicating which NGS and BioNano conflicting contigs to be cut [optional]")

##dual enzyme arguments
parser_dual.add_argument("-d", "--dual",
        help="run a dual enzyme hybrid scaffold", action="store_true")
parser_dual.add_argument("-e1", "--enzyme_1",
        help="enzyme 1. Avalible enzymes: BspQI, BbvCI, BsmI, BsrDI, BssSI.")
parser_dual.add_argument("-e2", "--enzyme_2",
        help="enzyme 2. Avalible enzymes: BspQI, BbvCI, BsmI, BsrDI, BssSI.")
parser_dual.add_argument("-b1", "--bionano_cmap_1",
        help="input BioNano CMAP assembly for enzyme 1")
parser_dual.add_argument("-b2", "--bionano_cmap_2",
        help="input BioNano CMAP assembly for enzyme 2")
parser_dual.add_argument("--config_file",
        help="configuration file, default: "+CONFIG_FILE, default=CONFIG_FILE)

args = parser.parse_args()

print args

if args.sequence and args.output and args.refaligner:
    logfile = open("./"+args.sequence.split("/")[-1]+"_"+time_string+".log", "w")
else:
    exit("sequence and output needed")

if args.single:
    if not (args.bionano_cmap and args.merge_config and ((args.conflict_filter_B and args.conflict_filter_N) or args.conflict_file)):
        exit("You did a boo boo, specify all the arguments needed please")
    logfile.write("Single run\n")
    if args.verbose:
        print "Single enzyme run"
    #copy xml file 
    new_config_file = "/".join(args.sequence.split("/")[:-1])+"/"+args.sequence.split("/")[-1]+"_hybrid_scaffold_config_"+time_string+".xml"
    subprocess.call(["cp", args.merge_config, new_config_file], shell=False)
    args.merge_config=new_config_file
    
    if args.verbose:
        print ['sed', '-i', 's/{}/{}/g'.format('flag attr="maxthreads" val0="32"','flag attr="maxthreads" val0="'+args.threads+'"'), args.merge_config]
    subprocess.call(['sed', '-i', 's/{}/{}/g'.format('flag attr="maxthreads" val0="32"','flag attr="maxthreads" val0="'+args.threads+'"'), args.merge_config], shell=False)
    
    if args.conflict_file:
        conflict_command = "-M {}".format(args.conflict_file)
    elif args.conflict_filter_B and args.conflict_filter_N:
        conflict_command = "-B {} -N {}".format(args.conflict_filter_B, args.conflict_filter_N)

    command = "perl {} -n {} -b {} -c {} -r {} -o {} {} {}".format(PATH_TO_SINGLE, args.sequence, args.bionano_cmap, args.merge_config, args.refaligner, args.output, args.additional_args, conflict_command)
    
    if args.qsub: 
        qsub_file_name = "./"+args.sequence.split("/")[-1]+"_"+time_string+".sh"
        qsub_file = open(qsub_file_name, "w")
        qsub_file.write(command)
        command = "qsub -pe smp "+args.threads+" -l h_rt=24:00:00 -l h_vmem="+str(128/int(args.threads)+1)+"G " + qsub_file_name
        print "TO SUBMIT TO THE QUEUE COPY AND PASTE THIS INTO THE COMMAND LINE:"
        print command
    else:
        subprocess.call(command.split(), shell=False)
    logfile.write(command+"\n")
    
    if args.verbose:
        print "Final command"
        print command

elif args.dual:
    if not (args.bionano_cmap_1 and args.bionano_cmap_2 and args.sequence and args.output and args.refaligner and args.enzyme_1 and args.enzyme_2):
        exit("You need to specify all arguments")
    if args.verbose:
        print "Dual enzyme run"
    logfile.write("Dual run\n")
    
    #copy xml file 
    new_config_file = "TGH_config_"+args.sequence.split("/")[-1]+"_"+time_string+".xml"
    subprocess.call(["cp", args.config_file, new_config_file], shell=False)
    
    #log
    logtmp="cp {} {}".format(args.config_file, new_config_file)
    logfile.write(logtmp+"\n")
    if args.verbose:
        print logtmp

    #Set the new filename so that it is used in the run!
    args.config_file=new_config_file
    
    default_list = ["NGSPATH_CHANGE", "BNGPATH1_CHANGE", "BNGPATH2_CHANGE", "OUTPUT_CHANGE", "REFALIGNER_CHANGE", "ENZYME1_CHANGE", "ENYZME2_CHANGE", 'flag attr="maxthreads" val0="32"']
    replace_list = [args.sequence, args.bionano_cmap_1, args.bionano_cmap_2, args.output, args.refaligner, args.enzyme_1, args.enzyme_2, 'flag attr="maxthreads" val0="'+args.threads+'"']
    for i in range(0,len(default_list)):
        default = '{}'.format(default_list[i])
        replace = '{}'.format(re.escape(replace_list[i]))
        subprocess.call(['sed', '-i', 's/{}/{}/g'.format(default,replace), args.config_file], shell=False)
        logtmp='sed -i s/{}/{}/g {}'.format(default, replace, args.config_file)
        logfile.write(logtmp+"\n")
        if args.verbose:
            print logtmp


    command = "Rscript {} -f {} {}".format(PATH_TO_DUAL, args.config_file, args.additional_args)
    subprocess.call(command.split(), shell=False)
    logfile.write(command+"\n")
    if args.verbose:
        print command
else:
    logfile.write("Choose single or dual run")
    print "Choose single or dual run"

logfile.close()


