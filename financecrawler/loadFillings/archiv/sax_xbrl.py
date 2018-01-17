'''
Created on 07.02.2017

@author: olli
'''

import xml.sax
from datetime import datetime
import re
pattern = re.compile("^(-[0-9]+)|([0-9]+)$")


# SAX Anweisung
class XbrlHandler(xml.sax.ContentHandler):
    
    def __init__(self, verbose=False):
        self.CurrentData = ""
        self.context = {}
        self.date = ''
        self.id = ''
        self.data = {}
        self.contextRef = ''
        self.misc = {}
        self.content = ''
        self.verbose = verbose

# Call when an element starts
    def startElement(self, tag, attr):
        tag = tag.split(":")[1] if ':' in tag else tag
        tag = tag
        self.CurrentData = re.sub('\.', '', tag)
        
        if self.CurrentData.lower() == 'context':
            self.id = attr['id']
            self.context[self.id] = {}
        elif 'contextRef' in attr and 'dei:' not in tag.lower():
            self.contextRef = attr['contextRef']
            if self.contextRef not in self.data: self.data[self.contextRef] = {}

# Call when a character is read
    def characters(self, content):
        self.content = content
        if self.CurrentData.lower() in ['instant', 'startdate', 'enddate']:
            self.date = content

# Call when an elements ends
    def endElement(self, tag):
        if self.CurrentData.lower() in ['startdate', 'enddate', 'instant']:
            self.context[self.id][self.CurrentData] = datetime.strptime(self.date, "%Y-%m-%d")
        elif self.contextRef != '' and pattern.match(self.content):
            self.data[self.contextRef][self.CurrentData] = self.content
        elif self.CurrentData != '':
            self.misc[self.CurrentData] = self.content
        self.CurrentData = ''
        self.contextRef = ''

    def getData(self):
        return {'context': self.context, 'data': self.data, 'misc': self.misc}
 
 