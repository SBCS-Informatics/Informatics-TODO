#!/bin/sh
#$ -N dir_omics_scratch
#$ -S /bin/sh
#$ -cwd
#$ -j y
echo Running on: `hostname`.
echo "Directories that have move than 30 small files (i.e. smaller than 100KB) and haven't been touched in a fortnight"
echo "---"
#$ -l h_rt=120:0:0
#$ -l h_vmem=4G

find /data/omicsScratch -mtime +14 -type f -size -100k -exec dirname '{}' \; > $HOME/dir_omics_scratch.log
cat $HOME/dir_omics_scratch.log | uniq -c | sort -r | awk '$1 >= 30 { print;}' > $HOME/dir_omics_scratch_sorted.log
