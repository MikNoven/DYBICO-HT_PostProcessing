# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 09:46:27 2022

@author: tvh307
"""

# remeber to install pycryptodome
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad 

simple_key = get_random_bytes(32)

salt = b'\xf9\xd7rC\xf3\x8e\x9d\xf2\x8a\xd3\xab\xfef\xbe\x03h\x15"}\xb1L\xc1\xc0\xdeJ1\xaf&\x11\x8cBM'
password = "n930fjs+2-.spk3,+Dwo4,_"

key = PBKDF2(password, salt, dkLen=32 )
print(key)