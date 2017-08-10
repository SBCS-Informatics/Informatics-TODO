#!/bin/bash
filename_ps="/data/SBCS-Informatics/monitoring/`hostname`_monitoring.txt"
date +"%Y_%m_%d_%H-%M" >> $filename_ps
uptime >> $filename_ps
ps aux | awk '{if (($1!="root" && $3$4$10!="0.00.00:00") || ($1=="root" && $3$4!="0.00.0")) print $0}' >> $filename_ps

