#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from sklearn.cluster import KMeans

import AreaMesh


def MakeMeshDataForClusteringDays(UserTripData):    
    
    MeshData = np.zeros((len(UserTripData.keys()), 10))
    dayItr = 0
    for datadate in sorted(UserTripData.keys()):
        secondMeshList = []
        for tripID in sorted(UserTripData[datadate].keys()):
            lat1 = UserTripData[datadate][tripID].OriginPlaceLat
            lon1 = UserTripData[datadate][tripID].OriginPlaceLon
            lat2 = UserTripData[datadate][tripID].DestinationPlaceLat
            lon2 = UserTripData[datadate][tripID].DestinationPlaceLon
            latS = UserTripData[datadate][tripID].LatSequence
            lonS = UserTripData[datadate][tripID].LonSequence
            
            secMesh = AreaMesh.searchAreaMesh(lat1, lon1)[0]
            try:
                int(secMesh)
                if secMesh not in secondMeshList:
                    secondMeshList.append(secMesh)
            except ValueError:
                pass
            secMesh = AreaMesh.searchAreaMesh(lat2, lon2)[0]
            try:
                int(secMesh)
                if secMesh not in secondMeshList:
                    secondMeshList.append(secMesh)
            except ValueError:
                pass 
            if len(latS) > 0:
                for i in range(len(latS)):
                    lat3 = latS[i]
                    lon3 = lonS[i]
                    secMesh = AreaMesh.searchAreaMesh(lat3, lon3)[0]
                    try:
                        int(secMesh)
                        if secMesh not in secondMeshList:
                            secondMeshList.append(secMesh)
                    except ValueError:
                        pass
        
        
        secondMeshDict = {}
        for mesh in secondMeshList:
            lat = (float(mesh[0:2])/1.5 + 1.0/12*int(mesh[4]))*1.5
            lon = 100 + float(mesh[2:4]) + 1.0/8*int(mesh[5])
            secondMeshDict.update({mesh:[lat, lon]})
            #print datadate, mesh, lat, lon
        
        if len(secondMeshDict.keys()) > 0:
            NorthernmostMesh = [0,0]
            SouthernmostMesh = [0,0]
            EasternmostMesh = [0,0]
            WesternmostMesh = [0,0]
            MeanMesh = [0,0]
        
            meshItr = 0
            for mesh in secondMeshDict.keys():
                if meshItr == 0:
                    (NorthernmostMesh[0], NorthernmostMesh[1]) = (secondMeshDict[mesh][0], secondMeshDict[mesh][1])
                    (SouthernmostMesh[0], SouthernmostMesh[1]) = (secondMeshDict[mesh][0], secondMeshDict[mesh][1])
                    (EasternmostMesh[0], EasternmostMesh[1]) = (secondMeshDict[mesh][0], secondMeshDict[mesh][1])
                    (WesternmostMesh[0], WesternmostMesh[1]) = (secondMeshDict[mesh][0], secondMeshDict[mesh][1])
                    (MeanMesh[0], MeanMesh[1]) = (secondMeshDict[mesh][0], secondMeshDict[mesh][1])
            
                elif meshItr > 0:
                    if secondMeshDict[mesh][0] > NorthernmostMesh[0]:
                        NorthernmostMesh = secondMeshDict[mesh]
                    if secondMeshDict[mesh][0] < SouthernmostMesh[0]:
                        SouthernmostMesh = secondMeshDict[mesh]
                    if secondMeshDict[mesh][1] > EasternmostMesh[1]:
                        EasternmostMesh = secondMeshDict[mesh]
                    if secondMeshDict[mesh][1] < WesternmostMesh[1]:
                        WesternmostMesh = secondMeshDict[mesh]
                
                    MeanMesh[0] += secondMeshDict[mesh][0]
                    MeanMesh[1] += secondMeshDict[mesh][1]
                    
                meshItr += 1
        
            MeshData[dayItr,:] = [MeanMesh[0]/meshItr, MeanMesh[1]/meshItr] +  NorthernmostMesh + SouthernmostMesh + EasternmostMesh + WesternmostMesh
            
        dayItr += 1
    
    return MeshData

def ClusteringDaysData(MeshData, UserTripData, K=10):
    
    ClusterDataDate = {}
    
    if len(UserTripData.keys()) >= 30:
        kmeans_model = KMeans(n_clusters=K, random_state=10).fit(MeshData)
        labels = kmeans_model.labels_
    
        for i in range(len(labels)):        
            try:
                ClusterDataDate[labels[i]].append(sorted(UserTripData.keys())[i])
            except KeyError:
                ClusterDataDate.update({labels[i]:[sorted(UserTripData.keys())[i]]})
    
    else:
        ClusterDataDate.update({0:sorted(UserTripData.keys())})
    
    return ClusterDataDate
    