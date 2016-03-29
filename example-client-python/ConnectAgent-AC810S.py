
#!/usr/bin/python
"""
ConnectAgent-AC801S.py - this program checks wireless modem cellular network 
connectivity and the selected Raspberry Pi interface and connects if disconnected. 
If a non-selected interface has an IP then program provides a warning about multiple IP interfaces 
on Raspberry Pi but continues to connect Raspberry Pi on the selected interface (eth1/wlan0). The program stores 
the modem cellular network IP address. This information can be used to message 
that IP address to a file if required.

By default the client script is using the (telstra.extranet) APN to connect to
the cellular network, this will mean that a publicly addressable IP is assigned 
to the modem. While the IP is public the IP address is not statically assigned 
and can change between reconnection's. Teams may also wish to use the 
(telstra.internet) APN which assigns a private IP and is thus more secure.

While the modem can be assigned a public IP the Raspberry Pi eth1 and wlan0 interfaces 
are assigned a local IP address from the modem. The eth1 intreface using the USB cable 
always gets a defualt 192.168.1.4 address where as the wlan0 IP address can vary. 
If you wish the Raspberry Pi to be reached from the internet you will need to 
log into the modem config web page (192.168.1.1) and configure port forward 
settings and if using wlan0 also a local static IP linked to the Raspbery pi MAC.

This script is provided as an example building block only to show what can be 
done and to give teams a basic connection script to work from. Please feel 
free to change, modify, rebuild or completely redesign components as 
specifically suits your teams chosen objective.

If your team finds bugs in this baseline script or identifies better ways to
implement the baseline code that is not specific to your solution, then please 
submit modifications via github. Teams will be recognised for their 
contributions in improving the baseline code.

"""

import random
import re
import subprocess
import sys
import time
import traceback
import urllib2
import lockfile
from cookielib import CookieJar


####################
# Global Constants #
####################
APN = 'telstra.extranet'  #Vaild settings are 'telstra.extranet' for pubic IP or 'telstra.internet' for private IP.
AC810_Interface = 'eth1'  #Select eth1 (if using USB cable) or wlan0 (if using WiFi dongle)
DHCP_Release = 'sudo dhclient -r '+AC810_Interface
DHCP_Renew = 'sudo dhclient -nw '+AC810_Interface
readIP = 'sudo ifconfig '+AC810_Interface
backoff = 10            # Sets the starting backoff time for attempting to reconnect (seconds)


####################
# Global Variables #
####################
backofftimer = backoff  # backofftimer is doubled every time the connection fails. See connectbackoff()
backoffStart = 0
token = ["00000000","xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]


##########################################################
# Code to manage connection and communication with modem #
##########################################################
def InterfaceCheck(interface):
    """
    Checks if the passed network interfaces has a IP address.
    Prints a warning if a IP address is detected as this could mean the 
    Raspberry Pi has multiple IP address if eth1 interface is activated.
    And lead to IP routing issues without correct configuration.
    """
    time.sleep(2)
    command = 'sudo ifconfig ' + interface
    commandresult, commanderror = SendOS(command)
    if commandresult:
        IP = re.search('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', commandresult)
        if IP:
            IPdefault = re.search('169.254.(?:[\d]{1,3})\.(?:[\d]{1,3})', IP.group(0))
            if IP.group(0) == "0.0.0.0" or IP.group(0) == "127.0.0.1" or IPdefault:
                print "[ OK ] Only default IP address on", interface
                result = None
            else:
                print "[ !! ] WARNING: Detected IP address", IP.group(0), "on", interface
                print "       If Raspberry "+AC810_Interface+" IP also activated this can cause routing issues"
                print "       Recommend only activating one IP interface or set routing table to handle multiple interfaces"
                result = IP.group(0)
        else:
            print "[ OK ] No IP address on", interface
            result = None
    else:
        if commanderror:
            print "[ OK ] No", interface, "interface detected"
        else:
            print "[FAIL] Error: Undefined response to ifconfig", interface, "command"
        result = None
    return result


def ModemDetect():
    """Checks if AC810  modem is plugged into USB port and detected on eth1 by RaspberryPi"""
    #print "[ -- ] Checking AC810S Modem Present"
    command = 'sudo ifconfig '+AC810_Interface
    commandresult, commanderror = SendOS(command)
    modeminterface = re.search(AC810_Interface, commandresult) # If modem available and detected there should be a interface created
    if modeminterface and not commanderror:
        print "[ OK ] "+AC810_Interface+" interface detected, communication with AC810 Modem enabled"
        result = True  # interface detected so assume modem is plugged in and correctly configured
    else:
        print "[FAIL] "+AC810_Interface+" interface is NOT detected, communication with AC810 Modem NOT possible"
        result = False
    return result


def SendOS(OScom):
    """Sends commands to Raspberry OS and returns output. """
    commandoutput = subprocess.Popen([OScom], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    commandresult, commanderror = commandoutput.communicate()
    return commandresult, commanderror


############################################
# Code to manage wireless connection state #
############################################
def RaspberryIPcheck():
    """
    Checks if IP address assigned on selected interface of Raspberry Pi
    """
    #SendOS(DHCP_Release)
    #time.sleep(2)
    SendOS(DHCP_Renew)
    time.sleep(10)
    commandresult, commanderror = SendOS(readIP)
    wwanip = re.search('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', commandresult)
    if wwanip and not commanderror:
        IPdefault = re.search('169.254.(?:[\d]{1,3})\.(?:[\d]{1,3})', wwanip.group(0))
        if wwanip.group(0) == "0.0.0.0" or wwanip.group(0) == "127.0.0.1" or IPdefault:
            print "[FAIL] Only dummy IP address on", AC810_Interface
            result = None
        else:
            print "[ OK ] RaspberryPi "+AC810_Interface+" connected with IP address", wwanip.group(0)
            result = wwanip.group(0)
    else:
        print "[FAIL] RaspberryPi unable to get "+AC810_Interface+" IP address"
        result = None
    return result


def ModemIPcheck():
    """
    Checks if IP address assigned on the wireless modem from cellular network
    """
    zeroIP = "0.0.0.0"
    targetUrl = 'http://192.168.1.1/index.html#settings/network/status'
    #postdata = "token=" + token[1] + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
    postdata = " "
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'GET'
    webresponse = urllib2.urlopen(req)
    modemwebpage = webresponse.read()
    #print modemwebpage
    modemip = re.search('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', modemwebpage)
    if modemip:
        if modemip.group(0) != zeroIP:
            print "[ OK ] AC810 Modem connected to cellular network with IP address", modemip.group(0)
            result = modemip.group(0)
        else:
            print "[ -- ] AC810 Modem has no IP address from cellular network"
            result = None
    else:
        print "[ -- ] AC810 Modem has has no IP address from cellular network"
        result = None
    return result


def ModemIPchange(modemip):
    """
    Checks if modem IP has changed from the last acquired modem IP
    Saves current IP in file .current_ip for later reference
    """
    print "[ -- ] Checking if AC810 Modem IP Changed"
    lastIP = subprocess.Popen("cat  ~/.current_ip", shell=True, stdout=subprocess.PIPE)
    lastIP = lastIP.communicate()[0]
    if lastIP:
        lastIPclean = re.search('(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', lastIP)
        if lastIPclean:
            if modemip != lastIPclean.group(0):
                print "[ -- ] New AC810 Modem IP address detected", modemip, "was", lastIPclean.group(0)
                iplist = "echo \"" + modemip + "\" >|~/.current_ip"
                # Save IP address in file .current_ip
                SendOS(iplist)
                IPchangeAlert(modemip)
            else:
                print "[ -- ] AC810 Modem IP address same as last acquired address", modemip
        else:
            # File .current_ip was empty
            print "[ -- ] New IP address", modemip
            iplist = "echo \"" + modemip + "\" >|~/.current_ip"
            # Save IP address in file .current_ip
            SendOS(iplist)
            IPchangeAlert(modemip)
    else:
        # File .current_ip did not exist
        print "[ -- ] New eth1 IP address", modemip
        iplist = "echo \"" + modemip + "\" >|~/.current_ip"
        # Save IP address in file .current_ip
        SendOS(iplist)
        IPchangeAlert(modemip)
        

def IPchangeAlert(modemip):
    """
    Send an alert to inform remote user that the external modem IP address has changed
    This is recommended if external remote ssh access to the pi is required using telstra.extranet APN
    """
    # Place code here if you want device to do something in response to IP change. 
    # Example send email or update Dynamic DNS service.


def privateIP(currentIP):
    """
    Checks if current IP is in the private IP range or the public IP range
    Returns True if in private IP range or False if in public IP range
    """
    #Match against private IP ranges
    if re.search('10\.(?:[\d]{1,3})\.(?:[\d]{1,3})\.(?:[\d]{1,3})', currentIP):
        print "[ -- ] Private IP using 10.x.x.x range"
        result = True
    elif re.search('192\.168\.(?:[\d]{1,3})\.(?:[\d]{1,3})', currentIP):
        print "[ -- ] Private IP using 192.168.x.x range"
        result = True
    elif re.search('172\.(?:1[6-9]|2[0-9]|3[0-1])\.(?:[\d]{1,3})\.(?:[\d]{1,3})', currentIP):     
        print "[ -- ] Private IP using 172.16.x.x to 172.31.x.x range"
        result = True
    else:
        print "[ -- ] Public IP range"
        result = False
    return result


def correctIP(currentIP):
    """
    Checks if current IP matches set APN's IP range
    telstra.extranet APN is always public
    telstra.internet APN is always private
    Other APNs (eg telstra.m2m) are ignored by returning True
    """
    privateIPset = privateIP(currentIP)
    if privateIPset and APN == 'telstra.extranet':
        result = False
    elif not privateIPset and APN == 'telstra.internet':
        result = False
    else:
        result = True
    return result


def connectbackoff():
    """
    If failure to connect on wireless this method sets a growing backoff 
    period before attempting again
    """
    global backofftimer

    timepassed = time.time() - backoffStart
    if timepassed > backofftimer:
        #print "[ -- ] Backoff timer has expired so ok to try to connect"
        backofftimer = backofftimer + backofftimer + random.random()  # Increase time before trying again
        if (backofftimer > 1800): # Set max backoff timer at 30 minutes
            backofftimer = 1800 + random.randint(0, 300) # Backoff 30 minutes plus 0 to 5 minute random window
        return True
    else:
        #print "[ -- ] Backoff timer has not expired so cannot try to connect yet"
        timeremain = backofftimer - timepassed
        timeremain = round(timeremain, 1)
        print "[ -- ] System can attempt reconnect to cellular netowrk in", timeremain, "seconds"
        return False


def ModemLogin():
    """Login to AC785 webpage"""
    global token
    targetUrl = "http://192.168.1.1/index.html"
    #print "[ -- ] Getting session cookie from AC810 webpage"
    req = urllib2.Request(targetUrl)
    req.get_method = lambda: 'GET'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ OK ] AC810 Webpage Opened"
        modemwebpage = response.read()
        #print modemwebpage
        # sessionId=00000000%2DyfHPjwmGkJLC3vghDRzbePeD0mhH9rA
        sessioncookie = re.search('sessionId=(?:[\d]{1,8})\%2D(?:[\w]{1,31})', modemwebpage)
        if sessioncookie:
            token = sessioncookie.group(0).split('%2D')
            print "[ -- ] Session Cookie: ", sessioncookie.group(0)
            time.sleep(2)
            targetUrl = "http://192.168.1.1/Forms/config"
            #print "[ -- ] Logging into AC810 Admin Webpage"
            postdata = "token=" + token[1] + "&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password=admin"
            headers = {"Cookie": token[0] + "-" + token[1]}
            #print "     URL: ", targetUrl
            #print "     Headers: ", headers
            #print "     Body: ", postdata
            req = urllib2.Request(targetUrl, postdata, headers)
            req.get_method = lambda: 'POST'
            response = urllib2.urlopen(req)
            UploadResult = response.getcode()
            if UploadResult == 200:
                print "[ OK ] AC810 Admin Webpage Login Sucessful"
            else:
                print "[FAIL] AC810 Admin Webpage Login Error", UploadResult
            #print response.read()
        else:
            print "[FAIL] No session cookie detected. Unable to login to AC810 Admin Webpage"
            sessioncookie = None
            token = None
            UploadResult = 0
    else:
        print "[FAIL] AC810 Webpage Load Error", UploadResult
    time.sleep(2)
    return UploadResult


def ModemPdpDisconnect():
    """Disconnect AC810 from celluar network"""
    targetUrl = "http://192.168.1.1/Forms/config"
    print "[ -- ] Running PDP Disonnection Commands"
    postdata = "wwan.connect=Disconnect&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ -- ] PDP Disconnect Request Sent"
    else:
        print "[FAIL] PDP Disconnect Error", UploadResult
    #print response.read()
    time.sleep(2)
    return UploadResult


def ModemPdpConnect():
    """Connect AC810 to cellular network"""
    targetUrl = "http://192.168.1.1/Forms/config"
    print "[ -- ] Running PDP Connection Commands"
    postdata = "wwan.connect=DefaultProfile&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ -- ] PDP Connect Request Sent"
    else:
        print "[FAIL] PDP Connect Error", UploadResult
    #print response.read()
    time.sleep(10)
    return UploadResult


def ModemDeleateProfile(id):
    """Deleate AC810S APN"""
    #print "[ -- ] Deleting APN Profile", str(id)
    targetUrl = 'http://192.168.1.1/Forms/profile'
    #profile.id=1&action=delete&err_redirect=/error.json&ok_redirect=/success.json&token=anyfLUyviCSSrTovug29PkZJKLDMdpr
    postdata = "profile.id=" + str(id) + "&action=delete&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ -- ] ."
    else:
        print "[FAIL] Unable to Delete APN Profile", str(id)
    #print response.read()
    time.sleep(2)
    return UploadResult


def ModemPdpSetAPN(id):
    """Set AC810 APN Profile"""
    # Clear any existing Profile settings
    print "[ -- ] Deleting Existing APN Profiles"
    for x in range(1, 5):
        ModemDeleateProfile(x)
    ModemDeleateProfile(id)
    print "[ -- ] Setting AC810 Modem APN to", APN
    targetUrl = 'http://192.168.1.1/Forms/profile'
    #postdata = "action=update&profile.index=" + str(id) + "&profile.id=" + str(id) + "&profile.name=UniChallenge&profile.apn=" + APN + "&profile.username=&profile.password=&profile.authtype=None&profile.type=IPV4&profile.pdproamingtype=None&profile.ipaddr=0.0.0.0&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    postdata = "action=create&profile.name=internet&profile.apn=" + APN + "&profile.authtype=None&profile.username=&profile.password=&profile.type=IPV4&profile.pdproamingtype=None&profile.ipaddr=0.0.0.0&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ -- ] Set APN", str(id)
        #ModemDefaultProfile(id + 1) #+1 offset due to webpage having default telstra.internet profile that can not be deleted
        ModemDefaultProfile(id)
    else:
        print "[FAIL] Unable to set APN", str(id)
    #print response.read()
    time.sleep(2)
    return UploadResult


def ModemDefaultProfile(id):
    """Set AC810 defulat APN"""
    print "[ -- ] Setting AC810 Modem Default Profile to", str(id)
    targetUrl = 'http://192.168.1.1/Forms/config'
    postdata = "wwan.profile.default=" + str(id) + "&wwan.profile.defaultLTE=" + str(id) + "&err_redirect=/error.json&ok_redirect=/success.json&token=" + token[1]
    headers = {"Cookie": token[0] + "-" + token[1]}
    #print "     URL: ", targetUrl
    #print "     Headers: ", headers
    #print "     Body: ", postdata
    req = urllib2.Request(targetUrl, postdata, headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    UploadResult = response.getcode()
    if UploadResult == 200:
        print "[ -- ] Set Defualt to Profile", str(id)
    else:
        print "[FAIL] Unable to set default to profile", str(id)
    #print response.read()
    time.sleep(2)
    return UploadResult


class ExitProgram(Exception):
    """
    Exits the program by using ExitProgram exception handler.
    Ensures the M2MconnectLOCKfile is released before close.
    """
    pass


#############################################
# Main program loop with exception handlers #
#############################################
def main():
    """ConnectAgent-AC810S main. Modem initialisation and exception handling"""
    print "[ -- ] System Initiating Connection Check for AC810S Modem Over "+AC810_Interface+" Interface"
    global backofftimer
    global backoffStart
    #Check lock file to see if another M2Mconnect program is already running. If already running then exit.
    ConnectAgentLOCKfile = lockfile.FileLock('ConnectAgentLOCKfile')
    try:
        ConnectAgentLOCKfile.acquire(timeout=0)    # wait up to 0 seconds
    except lockfile.LockError:
        print " "
        print "**********"
        print "Exception (ConnectAgentLOCKfile is locked)"
        print "Check another instance of ConnectAgent-AC810S.py is not already running"
        print "**********"
        sys.exit()
    while True:
        try:
            if connectbackoff(): 
                #print "Start loop backofftimer ", backofftimer
                #Check what interfaces already have a IP address
                InterfaceCheck('eth0')
                if AC810_Interface == "eth1":
                    InterfaceCheck('wlan0')
                elif AC810_Interface == "wlan0":
                    InterfaceCheck('eth1')
                else:
                    print "[ERROR] WARNING AC810_Interface is not correctly configured in ConnectAgent-AC810S.py"
                #Begin interface setup
                if ModemDetect():
                    if RaspberryIPcheck():
                        if ModemLogin():
                            currentIP = ModemIPcheck()
                            if currentIP:
                                if not correctIP(currentIP):
                                    # Disconnect currnet PDP session and start again
                                    if APN == 'telstra.internet':
                                        print "[ -- ] APN set to", APN, "but current modem IP is public"
                                    elif APN == 'telstra.extranet':
                                        print "[ -- ] APN set to", APN, "but current modem IP is private"
                                    print "[ -- ] Closing current network PDP connection"
                                    ModemPdpDisconnect()
                                    time.sleep(10)
                                    ModemPdpSetAPN(1)
                                    time.sleep(5)
                                    ModemPdpConnect()
                                    returnedIP = ModemIPcheck()
                                    if returnedIP is not None:
                                        if correctIP(returnedIP):
                                            ModemIPchange(returnedIP)
                                            print "[ OK ] System IP Connection Complete"
                                            print "************************************"
                                            backofftimer = backoff
                                            raise ExitProgram()
                                        else:
                                            print "[FAIL] AC810 Modem did not get correct IP address for APN", APN
                                            ModemPdpDisconnect()
                                            time.sleep(10)
                                            backoffStart = time.time()
                                            print " "
                                    else:
                                        print "[FAIL] Modem did not get IP address from network"
                                        backoffStart = time.time()
                                        print " "
                                else:
                                    # Currnet IP and APN match or APN not set as either extranet/internet.
                                    ModemIPchange(currentIP)
                                    print "[ OK ] System IP Connection Complete"
                                    print "************************************"
                                    backofftimer = backoff
                                    raise ExitProgram()
                            else:
                                ModemPdpSetAPN(1)
                                time.sleep(5)
                                ModemPdpConnect()
                                returnedIP = ModemIPcheck()
                                if returnedIP is not None:
                                    if correctIP(returnedIP):
                                        ModemIPchange(returnedIP)
                                        print "[ OK ] System IP Connection Complete"
                                        print "************************************"
                                        backofftimer = backoff
                                        raise ExitProgram()
                                    else:
                                        print "[FAIL] AC810S Modem did not get correct IP address for APN", APN
                                        ModemPdpDisconnect()
                                        time.sleep(10)
                                        backoffStart = time.time()
                                        print " "
                                else:
                                    print "[FAIL] A810S Modem could not get IP address from network"
                                    backoffStart = time.time()
                                    print " "
                        else:
                            print "[FAIL] Unable to Login as Admin to AC810S Modem"
                            backofftimer = backoff
                    else:
                        print "[FAIL] RaspberryPi could not get IP address from AC810S modem\n"
                        backofftimer = backoff
                else:
                    print "[FAIL] Unable to open connection to AC810S Modem\n"
                    backofftimer = backoff
            time.sleep(5)
        except ExitProgram:
            ConnectAgentLOCKfile.release()
            sys.exit()
        except urllib2.HTTPError as e:
            # Capture HTTPError errors
            print " "
            print "**********"
            print "Exception detected (HTTPError)"
            print "Code:", e.code
            print "Reason:", e.reason
            print "**********"
        except urllib2.URLError as e:
            # Capture URLError errors
            print " "
            print "**********"
            print "Exception detected (URLError)"
            print "Reason:", e.reason
            print "**********"
            print "[ -- ] Rebooting Modem"
        except OSError as e:
            # Capture OS command line errors
            print " "
            print "**********"
            print "Exception detected (OSError)"
            print " **********"
            print e.errno
            print e.filename
            print e.strerror
            traceback.print_exc(file=sys.stdout)
            print "**********"
            ConnectAgentLOCKfile.release()
            sys.exit()
        except Exception as e:
            print " "
            print "**********"
            print "Exception detected"
            print type(e)
            print e
            traceback.print_exc(file=sys.stdout)
            print "**********"
            ConnectAgentLOCKfile.release()
            sys.exit()
        except KeyboardInterrupt:
            print " "
            print "**********"
            print "Exception (Keyboard Interrupt)"
            print "**********"
            ConnectAgentLOCKfile.release()
            sys.exit()
        except:
            print " "
            print "**********"
            print "Exception (Unknown)"
            traceback.print_exc(file=sys.stdout)
            print "**********"
            ConnectAgentLOCKfile.release()
            sys.exit()

if __name__ == "__main__":
    main()




