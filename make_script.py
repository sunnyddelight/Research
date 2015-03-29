__author__ = 'duansy'
import sys
import math
import random
from lxml import etree as ET
#import xml.etree.ElementTree as ET
from sklearn.cluster import KMeans
import numpy as np
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
        self.latitude=0
        self.longitude=0
        self.label=-1
    def add_info(self,name,val):
        self.info[name]=val
    def add_coord(self, latitude,longitude):
        self.latitude=latitude
        self.longitude=longitude
class usb:
    def __init__(self):
        self.name=''
        self.location=''
        self.id=-1
        self.attributes={}
    def add_attrib(self,category,attrib):
        self.name=(self.name+('-' if self.name!='' else '')+attrib).replace(" ","")
        self.attributes[category]=attrib
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
    if total!=0:
        for key in parameters:
            if key!='location':
                k=0
                for l in range(0,total/division_size):
                    for option in parameters[key].options:
                        for j in range(0,int(division_size/len(parameters[key].options))):
                            usbs[int(j+k*division_size/len(parameters[key].options))].add_attrib(key,option)
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
                usbs[i].add_attrib(key,parameters[key].options.keys()[remaining[i]%len(parameters[key].options.keys())])
                remaining[i]/=len(parameters[key].options.keys())
        usbs[i].add_location(parameters['location'][remaining[i]])
        usbs[i].add_id(cur_id)
    return usbs
def label_places(places, num_labels):
    coords=[[place.latitude, place.longitude] for place in places]
    means=KMeans(n_clusters=num_labels, init='k-means++', max_iter=300, tol=0.0001, precompute_distances=True, verbose=0, random_state=None, copy_x=True, n_jobs=1)
    clusterPoints=np.array(coords)
    clusters=means.fit(clusterPoints)
    for i in range(0,len(places)):
        places[i].label = clusters.labels_[i]+1
def main():
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

    #Parse Locations
    for child in root.find('places'):
        tempPlace=place(child.find('name').text)
        tempPlace.add_coord(float(child.find('latitude').text),float(child.find('longitude').text))
        for category in child.iter('category'):
            tempPlace.add_info(category.attrib['name'],category.text)
        places.append(tempPlace)



    settings={}
    for child in root.find('settings'):
        if child.attrib['name']!='use_location_categories':
            settings[child.attrib['name']]=child.text
        else:
            locations=[]
            for category in child.iter('category'):
                locations.append(category.attrib['name'])
            settings[child.attrib['name']]=locations

    people=[]
    for child in root.find('people'):
        people.append(child.attrib['name'])


    label_places(places, int(settings['num_clusters']))
    variables['location']=places
    drives=label_drives(variables,settings)
    drives_out=ET.Element('drives')
    for drive in drives:
        print drive.name + '-' + drive.location.name.replace(" ","") + '-' + str(drive.id) + " Cluster: " + str(drive.location.label)
        drive_out=ET.SubElement(drives_out,'drive')
        name_out=ET.SubElement(drive_out,'id')
        name_out.text=drive.name + '-' + drive.location.name.replace(" ","") + '-' + str(drive.id)
        for attrib in drive.attributes:
            attrib_out=ET.SubElement(drive_out,attrib)
            attrib_out.text=drive.attributes[attrib]
        location_out=ET.SubElement(drive_out,'location')
        location_out.text=drive.location.name.replace(" ","")
        latitude_out=ET.SubElement(drive_out,'latitude')
        latitude_out.text=str(drive.location.latitude)
        longitude_out=ET.SubElement(drive_out,'longitude')
        longitude_out.text=str(drive.location.longitude)
        cluster_out=ET.SubElement(drive_out,'cluster')
        cluster_out.text=str(drive.location.label)
        assignee_out=ET.SubElement(drive_out,'assignee')
        assignee_out.text=str(people[drive.location.label % len(people)])
    tree_out=ET.ElementTree(element=drives_out)
    tree_out.write('output.xml', pretty_print=True)
main()
