#!/usr/bin/env python

import sys, time, os, binascii
from subprocess import call

t_zero = time.time()

tmpfile = "tmp_qacct_{}.txt".format(binascii.b2a_hex(os.urandom(15)))

call(["qacct -o {} -j > /tmp/{}".format(sys.argv[1], tmpfile)], shell=True)

f = open("/tmp/{}".format(tmpfile), "r")

qacct = f.readlines()

summary = [qacct[-3], qacct[-1]]

data = list()

ll = "qname\thostname\tgroup\towner\tproject\tdepartment\tjobname\tjobnumber\ttaskid\taccount\tpriority\tcwd\tsubmit_host\tsubmit_cmd\tqsub_time\tstart_time\tend_time\tgranted_pe\tslots\tfailed\tdeleted_by\texit_status\tru_wallclock\tru_utime\tru_stime\tru_maxrss\tru_ixrss\tru_ismrss\tru_idrss\tru_isrss\tru_minflt\tru_majflt\tru_nswap\tru_inblock\tru_oublock\tru_msgsnd\tru_msgrcv\tru_nsignals\tru_nvcsw\tru_nivcsw\twallclock\tcpu\tmem\tio\tiow\tioops\tmaxvmem\tmaxrss\tmaxpss\tarid\tjc_name"
for line in qacct[:-3]:
    if line == "==============================================================\n":
        data.append(ll.strip())
        ll = ""  
    else:
        ll += "{}\t".format(" ".join(line.split()[1:]).strip())

for i in data:
    print i
#print summary

f.close()


#print round(time.time()-t_zero, 2)
