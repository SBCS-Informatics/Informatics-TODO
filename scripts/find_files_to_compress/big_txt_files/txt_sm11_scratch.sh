#!/bin/sh
# Need to run locally on SM11
# i.e. cat __FILE__ | sh
#

echo Running on: `hostname`.
echo "Text files that are larger than 100mb and haven't been touched in 30 days"
echo "---"
find /scratch/ -mtime +30 -size +100M -exec grep -Iq . '{}' \; -exec du -h '{}' \; > $HOME/txt_scratch.log