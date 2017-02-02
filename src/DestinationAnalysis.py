#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import random
import datetime

import numpy as np
from sklearn.cluster import KMeans

import LatLonCalc
import foursquare_API


def output(fo, outputList):
    text = ""
    for i in range(len(outputList)-1):
        text = text + str(outputList[i]) + ","
    text = text + str(outputList[len(outputList)-1]) + "\n"
    fo.write(text)

def MakeDestinationDataforClustering(UserTripData):
    #Kmeans用データの作成
    NumOfDestinationsAll = 0
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            NumOfDestinationsAll += 2
    
    DestinationData = np.zeros((NumOfDestinationsAll, 2))
    itr = 0
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):            
            DestinationData[itr,:] = [float(UserTripData[datadate][tripID].OriginPlaceLat)*1.5, float(UserTripData[datadate][tripID].OriginPlaceLon)]
            itr += 1
            DestinationData[itr,:] = [float(UserTripData[datadate][tripID].DestinationPlaceLat)*1.5, float(UserTripData[datadate][tripID].DestinationPlaceLon)]
            itr += 1
    
    return (DestinationData, NumOfDestinationsAll)

def CalcNumOfCanopy(UserTripData, T1=500, T2=250):
    
    DestinationDict = {}
    destItr = 0
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            DestinationDict.update({destItr:[UserTripData[datadate][tripID].OriginPlaceLat, UserTripData[datadate][tripID].OriginPlaceLon]})
            destItr += 1
            DestinationDict.update({destItr:[UserTripData[datadate][tripID].DestinationPlaceLat, UserTripData[datadate][tripID].DestinationPlaceLon]})
            destItr += 1
    
    CanopyDict = {}
    NumOfCanopy = 0
    while len(DestinationDict.keys()) > 0:
        NumOfDestinations = len(DestinationDict.keys())
        candidate = DestinationDict.keys()[int(math.floor(random.random()*NumOfDestinations))]        
        candidateLat = DestinationDict[candidate][0]
        candidateLon = DestinationDict[candidate][1]
    
        canopyT1List = []
        canopyT2List = []    
        for dest in DestinationDict.keys():
            d1 = LatLonCalc.CalcDistance(candidateLat, candidateLon, DestinationDict[dest][0], DestinationDict[dest][1])
            if d1 <= T1:
                canopyT1List.append(dest)
            if d1 <= T2:
                canopyT2List.append(dest)
                DestinationDict.pop(dest)        
        CanopyDict.update({NumOfCanopy:canopyT2List})
        NumOfCanopy += 1
    
    return NumOfCanopy

def DestinationKMeans(DestinationData, UserTripData, K):
    
    kmeans_model = KMeans(n_clusters=K, random_state=10).fit(DestinationData)
    labels = kmeans_model.labels_
    
    #各clusterのラベル，緯度・経度の格納
    clusteringLabelDict = {}
    for i in range(K):
        clusterLat = kmeans_model.cluster_centers_[i][0]/1.5
        clusterLon = kmeans_model.cluster_centers_[i][1]
        clusteringLabelDict.update({i:[clusterLat, clusterLon]})
    
    #各データの情報を格納
    itr = 0
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            UserTripData[datadate][tripID].OriginPlaceID = labels[itr]
            UserTripData[datadate][tripID].OriginPlaceLat = clusteringLabelDict[labels[itr]][0]
            UserTripData[datadate][tripID].OriginPlaceLon = clusteringLabelDict[labels[itr]][1]
            itr += 1
            
            UserTripData[datadate][tripID].DestinationPlaceID = labels[itr]
            UserTripData[datadate][tripID].DestinationPlaceLat = clusteringLabelDict[labels[itr]][0]
            UserTripData[datadate][tripID].DestinationPlaceLon = clusteringLabelDict[labels[itr]][1]
            itr += 1
    
    return (UserTripData, clusteringLabelDict)

def ReadPOICategory(src):
    POICategoryDict = {}
    for line in open(src):
        line = line.strip()
        line = line.split('\t')
        POICategoryDict.update({unicode(line[0],'utf-8'):line[2]})
    
    return POICategoryDict    

def AddPOICharacteristicsFrom4sq(clusteringLabelDict, POICategory, setting4sq):
    POIDict = {}
    choiceSetDict = {}
    Client_id = setting4sq[0]
    Client_secret = setting4sq[1]
    
    for cluster in clusteringLabelDict.keys():
        clusterLat = clusteringLabelDict[cluster][0]
        clusterLon = clusteringLabelDict[cluster][1]
        
        placeDict = foursquare_API.request_4sq(clusterLat, clusterLon, Client_id, Client_secret)
        clusterchoiceSetDict = {}
        
        if len(placeDict.keys()) > 10:
            itr = 0
            for place in sorted(placeDict.keys()):
                try:
                    POICategory[placeDict[place]["category"]]
                    (POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance) = (placeDict[place]["name"], POICategory[placeDict[place]["category"]], placeDict[place]["category"], placeDict[place]["lat"], placeDict[place]["lon"], placeDict[place]["distance"])
                    clusterchoiceSetDict.update({itr:[POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance]})
                    itr += 1
                except KeyError:
                    (POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance) = (placeDict[place]["name"], u"専門その他", u"不明", placeDict[place]["lat"], placeDict[place]["lon"], placeDict[place]["distance"])
                    clusterchoiceSetDict.update({itr:[POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance]})
                    itr += 1
                if itr == 10:
                    break
        else:
            itr = 0
            for place in sorted(placeDict.keys()):
                try:
                    POICategory[placeDict[place]["category"]]
                    (POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance) = (placeDict[place]["name"], POICategory[placeDict[place]["category"]], placeDict[place]["category"], placeDict[place]["lat"], placeDict[place]["lon"], placeDict[place]["distance"])
                    clusterchoiceSetDict.update({itr:[POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance]})
                    itr += 1
                except KeyError:
                    (POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance) = (placeDict[place]["name"], u"専門その他", u"不明", placeDict[place]["lat"], placeDict[place]["lon"], placeDict[place]["distance"])
                    clusterchoiceSetDict.update({itr:[POIName, POIcategory, POIsubcategory, POILat, POILon, POIDistance]})
                    itr += 1
        
        try:
            clusterPOIName = clusterchoiceSetDict[0][0]
            clusterPOIcategory = clusterchoiceSetDict[0][1]
            clusterPOILat = clusterchoiceSetDict[0][3]
            clusterPOILon = clusterchoiceSetDict[0][4]
        except KeyError:
            clusterPOIName = u"不明"
            clusterPOIcategory = u"専門その他"
            clusterPOILat = 0
            clusterPOILon = 0
        stayTimeWindow = [0]*288
        
        #print cluster, clusterLat, clusterLon, POIName, POIcategory, POILat, POILon
        POIDict.update({cluster:[clusterPOIName, clusterPOIcategory, clusterPOILat, clusterPOILon, stayTimeWindow, 0, 0]})
        choiceSetDict.update({clusterPOIName:clusterchoiceSetDict})
    
    return POIDict, choiceSetDict

def IdentifyHomeWorkPlace(UserTripData, POIDict, clusteringLabelDict, NumOfDayData):
    
    ###Destination Nameの名寄せ
    DestinationNameDict = {}
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            ID1 = UserTripData[datadate][tripID].OriginPlaceID
            UserTripData[datadate][tripID].OriginPlacePOI = POIDict[ID1][0]
            UserTripData[datadate][tripID].OriginPlaceCategory = POIDict[ID1][1]
            Name1 = UserTripData[datadate][tripID].OriginPlacePOI
            
            ID2 = UserTripData[datadate][tripID].DestinationPlaceID
            UserTripData[datadate][tripID].DestinationPlacePOI = POIDict[ID2][0]
            UserTripData[datadate][tripID].DestinationPlaceCategory = POIDict[ID2][1]
            Name2 = UserTripData[datadate][tripID].DestinationPlacePOI
            
            if Name1 != u"不明":
                try:
                    DestinationNameDict[Name1]
                    if ID1 not in DestinationNameDict[Name1]:
                        DestinationNameDict[Name1].append(ID1)
                except KeyError:
                    DestinationNameDict.update({Name1:[ID1]})
            
            if Name2 != u"不明":
                try:
                    DestinationNameDict[Name2]
                    if ID2 not in DestinationNameDict[Name2]:
                        DestinationNameDict[Name2].append(ID2)
                except KeyError:
                    DestinationNameDict.update({Name2:[ID2]})
    
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            Name1 = UserTripData[datadate][tripID].OriginPlacePOI
            if Name1 != u"不明":
                UserTripData[datadate][tripID].OriginPlaceID = sorted(DestinationNameDict[Name1])[0]
            Name2 = UserTripData[datadate][tripID].DestinationPlacePOI
            if Name2 != u"不明":
                UserTripData[datadate][tripID].DestinationPlaceID = sorted(DestinationNameDict[Name2])[0]
    
    standardTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
    stayStartTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
    
    itr = 0
    stayStartPlaceID = 0
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            if itr > 1:
                stayEndTime = UserTripData[datadate][tripID].TripStartTimestamp
                stayEndPlaceID = UserTripData[datadate][tripID].OriginPlaceID
                stayTime = (stayEndTime - stayStartTime).seconds
                if stayTime <= 86400 and stayStartPlaceID == stayEndPlaceID:
                    startTimeWindow = (stayStartTime - standardTime).seconds/300
                    endTimeWindow = (stayEndTime - standardTime).seconds/300
                    if endTimeWindow >= startTimeWindow and endTimeWindow <= 288:
                        for i in range(startTimeWindow, (endTimeWindow+1)):
                            POIDict[stayStartPlaceID][4][i] += 1
                    elif endTimeWindow >= startTimeWindow and endTimeWindow == 288:
                        for i in range(startTimeWindow, endTimeWindow):
                            POIDict[stayStartPlaceID][4][i] += 1
                        POIDict[stayStartPlaceID][4][0] += 1
                    elif endTimeWindow < startTimeWindow:
                        for i in range(startTimeWindow, 288):
                            POIDict[stayStartPlaceID][4][i] += 1
                        for i in range(0, (endTimeWindow+1)):
                            POIDict[stayStartPlaceID][4][i] += 1
                elif stayTime <= 86400 and stayStartPlaceID != stayEndPlaceID:
                    startTimeWindow = (stayStartTime - standardTime).seconds/300
                    endTimeWindow = (stayEndTime - standardTime).seconds/300
                    if endTimeWindow >= startTimeWindow and endTimeWindow <= 288:
                        for i in range(startTimeWindow, (endTimeWindow+1)):
                            POIDict[stayStartPlaceID][4][i] += 0.5
                    elif endTimeWindow >= startTimeWindow and endTimeWindow == 288:
                        for i in range(startTimeWindow, endTimeWindow):
                            POIDict[stayStartPlaceID][4][i] += 0.5
                        POIDict[stayStartPlaceID][4][0] += 0.5
                    elif endTimeWindow < startTimeWindow:
                        for i in range(startTimeWindow, 288):
                            POIDict[stayStartPlaceID][4][i] += 0.5
                        for i in range(0, (endTimeWindow+1)):
                            POIDict[stayStartPlaceID][4][i] += 0.5
            
            stayStartTime = UserTripData[datadate][tripID].TripEndTimestamp
            stayStartPlaceID = UserTripData[datadate][tripID].DestinationPlaceID
            itr += 1
    
    dayTimePOIDict = {}
    nightTimePOIDict = {}
    for poi in POIDict.keys():
        dayTimePOIDict.update({poi:sum(POIDict[poi][4][132:204])})
        nightTimePOIDict.update({poi:sum(POIDict[poi][4][264:288]) + sum(POIDict[poi][4][0:72])})
        POIDict[poi][5] = sum(POIDict[poi][4][132:204])
        POIDict[poi][6] = sum(POIDict[poi][4][264:288]) + sum(POIDict[poi][4][0:72])
    
    
    homeIDList = []
    workIDList = []
    for key, value in sorted(nightTimePOIDict.items(), key=lambda x:x[1], reverse=True):
        homePOI = key
        if value/96 > NumOfDayData*0.1:
            homeIDList.append(homePOI)
        else:
            break
    for key, value in sorted(dayTimePOIDict.items(), key=lambda x:x[1], reverse=True):
        workPOI = key
        if value/72 > NumOfDayData*0.1:
            workIDList.append(workPOI)
        else:
            break
    
    for homeID in homeIDList:
        POIDict[homeID][0] = "home"
        POIDict[homeID][1] = "home"
        homeLat = clusteringLabelDict[homeID][0]
        homeLon = clusteringLabelDict[homeID][1]
        POIDict[homeID][2] = homeLat
        POIDict[homeID][3] = homeLon
        
        for cluster in clusteringLabelDict.keys():
            clusterLat = clusteringLabelDict[cluster][0]
            clusterLon = clusteringLabelDict[cluster][1]
            distance = LatLonCalc.CalcDistance(homeLat, homeLon, clusterLat, clusterLon)
            if cluster != homeID and distance < 300:
                POIDict[cluster][0] = "home"
                POIDict[cluster][1] = "home"
                POIDict[cluster][2] = clusterLat
                POIDict[cluster][3] = clusterLon
        
    for workID in workIDList:
        POIDict[workID][1] = "work"
        workLat = clusteringLabelDict[workID][0]
        workLon = clusteringLabelDict[workID][1]
        POIDict[workID][2] = workLat
        POIDict[workID][3] = workLon
        
        for cluster in clusteringLabelDict.keys():
            clusterLat = clusteringLabelDict[cluster][0]
            clusterLon = clusteringLabelDict[cluster][1]
            distance = LatLonCalc.CalcDistance(workLat, workLon, clusterLat, clusterLon)
            if cluster != workID and distance < 300 and POIDict[cluster][1] != "home" and POIDict[cluster][1] != "work":
                POIDict[cluster][1] = "work"
                POIDict[cluster][2] = clusterLat
                POIDict[cluster][3] = clusterLon   
    
    #格納
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            ID1 = UserTripData[datadate][tripID].OriginPlaceID
            UserTripData[datadate][tripID].OriginPlacePOI = POIDict[ID1][0]
            UserTripData[datadate][tripID].OriginPlaceCategory = POIDict[ID1][1]
            UserTripData[datadate][tripID].OriginPlaceLat = POIDict[ID1][2]
            UserTripData[datadate][tripID].OriginPlaceLon = POIDict[ID1][3]
            
            ID2 = UserTripData[datadate][tripID].DestinationPlaceID
            UserTripData[datadate][tripID].DestinationPlacePOI = POIDict[ID2][0]
            UserTripData[datadate][tripID].DestinationPlaceCategory = POIDict[ID2][1]
            UserTripData[datadate][tripID].DestinationPlaceLat = POIDict[ID2][2]
            UserTripData[datadate][tripID].DestinationPlaceLon = POIDict[ID2][3]
            
            
            
    return (UserTripData, POIDict)
    
def WriteTripData(UserTripData, choiceSetDict, outputPATH, outputFileName):
    
    dst = outputPATH + outputFileName + "_tripdata.csv"
    fo = open(dst, 'w')
    for datadate in sorted(UserTripData.keys()):
        for tripID in UserTripData[datadate].keys():
            outputList = [UserTripData[datadate][tripID].TripStartTimestamp, UserTripData[datadate][tripID].OriginPlacePOI, UserTripData[datadate][tripID].OriginPlaceCategory, UserTripData[datadate][tripID].OriginPlaceLat, UserTripData[datadate][tripID].OriginPlaceLon, UserTripData[datadate][tripID].TripEndTimestamp, UserTripData[datadate][tripID].DestinationPlacePOI, UserTripData[datadate][tripID].DestinationPlaceCategory, UserTripData[datadate][tripID].DestinationPlaceLat, UserTripData[datadate][tripID].DestinationPlaceLon]
            """
            try:
                for choice in choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI].keys():
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][0])
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][1])
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][2])
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][3])
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][4])
                    outputList.append(choiceSetDict[UserTripData[datadate][tripID].DestinationPlacePOI][choice][5])
            except KeyError:
                pass
            """
            output(fo, outputList)
    fo.close()