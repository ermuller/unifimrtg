#!/usr/bin/python
# a quick hack to feed ubiquiti user stats to mrtg
# (c)2017 Network Utility Force / Erik Muller
# Licensed under CC BY-SA 4.0 terms

# global predefines
mibdir='/usr/local/share/snmp/mibs/'
hosts=['unifi1.example.org','unifi2.example.org']
comm='yourmom'

import time
import logging, sys
import argparse
from pysnmp.hlapi import *
#from pysnmp.smi import builder, view, error
from pysnmp.proto import rfc1905

parser = argparse.ArgumentParser(description='Grab user counts from APs.')
parser.add_argument('--debug', dest='debug', action='count',
                    help='turn on debugging (multiple times for more detail')
parser.add_argument('--total', dest='total', action='store_true',
                    help='report total instead of per-band')
parser.add_argument('--mrtg', dest='mrtg', action='store_true',
                    help='output in MRTG format')

args = parser.parse_args()
if (args.debug > 0):
  loglevel=logging.DEBUG
else:
  loglevel=logging.INFO
logging.basicConfig(stream=sys.stderr, level=loglevel)

def main():
  fiveusers=0
  twousers=0
  for (host) in hosts:
    # foreach unifiVapEssId: unifiVapNumStations, unifiVapRadio...
    #ssids = walk_ap_info(host, comm, 'unifiVapEssId')
    #print ssids 
    users = walk_ap_info(host, comm, 'unifiVapNumStations')
    #print users
    radios = walk_ap_info(host, comm, 'unifiVapRadio')
    #print radios
    for i in sorted(radios.keys()):
      count=int(users[i])
      if (radios[i] == "na"):
        fiveusers += count
      else:
        twousers += count
  if args.mrtg:
    if args.total:
      print "%d"%(fiveusers + twousers)
      print "0"
    else:
      print "%d"%fiveusers
      print "%d"%twousers
    print int(time.time())
    print "localhost"
  else:
    if args.total:
      print (fiveusers + twousers)
    else:
      print "5g  total", fiveusers
      print "24g total", twousers
    


# walk
def walk_ap_info(device, comm, entry):
  d={}
  Oid=ObjectType(ObjectIdentity('UBNT-UniFi-MIB', entry).addAsn1MibSource('file:///usr/local/share/snmp/mibs/'))
  startString = None
  for (errorIndication,
     errorStatus,
     errorIndex,
     varBinds) in bulkCmd(SnmpEngine(),
                          #UsmUserData('usr-md5-des', 'authkey1', 'privkey1'),
                          CommunityData(comm, mpModel=0),
                          UdpTransportTarget((device, 161)),
                          ContextData(),
                          1, 25,
                          Oid,
                          lexicographicMode=False):
  
    if errorIndication:
      print(errorIndication)
      break
    elif errorStatus:
      print('%s at %s' % (errorStatus.prettyPrint(),
                          errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
      break
    else:
      name, value = varBinds[0]
      #print name, value
      if startString is None:
        startString = ".".join(map(str, str(name).split(".")[:-1]))
      if value.isSameTypeWith(rfc1905.endOfMibView):
        logging.debug( "saw end at %s"% name)
        break
      elif not oidStartsWith(name, startString):
        # getBulk keeps iterating.  Stop if we are outside of our subtree.
        logging.debug("%s not under %s"%(name,startString))
        break

      if (value is not None):
       if (name is not None):
        logging.debug("Values %s, %s" % (str(name).split(".")[-1], value))
        index = str(name).split(".")[-1]
	value=str(value)
      d[index]=value
  return d

def oidStartsWith(oid1, startStr):
  prefix = ".".join(map(str, str(oid1).split(".")[:-1]))
  return startStr.startswith(prefix)


if __name__ == "__main__":
    main()

