#!/usr/bin/env python

import sys, time, subprocess

timezero=time.time()

f = open(sys.argv[1], "r")

emails = dict()
files = dict()

for l in f:
    ll = l.split("\t")
    filename = ll[1].strip()
    name = filename.split("/")[3].strip()
    

    if name not in emails.keys():
        try:
            ldap_ps = subprocess.Popen(["ldapinfo_v2", "-uid", name], stdout=subprocess.PIPE)
            email = subprocess.check_output(('grep', 'mail:'), stdin=ldap_ps.stdout)
            ldap_ps.wait()
            emails[name] = email.split()[-1].strip()
            files[name] = [0, []]
        except subprocess.CalledProcessError as e:
            emails[name] = None
            files[name] = [0, []]
    

    size = float(ll[0][0:-1])
    size_order = ll[0][-1]
    if size_order == "G":
        pass
    elif size_order == "T":
        size = size*1000000
    elif size_order == "M":
        size = size/1000
    else:
        size = 0

    files[name][1].append(filename)
    files[name][0]=files[name][0]+size


    #print size, size_order
for user in files.keys():
    print user, files[user][0]

for user in files.keys():
    if files[user][0]< 200:
        pass
    else:
        print user
        for file in files[user][1]:
            print file

print round(time.time()-timezero, 2), "s"
