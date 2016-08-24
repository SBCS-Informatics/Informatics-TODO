#!/bin/sh
#$ -N txt_omics_scratch
#$ -S /bin/sh
#$ -cwd
#$ -j y
#$ -l h_rt=120:0:0
#$ -l h_vmem=4G

# Can be queued on the cluster instead of ran on an interactive node as it is looking at GPFS share. 

echo "Running on: `hostname`."
echo "Text files that are larger than 100mb and haven't been touched in a while"
echo "---"
find /data/omicsScratch -mtime +30 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > /data/SBCS-Informatics/monitoring/cleanup_survey/large_nonbinary_omicsScratch_`date +"%m_%d_%Y_%H-%M"`.log
