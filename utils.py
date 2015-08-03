import json
import requests
import urllib
import os
import sys
from json import loads
from constants import Constants

import cv2
import time
import numpy
import array

def percentage(percent, whole):
	return (percent * 100.0) / whole

def from_percentage(percentage, whole):
	return (whole * percentage) / 100

def bytesto(bytes, to, bsize=1024):
	
	"""convert bytes to megabytes, etc.
	   sample code:
		   print('mb= ' + str(bytesto(314575262000000, 'm')))

	   sample output: 
		   mb= 300002347.946
	"""
 
	a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
	r = float(bytes)
	for i in range(a[to]):
		r = r / bsize

	return(r)

def print_inline(string):
	sys.stdout.write(string)
	sys.stdout.flush()

def contains(small, big):
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False
