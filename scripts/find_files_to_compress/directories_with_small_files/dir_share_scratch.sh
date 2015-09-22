#!/bin/sh
#$ -N dir_share_scratch
#$ -S /bin/sh
#$ -cwd
#$ -j y
echo Running on: `hostname`.
echo "Directories that have move than 30 small files (i.e. smaller than 100KB) and haven't been touched in a fortnight"
echo "---"
#$ -l h_rt=120:0:0
#$ -l h_vmem=4G

find /share/scratch-sbcs/ARCHIVE -mtime +730 -type f -size -100k -exec dirname '{}' \; > $HOME/dir_share_scratch_archive.log
cat $HOME/dir_share_scratch_archive.log | uniq -c | sort -r | awk '$1 >= 30 { print;}' > $HOME/dir_share_scratch_archive_sorted.log


find /share/scratch-sbcs/YEARLY -mtime +730 -type f -size -100k -exec dirname '{}' \; > $HOME/dir_share_scratch_yearly.log
cat $HOME/dir_share_scratch_yearly.log | uniq -c | sort -r | awk '$1 >= 30 { print;}' > $HOME/dir_share_scratch_yearly_sorted.log


find /share/scratch-sbcs/MONTHLY -mtime +60 -type f -size -100k -exec dirname '{}' \; > $HOME/dir_share_scratch_monthly.log
cat $HOME/dir_share_scratch_monthly.log | uniq -c | sort -r | awk '$1 >= 30 { print;}' > $HOME/dir_share_scratch_monthly_sorted.log


find /share/scratch-sbcs/TEMP -mtime +14 -type f -size -100k -exec dirname '{}' \; > $HOME/dir_share_scratch_temp.log
cat $HOME/dir_share_scratch_temp.log | uniq -c | sort -r | awk '$1 >= 30 { print;}' > $HOME/dir_share_scratch_temp_sorted.log
