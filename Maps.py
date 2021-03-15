#!/usr/bin/env python
# coding: utf-8

# In[8]:


import gmaps
import gmaps.datasets
import os
from scapy.all import *
from ip2geotools.databases.noncommercial import Ipstack
import ipinfo

#initial configuration of gmaps with Google API  key
gmaps.configure(api_key='AIzaSyDXm-HJwRTa0FhoRlKi-p4uHYHc8pR-dTs')
#initalize google map
fig = gmaps.figure()

def userInput():
    userIn = input("Enter a website or IP: ")
    return userIn

def traceroute(webIP):
    '''
    Function for performing traceroute and returning list of IPs
    '''
    hostname = webIP #Change that to user input later
    ipList = [] #used to hold a list of IPs
    print("Destination: " + hostname)

    i = 1
    for i in range(1,28):
        #pkt = IP(dst=hostname, ttl=i)/ UDP(dport=33434)
        pkt = IP(dst=hostname, ttl=i)/ ICMP()
    
        #packet is sent
        reply = sr1(pkt, verbose=0, timeout=1, retry =-3)
        #print(reply.type)
    
        #No reply
        if reply is None:
            print("%d Request timed out" %i)
            continue
            
            
        elif reply.type == 0:
            #reached
            print("Done", reply.src)
            ipList.append(reply.src)
            break
            
        else:
            print ("%d hops away: " %i, reply.src)
            ipList.append(reply.src)
        
    #if it sends more than 28 packets and never breaks
    #print(i)
    if(i > 28):
        print("Request timed out.")
    return ipList

def addMarkers(ipList):
    '''
    Class for adding markers to the map and converting ipList to coordinates
    '''
    access_token='1687752321ca13'
    handler = ipinfo.getHandler(access_token) #initialize handler for ipinfo
    coords=[] #List of coordinates found from converting ipList
    markerLab = [] #List of marker labels (1 to x)
    citySt = [] #List of city, state based off coordinate list
    
    #iterate through list of IPs
    for i in range(len(ipList)):
        try: #check if IP is valid (has all necessary information)
            response = Ipstack.get(ipList[i], api_key='bd6f2393dca8bab90bc9e4304fba1139')
            details = handler.getDetails(ipList[i])            
        except: #ignore the given IP (either empty or masked ip)
            continue
        #converting location to tuple and adding to coords list
        res = eval(details.loc)
        coords.append(res)
        #add marker label numbers to markerLab list
        markerLab.append(str(i))
        #adding "city, state" to citySt list
        #citySt.append(details.city + ', ' + details.region)
        if i == 3:
            citySt.append(details.city + ', ' + details.region + ": " + "Start")
        elif i == len(ipList):
            citySt.append(details.city + ', ' + details.region + "\n" + "Finish")
        else:
            citySt.append(details.city + ', ' + details.region)

    #add all coords, labels and city/state to marker layer
    marker = gmaps.marker_layer(
        coords, 
        label = markerLab,
        info_box_content = citySt
    )
    for i in range(len(marker.markers)):
        if i == 0:
            if marker.markers[i].location == marker.markers[i+1].location:
                marker.markers[i].label = "+"
        elif i == len(marker.markers)-1:
            if marker.markers[i].location == marker.markers[i-1].location:
                marker.markers[i].label = "+"
        elif marker.markers[i].location == marker.markers[i-1].location or marker.markers[i].location == marker.markers[i+1].location:
            marker.markers[i].label = "+"
    #add markers to map
    fig.add_layer(marker)
    return coords
    
def drawLines(coords):
    '''
    Function for drawing lines on the map based off list of coordinates
    '''
    for i in range(len(coords)-1): 
        if coords[i] != coords[i+1]:
            lines = gmaps.Line(start=(coords[i]), end=(coords[i+1]), stroke_weight=3.0, stroke_color='#FF0000')
            drawing = gmaps.drawing_layer(features=[lines], mode='DISABLED', show_controls=False)
            fig.add_layer(drawing)
        else:
            continue
            
def main():
    webIP = userInput()
    ipList = traceroute(webIP) #retreiving list of IPs from traceroute()
    coords = addMarkers(ipList) #getting coords and adding marker layer to map
    drawLines(coords) #drawing lines on map
    
if __name__ == "__main__":
    main()

fig #display google map


# In[ ]:




