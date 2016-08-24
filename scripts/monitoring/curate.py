#!/bin/env python
#Author
#Adrian Larkeryd 2016

#importing sys for command line argument handling and glob for file globbing
import sys,glob

#importing groups and "non-human" users, from file groups_and_users.py
from groups_and_users import groups, non_users

def print_usage(ps_file):
    #goes through a `ps aux` log to calculate usage per research group
    all_processes_by_user = dict()
    
    for line in ps_file:
        l_split = line.split()
        if not len(l_split) < 2 and not l_split[0] == 'USER':
            if l_split[0] not in all_processes_by_user.keys():
                all_processes_by_user[l_split[0]] = 0.0
            if float(l_split[2]) > 5.0:
                all_processes_by_user[l_split[0]] += float(l_split[2])
    
    group_totals = dict()
    print "GROUP USAGE:"
    for group_key in groups.keys():
        group_total = 0
        for user in groups[group_key]:
            if user in all_processes_by_user.keys():
                group_total += all_processes_by_user[user]/100.0/60.0
                del all_processes_by_user[user]
        group_totals[group_key] = group_total
        #print group_key, group_total
    
    for group in sorted(group_totals, key=group_totals.get, reverse=True):
        print group, group_totals[group]
    
    print "\nOTHER USERS:"
    #printing the usage of any users which are not assigned to a research group
    for user in sorted(all_processes_by_user, key=all_processes_by_user.get, reverse=True):
        if user not in non_users:
            print user, all_processes_by_user[user]/100.0/60.0

if __name__ == "__main__":
    #this runs only if this script is the main script, ie not if imported. 
    if len(sys.argv) == 2: #open the specified file if there was an argument sent
        print_usage(open(sys.argv[1], "r"))
    elif len(sys.argv) == 1: #look for all files in current directory if no argument
        ps_files = glob.glob("*.txt")
        print "GOING THROUGH:", ps_files
        for ps_file in ps_files:
            print "\n"
            print ps_file
            print_usage(open(ps_file, "r"))
    else:
        exit('usage: curate.py [input_ps_file]\nWith no argument it will grab all .txt files in current directory')

