#! /usr/bin/python
"""
VM-VM-Upload.py - sends team code and data to the confired VM.
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
TEAMNAME = "ENTER YOUR TEAM NAME HERE"  # Change value to reflect your team name
TUC2016TEAMCODE = "ENTER TEAM CODE HERE"  # Change value to the unique code provide to your team
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
def UploadJsonTelstraVM(targetUrl, code, name, cpuID, RAMusage):
    """Uploads data via Json POST to Telstra VM Server"""
    print "[ -- ] Posting data to Telstra VM Server"
    postdata = json.dumps({
                    "TUC2016TEAMCODE": str(code),
                    "TEAMNAME": str(name),
                    "cpuID":str(cpuID),
                    "cpuTEMP":str(RAMusage)
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
# Code to extract and format Device ID information       #
##########################################################
	
def GetVMid():
    """Queries VM eth0 for MAC addr"""
    commandoutput = subprocess.Popen(["/sbin/ip", "link", "show", "eth0"], stdout=subprocess.PIPE)
    commandresult = commandoutput.communicate()[0]
    z = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', commandresult, re.I)
    if z:
        print ' VM ID: ', z.group().replace(':', '')
        return z.group().replace(':', '')
    else:
        print '[FAIL] Unable to get VM ID'
        return 0

def GetRAMusage():
    """Queries VM to get RAM usage stats, returns % of RAM used accurate to 2 decimal places"""
    p1 = subprocess.Popen(["free"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "Mem"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    commandresult =  p2.communicate()[0]
    split = commandresult.split(' ')
    output = str(round(float(split[12])*100/float(split[7]),2))
    return output

	
#############################################
# Main program loop with exception handlers #
#############################################

def main():
  global uploadcounter
  #os.system('clear') #optional
  print '[ -- ] Starting Telstra University Challenge Client 2016'
  cpuID = GetVMid()
  print '[    ] Team Name: ',TEAMNAME
  print '[    ] Team Code: ',TUC2016TEAMCODE
  print '[    ] VM ID: ',cpuID
  print '----------------------------------------'
  try:
    while True:
      RAMusage = GetRAMusage()
      print '[    ] RAM usage:', RAMusage
      if uploadcounter >= UPLOADFREQ:
          try:
            UploadJsonTelstraVM(TelstraVMServerUrl, TUC2016TEAMCODE, TEAMNAME, cpuID, RAMusage)
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
      time.sleep(DELAY) #See Global variables for setting
	  

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

