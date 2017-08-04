#!/bin/env python
#Author: Adrian Larkeryd, 2017

#importing sys for command line argument handling and glob for file globbing
import sys,glob

#importing groups and "non-human" users, from file groups_and_users.py
from groups_and_users import groups, non_users

infile = open(sys.argv[1], "r")
## do a glob for this later?

time = 0
all_processes_by_user = dict()

group_string=""
for group_key in sorted(groups.keys()):
    group_string += "\t"+group_key

print "time\t"+group_string+"\ttotal"

average=0
average_total=0

for line in infile:
    l_split = line.split()
    
    if len(l_split) == 1:
        if time == 0:
            time = l_split[0]
        else:
            all_groups_total=0
            group_totals = dict()
            for group_key in groups.keys():
                group_total = 0
                for user in groups[group_key]:
                    if user in all_processes_by_user.keys():
                        group_total += all_processes_by_user[user]/100.0/60.0
                        del all_processes_by_user[user]
                group_totals[group_key] = group_total
                all_groups_total += group_total
            
            totals_string=""
    
            if average==60:
                print time+"\t"+str(average_total/60)
                average_total=0
                average=0
            else:
                average+=1
                average_total += all_groups_total

            #for group_key in sorted(groups.keys()):
            #    totals_string += "\t"+str(group_totals[group_key])
            #print time+totals_string+"\t"+str(all_groups_total)
            
            time = l_split[0]

            #delete the data to prepare for next minute segment
            group_totals = dict()
            all_processes_by_user = dict()
    elif not len(l_split) < 2 and not l_split[0] == 'USER' and not line[0] == ' ':
        if l_split[0] not in all_processes_by_user.keys():
            all_processes_by_user[l_split[0]] = 0.0
        if float(l_split[2]) > 5.0:
            all_processes_by_user[l_split[0]] += float(l_split[2])
 
