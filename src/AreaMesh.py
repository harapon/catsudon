#!/usr/bin/env python
# -*- coding: utf-8 -*-

def searchLatMesh(lat):
    lat = float(lat)
    v1 = 30
    v2 = int((lat - 20)/(2.0/3))
    v1 += v2
    v3 = int((lat - 20)/(2.0/3/8/10) - 80*v2)
    v4 = v3/10
    v5 = v3 - v4*10
    return(v1, v4, v5)

def searchLonMesh(lon):
    lon = float(lon)
    
    v1 = 22
    v2 = int((lon - 100 - v1))
    v1 += v2
    v3 = int((lon - (122 + v2))*80)
    v4 = v3/10
    v5 = v3 - v4*10
    return(v1, v4, v5)

def searchAreaMesh(lat, lon):
    (v1, v2, v3) = searchLatMesh(lat)
    (v4, v5, v6) = searchLonMesh(lon)
    secondMesh = str(v1) + str(v4) + str(v2) + str(v5)
    thirdMesh  = str(v1) + str(v4) + str(v2) + str(v5) + str(v3) + str(v6)
    return secondMesh, thirdMesh

def extractSecondThirdMesh(UserData):
    secondMeshList = []
    thirdMeshList = []
    
    for trip in UserData.keys():
        for dataid in UserData[trip]:
            lat = dataid.lat
            lon = dataid.lon
            (secMesh, thiMesh) = searchAreaMesh(lat,lon)
            
            try:
                int(secMesh)
                if secMesh not in secondMeshList:
                    secondMeshList.append(secMesh)
                if thiMesh not in thirdMeshList:
                    thirdMeshList.append(thiMesh)
            except ValueError:
                pass
    
    return (secondMeshList, thirdMeshList)

def MakeAllSecondMeshList(UserTripData):
    AllSecondMeshList = []
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            lat1 = UserTripData[datadate][tripID].OriginPlaceLat
            lon1 = UserTripData[datadate][tripID].OriginPlaceLon
            lat2 = UserTripData[datadate][tripID].DestinationPlaceLat
            lon2 = UserTripData[datadate][tripID].DestinationPlaceLon
            latS = UserTripData[datadate][tripID].LatSequence
            lonS = UserTripData[datadate][tripID].LonSequence
            
            secMesh = searchAreaMesh(lat1, lon1)[0]
            try:
                int(secMesh)
                if secMesh not in AllSecondMeshList:
                    AllSecondMeshList.append(secMesh)
            except ValueError:
                pass
            secMesh = searchAreaMesh(lat2, lon2)[0]
            try:
                int(secMesh)
                if secMesh not in AllSecondMeshList:
                    AllSecondMeshList.append(secMesh)
            except ValueError:
                pass
                
            if len(latS) > 0:
                for i in range(len(latS)):
                    lat3 = latS[i]
                    lon3 = lonS[i]
                    secMesh = searchAreaMesh(lat3, lon3)[0]
                    try:
                        int(secMesh)
                        if secMesh not in AllSecondMeshList:
                            AllSecondMeshList.append(secMesh)
                    except ValueError:
                        pass
    
    return AllSecondMeshList
