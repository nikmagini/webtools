#!/usr/bin/env python

################################################################
# crypttest.py
#
# Version info: $Id: crypttest.py,v 1.2 2007/03/30 12:51:38 eulisse Exp $
################################################################

import sys
import getopt
import os
from Crypto.Cipher import Blowfish   # DES,AES
import base64 


#####################################################
# PARAMETERS
#
# we use a 56 byte key
key = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabde'
#####################################################

def addPadding(s):
    r = 8 - len(s)%8
    ret = s + r * chr(r)
    return ret

def encrypt(plain):
    obj = Blowfish.new(key, Blowfish.MODE_CBC,iv)
    plain=addPadding(plain)

    # prepend the iv to the encrypted string
    encr = iv + obj.encrypt(plain)
    encr64=base64.encodestring(encr)    
    return encr64;

def decrypt(encr64):
    decr64=base64.decodestring(encr64)

    # retrieve the iv from the encrypted string
    iv = decr64[0:8];
    decr64 = decr64[8:]
    
    obj = Blowfish.new(key, Blowfish.MODE_CBC,iv)
    decr = obj.decrypt(decr64)

    # remove any standard padding
    if ord(decr[-1]) <= 8:
        decr = decr.strip(decr[-1])

    return decr


##############
# MAIN

(o,leftover)=getopt.getopt(sys.argv[1:],"edhi:")

opts={}
for k,v in o:
    opts[k] = v
    
mode="e"
if opts.has_key('-d'):
    mode="d"

if opts.has_key('-i'):
    iv = opts['-i']
else:
    iv = os.urandom(8)

if len(iv) != 8:
    print 'Error: IV needs to have length = 8'
    sys.exit(1);

text=leftover[0]

if mode == 'e':
    encr=encrypt(text)
    if encr[-1] == '\n':
        encr = encr[:-1]
    print '>'+encr+'<'
else:
    decr=''
    decr=decrypt(text)
    print '>'+decr+'<'


sys.exit(0)


#######################################################

#print 'key:',key
#print 'key length: ', len(key)
#key = 'abcdefgh'

# Some tests with other ciphers
#
#obj = DES.new(key, DES.MODE_ECB)
#obj = AES.new(key, AES.MODE_ECB)
#obj = Blowfish.new(key, Blowfish.MODE_CBC,'abcdefgh')
#obj = Blowfish.new(key, Blowfish.MODE_CBC)
#obj = Blowfish.new(key, Blowfish.MODE_ECB)
#print "Key size: ", obj.key_size   # 0 means variable key size
#print "Block size: ", obj.block_size
