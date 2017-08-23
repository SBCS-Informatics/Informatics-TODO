#!/usr/bin/env python
'''
Simple script to run bionano solve hybrid scaffold

Author: Adrian Larkeryd, 2017
'''

import sys, os, time
import subprocess
import argparse

#Defaults
PATH_TO_REFALIGNER="/data/home/btw977/bionano_solve/REFALIGNER/5678.6119relO/avx/"

PATH_TO_SINGLE = "/data/home/btw977/bionano_solve/HybridScaffold/03062017/hybridScaffold.pl"
PATH_TO_DUAL = "/data/home/btw977/bionano_solve/HybridScaffold/03062017/runTGH.R"


#Date
time_string = time.strftime("%Y_%m_%d",time.localtime())


#Command line argument parsing
parser = argparse.ArgumentParser(description="Bionano assembly wrapper for Apocrita, written by Adrian Larkeryd, 2017")

parser.add_argument("--sequence",
        help="the NGS fasta or cmap sequence file")

#Create parsing groups to separate options
parser_single = parser.add_argument_group('single_enzyme', 'run a single enzyme hybrid scaffold')
parser_dual = parser.add_argument_group('dual_enzyme', 'run a dual enzyme hybrid scaffold')
parser_single.add_argument("-s", "--single",
        help="run a single enzyme hybrid scaffold", action="store_true")

parser_single.add_argument("-b", "--bionano_cmap",
        help="input BioNano CMAP assembly")
parser_single.add_argument("-o", "--output",
        help="output folder")
parser_single.add_argument("-r", "--refaligner",
        help="path to refaligner program", default=PATH_TO_REFALIGNER)
parser_single.add_argument("-c", "--merge_config",
        help="merge configuration file [REQUIRED]")
parser_single.add_argument("-B", "--confict_filter_B",
        help="conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]")
parser_single.add_argument("-N", "--conflict_filter_N",
        help="conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]")
parser_single.add_argument("-M", "--conflict_file",
        help="Input a conflict resolution file indicating which NGS and BioNano conflicting contigs to be cut [optional]")
'''
Usage: perl hybridScaffold.pl <-h> <-n ngs_file> <-b bng_cmap_file> <-c hybrid_config_xml> <-o output_folder> <-B conflict_filter_level> <-N conflict_filter_level> <-f>
      <-m molecules_bnx> <-p de_novo_pipeline> <-q de_novo_xml> <-v> <-x> <-y> <-e noise_param><-z tar_zip_file><-S>
      -h    : This help message
      -n    : Input NGS FASTA or CMAP file [required]
      -b    : Input BioNano CMAP  [required]
      -c    : Merge configuration file [required]
      -o    : Output folder [required]
      -r    : RefAligner program [required]
      -B    : conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]
      -N    : conflict filter level: 1 no filter, 2 cut contig at conflict, 3 exclude conflicting contig [required if not using -M option]
      -f    : Force output and overwrite any existing files
      -x    : Flag to generate molecules to hybrid scaffold alignment and molecules to genome map alignment [optional]
      -y    : Flag to generate chimeric quality score for the Input BioNano CMAP [optional]
      -m    : Input BioNano molecules BNX [optional; only required for either the -x or -y option]
      -p    : Input de novo assembly pipeline directory [optional; only required for -x option]
      -q    : Input de novo assembly pipeline optArguments XML script [optional; only required for -x option]
      -e    : Input de novo assembly noise parameter .errbin or .err file [optional; recommended for -y option but not required]
      -v    : Print pipeline version information
      -M    : Input a conflict resolution file indicating which NGS and BioNano conflicting contigs to be cut [optional]
      -z    : Name of a zipped file to archive the essential output files [optional]
      -S    : Only run hybridScaffold up to before Merge steps [optional]
      -w    : Name of the status text file needed by IrysView [optional]
      -t    : Perform pre-pairmerge sequence to pre-pairmerge genome map alignment (using align_final parameter) [optional]
      -u    : Sequence of enzyme recognition site (overrides what has been specified in config XML file, for IrysView only) [optional]
'''

parser_dual.add_argument("-d", "--dual",
        help="run a dual enzyme hybrid scaffold", action="store_true")


'''
usage: runTGH.R [--] [--help] [--override] [--install] [--opts OPTS] [--BNGPath1 BNGPATH1] [--BNGPath2 BNGPATH2] [--NGSPath NGSPATH] [--OutputDir OUTPUTDIR] [--RefAlignerPath REFALIGNERPATH] [--RunFlags RUNFLAGS] [--Enzyme1 ENZYME1] [--Enzyme2 ENZYME2] [--ManualCut1 MANUALCUT1] [--ManualCut2 MANUALCUT2] [--tar TAR] [--status STATUS] paramFile

This script performs two-enzyme hybrid scaffolding of BNG genome maps and NGS sequence

positional arguments:
  paramFile			parameter file (xml)

flags:
  -h, --help			show this help message and exit
  -f, --override			Override output folder
  -i, --install			Install/re-install TGH packages

optional arguments:
  -x, --opts OPTS			RDS file containing argument values
  -b1, --BNGPath1 BNGPATH1			Path to BNG maps for enzyme1
  -b2, --BNGPath2 BNGPATH2			Path to BNG maps for enzyme2
  -N, --NGSPath NGSPATH			Path to NGS sequence (fasta file)
  -O, --OutputDir OUTPUTDIR			Output directory [default: ./]
  -R, --RefAlignerPath REFALIGNERPATH			Path to RefAligner
  --RunFlags RUNFLAGS			Specify the stage of scaffold to run/skip
  -e1, --Enzyme1 ENZYME1			Enzyme used in BNG maps specify by --bng1
  -e2, --Enzyme2 ENZYME2			Enzyme used in BNG maps specify by --bng2
  -m1, --ManualCut1 MANUALCUT1			Manual cut file
  -m2, --ManualCut2 MANUALCUT2			Manual cut file
  -t, --tar TAR			Result tar file to be import to IrysView [default: TGH.tar]
  -s, --status STATUS			Path to status file [default: status.txt]
'''
args = parser.parse_args()

print args

if args.single:
    print "SINGLE"
elif args.dual:
    print "DUAL"
else:
    exit("CHOOSE SINGLE OR DUAL")


'''
parser.add_argument("--optargs", metavar=("FP", "FN", "sd", "sf", "sr"),
        help="optArgs in space separated list in order", nargs=5)
parser.add_argument("--optargs_file",
        help="path to the optargs file that is used (and changed if --optargs is specified)", default=PATH_TO_OPTARGS)
parser.add_argument("--reference",
        help="reference .cmap file, for comparison")
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

if args.reference:
    command = "/share/apps/iryssolve/utils/drmaapywrapper.sh {} -l {} -a {} -b {} -t {} -C {} -T -r {} 32 -j 16".format(args.pipelineCL, args.output, args.optargs_file, args.input, args.refaligner, args.clusterargs, args.reference)
else:
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

'''
