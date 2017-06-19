#!/usr/bin/env python
"""
#define UT_LINESIZE     32
#define UT_NAMESIZE     32
#define UT_HOSTSIZE     256


/* The structure describing an entry in the database of
   previous logins.  */
struct lastlog
  {
#if __WORDSIZE == 32
    int64_t ll_time;
#else
    __time_t ll_time;
#endif
    char ll_line[UT_LINESIZE];
    char ll_host[UT_HOSTSIZE];
  };


/* The structure describing the status of a terminated process.  This
   type is used in `struct utmp' below.  */
struct exit_status
    short int e_termination;    /* Process termination status.  */
    short int e_exit;           /* Process exit status.  */
  };


/* The structure describing an entry in the user accounting database.  */
struct utmp
{
  short int ut_type;            /* Type of login.  */
  pid_t ut_pid;                 /* Process ID of login process.  */
  char ut_line[UT_LINESIZE];    /* Devicename.  */
  char ut_id[4];                /* Inittab ID.  */
  char ut_user[UT_NAMESIZE];    /* Username.  */
  char ut_host[UT_HOSTSIZE];    /* Hostname for remote login.  */
  struct exit_status ut_exit;   /* Exit status of a process marked
                                   as DEAD_PROCESS.  */
/* The ut_session and ut_tv fields must be the same size when compiled
   32- and 64-bit.  This allows data files and shared memory to be
   shared between 32- and 64-bit applications.  */
#if __WORDSIZE == 32
  int64_t ut_session;           /* Session ID, used for windowing.  */
  struct
  {
    int64_t tv_sec;             /* Seconds.  */
    int64_t tv_usec;            /* Microseconds.  */
  } ut_tv;                      /* Time entry was made.  */
#else
  long int ut_session;          /* Session ID, used for windowing.  */
  struct timeval ut_tv;         /* Time entry was made.  */
#endif

  int32_t ut_addr_v6[4];        /* Internet address of remote host.  */
  char __glibc_reserved[20];            /* Reserved for future use.  */
};
"""

import struct
import sys


from collections import namedtuple

UT_LINESIZE = 32
UT_NAMESIZE = 32
UT_HOSTSIZE = 256
exit_statusStruct = 'h h'

lastlogStruct = 'I {}s {}s'.format(UT_LINESIZE, UT_HOSTSIZE)
lastlogStructSize = struct.calcsize(lastlogStruct)
utmpStruct = 'h I {}s 4s {}s {}s {} iii 4i 20s'.format(UT_LINESIZE, UT_NAMESIZE, UT_HOSTSIZE, exit_statusStruct)
utmpStructSize = struct.calcsize(utmpStruct)

lastlog = namedtuple('lastlog', 'll_time ll_line ll_host')
utmp = namedtuple('utmp', 'ut_type ut_pid ut_line ut_id ut_user ut_host ut_term_status ut_exit_status ut_session tv_sec tv_usec ut_addr_v6_0 ut_addr_v6_1 ut_addr_v6_2 ut_addr_v6_3 ut_glibc_reserved')

def clean_strings(in_list):
    for i, val in enumerate(in_list):
        if type(val) is str:
            in_list[i] = val.rstrip('\0')
    return in_list


def read_utmp(fpath):
    with open(fpath, 'rb') as f:
        rawStruct = f.read(utmpStructSize)
        while  rawStruct != b'':
            unpackedStruct = list(struct.unpack(utmpStruct, rawStruct))
            current_utmp = utmp._make(clean_strings(unpackedStruct))
            print current_utmp
			#b=struct.pack(utmpStruct, *current_utmp)
            rawStruct = f.read(utmpStructSize)

def read_lastlog(fpath):
    with open(fpath, 'rb') as f:
        rawStruct = f.read(lastlogStructSize)
        while  rawStruct != b'':
            unpackedStruct = list(struct.unpack(lastlogStruct, rawStruct))
            current_lastlog = lastlog._make(clean_strings(unpackedStruct))
            print current_lastlog
            rawStruct = f.read(lastlogStructSize)

def read_lastlog_uid(fpath, uid):
    with open(fpath, 'rb') as f:
        f.seek(lastlogStructSize*uid)
        rawStruct = f.read(lastlogStructSize)
        unpackedStruct = list(struct.unpack(lastlogStruct, rawStruct))
        current_lastlog = lastlog._make(clean_strings(unpackedStruct))
        print current_lastlog

def fix_lastlog(fpath, uid, new_lastlog):
    with open(fpath, 'r+b') as f:
        f.seek(lastlogStructSize*uid)
        f.write(struct.pack(lastlogStruct, *new_lastlog))

def writeNewFile(Path, Content):
  with open(Path, 'w+b') as fn:
  	fn.write(Content)

#read_utmp('/var/log/wtmp')
read_utmp('/var/run/utmpx')
read_lastlog_uid('/var/log/lastlog', 1000)
new_lastlog = lastlog(ll_time=1024, ll_line = 'pts/3', ll_host = 'localhost')
#fix_lastlog('/var/log/lastlog', 1000, new_lastlog)
