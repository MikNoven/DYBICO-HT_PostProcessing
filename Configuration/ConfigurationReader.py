# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:23:23 2022

@author: tvh307
"""

# remeber to install pycryptodome
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad 
import Configuration.CeasarShifting as Ceasar
import string
import os

def readConfiguration():
    
    with open(os.path.join('Configuration','config_key.bin'), 'rb') as f:
        readKey = f.read()
     
    with open(os.path.join('Configuration','Configuration.bin'), 'rb') as f :
        iv = f.read(16)
        encrypted_data = f.read()
        
    cipher = AES.new(readKey, AES.MODE_CBC, iv=iv)
    original = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    config = Ceasar.CeasarShifting(str(original), -8, [string.ascii_lowercase, string.ascii_uppercase, string.digits, string.punctuation])
    return config

def GetRemotepath(config):
    configs = config.split(',')
    remotepath = configs[3]
    remotepath = remotepath.removeprefix(' remotepath=')
    remotepath = remotepath.removesuffix('}')
    return remotepath

def GetHost(config):
    configs = config.split(',')
    host = configs[0]
    host = host.removeprefix('t}host=')
    return host 

def GetUser(config):
    configs = config.split(',')
    user = configs[1]
    user = user.removeprefix(' username=')
    return user 
    
def GetPsw(config):
    configs = config.split(',')
    psw = configs[2]
    psw = psw.removeprefix(' password=')
    return psw

