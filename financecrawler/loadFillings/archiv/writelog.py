'''
Created on 22.02.2017

@author: olli
'''
from time import strftime

def log(path, *msg):
    """Logfile beschreiben"""
    file = open(path,"a")
    for m in msg:
        file.write("%s: %s\n" % (strftime("%d.%m.%Y %H:%M:%S"), m))
    file.close