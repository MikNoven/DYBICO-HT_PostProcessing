# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 12:50:36 2022

@author: tvh307
"""
def CeasarShifting(text, shift, alphabets):
    
    def shift_alphabet(alphabet):
        return alphabet[shift:] + alphabet[:shift]
    
    shifted_alphabets = tuple(map(shift_alphabet, alphabets))
    final_alphabet = ''.join(alphabets)
    final_shifted_alphabet = ''.join(shifted_alphabets)
    table = str.maketrans(final_alphabet, final_shifted_alphabet)
    return text.translate(table)