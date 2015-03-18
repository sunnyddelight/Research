__author__ = 'duansy'
import sys
import math
import random
import xml.etree.ElementTree as ET
class variable:
    def __init__(self,name):
        self.name=name
        self.options={}
    def add_value(self,val):
        self.options[val]=0
    def size(self):
        return len(self.options)
class place:
    def __init__(self,name):
        self.name=name
        self.info={}
    def add_info(self,name,val):
        self.info[name]=val
class usb:
    def __init__(self):
        self.name=''
        self.location=''
        self.id=-1
    def add_attrib(self,attrib):
        self.name=(self.name+('-' if self.name!='' else '')+attrib).replace(" ","")
    def add_location(self,location):
        self.location=location
    def add_id(self,id):
        self.id=id
def getSpaceSize(parameters):
    curSize=1
    for key in parameters:
        if key!='location':
            curSize*=parameters[key].size()
    curSize*=len(parameters['location'])
    return curSize

def label_drives(parameters,settings):
    usbs=[]
    for i in range(0,int(settings['num_drives'])):
        usbs.append(usb())
    division_size=total=int(int(settings['num_drives'])/getSpaceSize(parameters))*getSpaceSize(parameters)
    for key in parameters:
        if key!='location':
            k=0
            for l in range(0,total/division_size):
                for option in parameters[key].options:
                    for j in range(0,int(division_size/len(parameters[key].options))):
                        usbs[int(j+k*division_size/len(parameters[key].options))].add_attrib(option)
                    k+=1
            division_size/=len(parameters[key].options)
    cur_id=0
    for i in range(0,int(int(settings['num_drives'])/getSpaceSize(parameters))*getSpaceSize(parameters)/
            len(parameters['location'])):
        k=0
        for location in parameters['location']:
            usbs[i*len(parameters['location'])+k].add_location(location)
            usbs[i*len(parameters['location'])+k].add_id(cur_id)
            k+=1
        cur_id+=1
    num_remaining=int(int(settings['num_drives'])-math.floor(int(
        settings['num_drives'])/getSpaceSize(parameters))*getSpaceSize(parameters))
    remaining=random.sample(range(0,int(getSpaceSize(parameters))),num_remaining)
    for i in range(-1,-num_remaining-1,-1):
        for key in parameters:
            if key!='location':
                usbs[i].add_attrib(parameters[key].options.keys()[remaining[i]%len(parameters[key].options.keys())])
                remaining[i]/=len(parameters[key].options.keys())
        usbs[i].add_location(parameters['location'][remaining[i]])
        usbs[i].add_id(cur_id)
    return usbs


tree=ET.parse(sys.argv[1])
root=tree.getroot()
variables={}
places=[]
for child in root.find('variables'):
    tempVar=variable(child.attrib['name'])
    for option in list(child):
        if('abbreviation' in option.attrib):
            tempVar.add_value(option.attrib['abbreviation'])
        else:
            tempVar.add_value(option.text)
    variables[tempVar.name]=tempVar
for child in root.find('places'):
    tempPlace=place(child.find('name').text)
    for category in child.iter('category'):
        tempPlace.add_info(category.attrib['name'],category.text)
    places.append(tempPlace)
variables['location']=places

settings={}
for child in root.find('settings'):
    if child.attrib['name']!='use_location_categories':
        settings[child.attrib['name']]=child.text
    else:
        locations=[]
        for category in child.iter('category'):
            locations.append(category.attrib['name'])
        settings[child.attrib['name']]=locations
drives=label_drives(variables,settings)
for drive in drives:
    print drive.name + '-' + drive.location.name.replace(" ","") + '-' + str(drive.id)

