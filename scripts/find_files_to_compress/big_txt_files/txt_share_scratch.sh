#!/bin/sh
#$ -N txt_share_scratch
#$ -S /bin/sh
#$ -cwd
#$ -j y
echo Running on: `hostname`.
echo "Text files that are larger than 100mb and haven't been touched in a while"
echo "---"
#$ -l h_rt=120:0:0
#$ -l h_vmem=4G

find /share/scratch-sbcs/ARCHIVE -mtime +730 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > $HOME/txt_share_scratch_archive.log
find /share/scratch-sbcs/YEARLY -mtime +730 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > $HOME/txt_share_scratch_yearly.log
find /share/scratch-sbcs/MONTHLY -mtime +60 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > $HOME/txt_share_scratch_monthly.log
find /share/scratch-sbcs/TEMP -mtime +14 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > $HOME/txt_share_scratch_temp.log
