#!/bin/bash
#Cleaning up the usage ps-logs from sm11, frontend5 and frontend6
#
#Author
#Adrian Larkeryd
#2016

startdate=`head -n1 /data/SBCS-Informatics/monitoring/sm11_monitoring.txt`
enddate=`date +"%Y_%m_%d_%H-%M"`
#naming

mv /data/SBCS-Informatics/monitoring/sm11_monitoring.txt /data/SBCS-Informatics/monitoring/old_logs/sm11_monitoring_${enddate}.txt
mv /data/SBCS-Informatics/monitoring/frontend5.apocrita_monitoring.txt /data/SBCS-Informatics/monitoring/old_logs/frontend5.apocrita_monitoring_${enddate}.txt
mv /data/SBCS-Informatics/monitoring/frontend6_monitoring.txt /data/SBCS-Informatics/monitoring/old_logs/frontend6_monitoring_${enddate}.txt
#move the logs

cd /data/SBCS-Informatics/monitoring/old_logs/

/data/SBCS-Informatics/monitoring/scripts/curate.py > curate_${startdate}_to_${enddate}.log
#curate the logs and store the results in a tiny log file

gzip /data/SBCS-Informatics/monitoring/old_logs/sm11_monitoring_${enddate}.txt
gzip /data/SBCS-Informatics/monitoring/old_logs/frontend5.apocrita_monitoring_${enddate}.txt
gzip /data/SBCS-Informatics/monitoring/old_logs/frontend6_monitoring_${enddate}.txt
#zip up the larger txt logs

echo "Moved logs for sm11, fte5/6 to /data/SBCS-Informatics/monitoring/old_logs/" | mail -s "Interactive node logging" a.larkeryd@qmul.ac.uk
#send email about logging. quite uninformative at the moment. 
