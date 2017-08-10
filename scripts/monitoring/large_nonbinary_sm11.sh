#!/bin/sh
# Needs to run locally on SM11
# as it is looking at a local disk

echo "sm11 local scratch disk survey."
echo "Listing text files that are larger than 100MB and haven't been touched in 30 days:"
echo "---"
find /scratch/ -mtime +30 -size +100M -exec du -h '{}' \; > /data/SBCS-Informatics/monitoring/cleanup_survey/large_nonbinary_sm11_`date +"%Y_%m_%d_%H-%M"`.log
