#! /usr/bin/python
"""
Upload-DataTo-VM.py - sends team code and data to the confired VM.
Using the Telstra provided VM server URL this script will post your team name and team code 
so you can be plotted on the Telstra challenge Map and leaderboard.

Before running the script please change the global variables.

This script is provided as an example building block only to show what can be done 
and to give teams a basic agent to connect to the Telstra VM. 
Please feel free to change, modify, rebuild or completely redesign components as 
specifically suits your teams chosen objective.

If your team finds bugs in this baseline script or identifies better ways to 
implement the baseline code that is not specific to your solution, then please submit 
modifications via github. Teams will be recognised for their contributions in 
improving the baseline code.

Note: While we have provided this python script, teams do not have to use it in their solution.
"""

import os
import time
import subprocess
import urllib2
import re
import json
import traceback
import sys


#####################
# Global Constants  #
#####################
TEAMNAME = "Enter Team Name Here"  # Change value to reflect your team name
TUC2016TEAMCODE = "Enter Team Code Here"  # Change value to the unique code provide to your team
TelstraVMServerUrl = "http://XXX.XXX.XXX.XXX/api/position"  # Target M2M server for JSON upload
DELAY = 10 # Seconds. Delay between measurments.
UPLOADFREQ = 6 #Sets upload rate = (DELAY*UPLOADFREQ) for JSON post.

####################
# Global Variables #
####################
uploadcounter = UPLOADFREQ


######################################################
# Code to handle uploading collected data to servers #
######################################################
def UploadJsonTelstraVM(targetUrl, code, name, cpuID, cpuTEMP):
    """Uploads data via Json POST to Telstra VM Server"""
    print "[ -- ] Posting data to Telstra VM Server"
    postdata = json.dumps({
                    "TUC2016TEAMCODE": str(code),
                    "TEAMNAME": str(name),
                    "cpuID":str(cpuID),
                    "cpuTEMP":str(cpuTEMP)
    })
    headers = {"Content-Type": "application/json"}
    print "     URL: ", targetUrl
    print "     Headers: ", headers
    print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ OK ] Upload Sucessful"
    else:
        print "[FAIL] Upload HTTP Error", UploadResult
    return UploadResult


##########################################################
# Code to extract and format CPU ID information from Pi  #
##########################################################
	
def GetCPUid():
    """Queries Raspberry Pi for its unique CPU ID"""
    commandoutput = subprocess.Popen(["/bin/cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)
    commandresult = commandoutput.communicate()[0]
    z =  re.search('Serial\s+\:\s+(.*)$', commandresult, re.MULTILINE)
    if z:
        #print ' CPU ID: ', z.group(1)
        return z.group(1)
    else:
        print '[FAIL] Unable to get CPU ID'
        return 0

def GetCPUtemp():
    """Queries Raspberry Pi for its unique CPU ID"""
    commandoutput = subprocess.Popen(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE)
    commandresult = commandoutput.communicate()[0]
    z =  re.search('temp=([\.\d]+)', commandresult, re.MULTILINE)
    if z:
        #print ' CPU Temp: ', z.group(1)
        return z.group(1)
    else:
        print '[FAIL] Unable to get CPU ID'
        return 0


#############################################
# Main program loop with exception handlers #
#############################################

def main():
  global uploadcounter
  #os.system('clear') #optional
  print '[ -- ] Starting Telstra University Challenge Client 2016'
  cpuID = GetCPUid()
  print '[    ] Team Name: ',TEAMNAME
  print '[    ] Team Code: ',TUC2016TEAMCODE
  print '[    ] Raspberry Pi ID: ',cpuID
  print '----------------------------------------'
  try:
    while True:
      cpuTEMP = GetCPUtemp()
      print '[    ] CPU Temp:', cpuTEMP
      if uploadcounter >= UPLOADFREQ:
          try:
            UploadJsonTelstraVM(TelstraVMServerUrl, TUC2016TEAMCODE, TEAMNAME, cpuID, cpuTEMP)
          except urllib2.HTTPError as e:
            # Capture HTTPError errors
            print " "
            print "******************************"
            print "Exception detected (HTTPError)"
            print "Code:", e.code
            print "Reason:", e.reason
            print "******************************"
            pass
          except urllib2.URLError as e:
            # Capture URLError errors
            print " "
            print "*****************************"
            print "Exception detected (URLError)"
            print "Reason:", e.reason
            print "*****************************"
            print "[ -- ] Check Raspberry Pi and modem have assigned IP addresses"
            pass
          uploadcounter = 1
      else:
          uploadcounter = uploadcounter + 1
      time.sleep(DELAY) #See Global Constants for setting
  except OSError as e:
    # Capture OS command line errors
    print " "
    print "****************************"
    print "Exception detected (OSError)"
    print "****************************"
    print e.errno
    print e.filename
    print e.strerror
    traceback.print_exc(file=sys.stdout)
    print "****************************"
    print "Done.\nExiting."
    sys.exit()
  except Exception as e:
    print " "
    print "******************"
    print "Exception detected"
    print "******************"
    print type(e)
    print e
    traceback.print_exc(file=sys.stdout)
    print "******************"
    print "Done.\nExiting."
    sys.exit()
  except KeyboardInterrupt:
    print " "
    print "******************************"
    print "Exception (Keyboard Interrupt)"
    print "******************************"
    print "Done.\nExiting."
    sys.exit()
  except:
    print " "
    print "*******************"
    print "Exception (Unknown)"
    print "*******************"
    traceback.print_exc(file=sys.stdout)
    print "*******************"
    print "Killing Thread..."
    print "Done.\nExiting."
    sys.exit()

if __name__ == "__main__":
    main()

