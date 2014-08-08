############################################################
#Use to record and replay the events
#author = "Venu Dusari"
#version = "0.1"
#email = "venu.dusari@qti.qualcomm.com"
#status = "Testing/UAT"
#reference = "RERAN"
############################################################

# adb shell getevent -tt > recordedEvents.txt
# [   60227.009769] /dev/input/event0: 0003 0039 00000004
# 60227-48470 /dev/input/event0: 0003 0035 00000169

USAGE = """fetching info from getevent input into python script
that replays recorded commands using 'sendevent' and 'sleep'.

USAGE:
        python replay.py input(recordedEvents.txt) 
"""

import os
import re
import sys
import time
import subprocess

class Replay():
    def __init__(self):
        getevent_out,getevent_err = subprocess.Popen('adb shell getevent -p',stdout=subprocess.PIPE).communicate()
        if getevent_out:
            for eachdev in re.compile(r'^add device .*\r?\n(?: .*\r?\n){0,}',re.MULTILINE).findall(getevent_out):
                dev, name = re.match(r'add device \d+: (\S+)(?:.*\r?\n)+?\s+name:\s+"(.*?)"',eachdev).groups()
                has_014a = False
                for _type, _params in re.compile(r'^    (?:....? \(?([\da-f]{4})\)?): (.*\r?\n(?:     .*\r?\n)*)',re.MULTILINE).findall(eachdev):
                    if _type == '0003':# ABS
                        #if hasattr(self, 'touch_dev'): continue
                        d=dict([ (_.groupdict()['type'], _.groupdict()) for _ in re.compile(r'(?P<type>[\da-f]{4})  (?:[: ]+)?value -?\d+, min (?P<min>-?\d+), max (?P<max>-?\d+), fuzz -?\d+,? flat -?\d+(?:, resolution \d+)?[\r\n]+', re.MULTILINE).finditer(_params) ])
                        if '0000' in d and '0001' in d and '002f' in d and has_014a :
                            x,y = d['0000'],d['0001']
                            self.touch_dev = dev
                        elif '0035' in d and '0036' in d and '002f' in d:
                            x,y = d['0035'],d['0036']
                            self.touch_dev = dev
    def sendevent(self,args):
        assert len(args) > 0 and len(args) % 4 == 0
        while args:
            # Chunk to avoid exceeding the maximum command line length (1024):
            # 1024/len('sendevent /dev/input/event0 000 000 000;') == 25
            command = ['adb','shell']
            #cmd = ''.join( [ 'sendevent %s %s %s %s;' % tuple(args[n:n+4]) for n in range(0,min(len(args),100),4) ])
            cmd = ''.join( [ 'sendevent %s %s %s %s;' % tuple(args[n:n+4]) for n in range(0,min(len(args),100),4) ])
            command.append(cmd)
            args=args[100:]
            subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE,close_fds=sys.platform not in [ 'win32', 'cygwin' ],shell=True)

    def replay(self):
        try:
            _re = re.compile(r'[^\d]*(?P<sec>\d+)[.-](?P<msec>\d+)[:\]] (?P<device>[^:]+):'
                ' (?P<class>[0-9a-f]+) (?P<event>[0-9a-f]+) (?P<params>[0-9a-f]+)')
            TIME_FIX = 0.1
            prev_time = None
            input_fn = sys.argv[1]
            if not os.path.exists(os.path.join(os.getcwd(),input_fn)):
                print "Need recordedEvents.txt file in current directory"
                return False
            _device = self.touch_dev
            with open(input_fn, 'rt') as f:
                for eachline in f :
                    m = _re.match(eachline)
                    if m:
                        d = m.groupdict()
                        cur_time = float(d['sec']) + float(d['msec'][:2])/100
                        if prev_time:
                            diff_time = (cur_time - prev_time)
                            if diff_time > 0.2:
                                time.sleep(diff_time - TIME_FIX)
                        prev_time = cur_time
                        self.sendevent([_device,int(d['class'], 16),int(d['event'], 16), int(d['params'], 16)])
        except:
            print "Oops something went wrong :-)"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print USAGE
        sys.exit(1)
    obj = Replay()
    obj.replay()
