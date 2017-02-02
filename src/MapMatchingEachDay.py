#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import networkx as nx

import AreaMesh
import LatLonCalc

def outputCSV(fo, outputList):
    text = ""
    for i in range(len(outputList)-1):
        text = text + str(outputList[i]) + ","
    text = text + str(outputList[len(outputList)-1]) + "\n"
    fo.write(text)
    
def readJsonToNetwork(jsonFile, NetworkData):
    f = open(jsonFile, 'r')
    jsonData = json.load(f)
    
    NetworkData2 = jsonData
    NetworkData.update(NetworkData2)
    return NetworkData

def MakeUserTripDataOfCluster(UserTripData, ClusterDataDate, cluster):
    
    UserTripDataOfCluster = {}
    
    for datadate in UserTripData.keys():
        if datadate in ClusterDataDate[cluster]:
            UserTripDataOfCluster.update({datadate:UserTripData[datadate]})
    
    return UserTripDataOfCluster

def ReadOSM_NetworkData(AllSecondMeshList, networkDataPATH):
    NetworkData = {}
    for secondMesh in AllSecondMeshList:
        jsonFile = networkDataPATH + str(secondMesh) + "_RoadLink.json"
        try:
            NetworkData = readJsonToNetwork(jsonFile, NetworkData)
        except IOError:
            pass
    return NetworkData

def trajectoryDotToNetworkNode(lat, lon, secondMesh, thirdMesh, NetworkData):
    minDis = 999999
    minNode = 0
    
    try:
        for link in NetworkData[thirdMesh].keys():
            if LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"Olat"], NetworkData[thirdMesh][link][u"Olon"]) < minDis:
                minDis = LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"Olat"], NetworkData[thirdMesh][link][u"Olon"])
                minNode = NetworkData[thirdMesh][link][u"OnodeID"]
                for i in range(len(NetworkData[thirdMesh][link][u"InterNodeLat"])):
                    if LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"InterNodeLat"][i], NetworkData[thirdMesh][link][u"InterNodeLon"][i]) < minDis:
                        minDis = LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"InterNodeLat"][i], NetworkData[thirdMesh][link][u"InterNodeLon"][i])
                        if i < float(len(NetworkData[thirdMesh][link][u"InterNodeLat"]))/2:
                            minNode = NetworkData[thirdMesh][link][u"OnodeID"]
                        else:
                            minNode = NetworkData[thirdMesh][link][u"DnodeID"]
            
            if LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"Dlat"], NetworkData[thirdMesh][link][u"Dlon"]) < minDis:
                minDis = LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"Dlat"], NetworkData[thirdMesh][link][u"Dlon"])
                minNode = NetworkData[thirdMesh][link][u"DnodeID"]
                for i in range(len(NetworkData[thirdMesh][link][u"InterNodeLat"])):
                    if LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"InterNodeLat"][i], NetworkData[thirdMesh][link][u"InterNodeLon"][i]) < minDis:
                        minDis = LatLonCalc.CalcDistance(lat, lon, NetworkData[thirdMesh][link][u"InterNodeLat"][i], NetworkData[thirdMesh][link][u"InterNodeLon"][i])
                        if i < float(len(NetworkData[thirdMesh][link][u"InterNodeLat"]))/2:
                            minNode = NetworkData[thirdMesh][link][u"OnodeID"]
                        else:
                            minNode = NetworkData[thirdMesh][link][u"DnodeID"]
    except KeyError:
        minNode = 0
        minDis = 0
    
    return minNode, minDis

def ConvertDotToNetworkNode(UserTripData, NetworkData):
    #trajectory上のドットデータをネットワークノードへ写像
    for datadate in sorted(UserTripData.keys()):
        for tripID in sorted(UserTripData[datadate].keys()):
            NodeList = []
            lat1 = UserTripData[datadate][tripID].OriginPlaceLat
            lon1 = UserTripData[datadate][tripID].OriginPlaceLon
            (secMesh, thiMesh) = AreaMesh.searchAreaMesh(lat1,lon1)
            NodeList.append(trajectoryDotToNetworkNode(lat1, lon1, secMesh, thiMesh, NetworkData)[0])
            
            if len(UserTripData[datadate][tripID].LatSequence) > 0:
                for i in range(len(UserTripData[datadate][tripID].LatSequence)):
                    lat3 = UserTripData[datadate][tripID].LatSequence[i]
                    lon3 = UserTripData[datadate][tripID].LonSequence[i]
                    (secMesh, thiMesh) = AreaMesh.searchAreaMesh(lat3,lon3)
                    NodeList.append(trajectoryDotToNetworkNode(lat3, lon3, secMesh, thiMesh, NetworkData)[0])
            
            lat2 = UserTripData[datadate][tripID].DestinationPlaceLat
            lon2 = UserTripData[datadate][tripID].DestinationPlaceLon
            (secMesh, thiMesh) = AreaMesh.searchAreaMesh(lat2,lon2)
            NodeList.append(trajectoryDotToNetworkNode(lat2, lon2, secMesh, thiMesh, NetworkData)[0])
            
            UserTripData[datadate][tripID].NodeSequence = NodeList
            
    return UserTripData

def MakeGraphStructure(NetworkData):
    ###グラフデータGの格納, 2つのノードIDからリンクIDへの紐付け, LinkDictの作成
    G = nx.DiGraph()
    NodeToLinkIDDict = {}
    LinkDict = {}
    
    for secondMesh in NetworkData.keys():
        for link in NetworkData[secondMesh].keys():
            G.add_weighted_edges_from([(NetworkData[secondMesh][link][u"OnodeID"], NetworkData[secondMesh][link][u"DnodeID"], float(NetworkData[secondMesh][link][u"Length"]))])
            G.add_weighted_edges_from([(NetworkData[secondMesh][link][u"DnodeID"], NetworkData[secondMesh][link][u"OnodeID"], float(NetworkData[secondMesh][link][u"Length"]))])
            
            #2つのノードIDからリンクIDへの紐付け
            LinkID = link
            (OnodeID, DnodeID) = (NetworkData[secondMesh][link][u"OnodeID"], NetworkData[secondMesh][link][u"DnodeID"])
            try:
                NodeToLinkIDDict[OnodeID].update({DnodeID:LinkID})
            except KeyError:
                NodeToLinkIDDict.update({OnodeID:{}})
                NodeToLinkIDDict[OnodeID].update({DnodeID:LinkID})
            try:
                NodeToLinkIDDict[DnodeID].update({OnodeID:LinkID})
            except KeyError:
                NodeToLinkIDDict.update({DnodeID:{}})
                NodeToLinkIDDict[DnodeID].update({OnodeID:LinkID})
            
            #LinkDictの作成
            (Olat, Olon, Dlat, Dlon, InterNodeLat, InterNodeLon) = (NetworkData[secondMesh][link][u"Olat"], NetworkData[secondMesh][link][u"Olon"], 
                                        NetworkData[secondMesh][link][u"Dlat"], NetworkData[secondMesh][link][u"Dlon"], 
                                        NetworkData[secondMesh][link][u"InterNodeLat"], NetworkData[secondMesh][link][u"InterNodeLon"])
            LatList = [Olat]
            LonList = [Olon]
            if len(InterNodeLat) > 0:
                LatList +=  InterNodeLat
                LonList +=  InterNodeLon
            LatList.append(Dlat)
            LonList.append(Dlon)
            LinkDict.update({LinkID:[LatList, LonList]})
            
    return (G, NodeToLinkIDDict, LinkDict)
    
    
def MakeTripPathData(UserTripData, G, NodeToLinkIDDict, outputPATH2, filename):
    
    #データから最短経路探索により経路特定
    PathLinkDict = {}
    itr = 0
    PreNode = 0
    for datadate in sorted(UserTripData.keys()):
        
        dst = outputPATH2 + filename + "_path_" + str(datadate) + ".csv"
        fo = open(dst, 'w')
        for tripID in sorted(UserTripData[datadate].keys()):
            for NowNode in UserTripData[datadate][tripID].NodeSequence:
                PathNodeList = []
                if PreNode != 0 and NowNode != 0 and PreNode != NowNode:
                    try:
                        path = nx.dijkstra_path(G, PreNode, NowNode, 'weight')
                        for j in path:
                            if len(PathNodeList) > 0 and PathNodeList[-1] != j:
                                PathNodeList.append(j)
                            elif len(PathNodeList) == 0:
                                PathNodeList.append(j)
                        
                    except nx.exception.NetworkXNoPath:
                        pass
                
                if len(PathNodeList) >= 2:
                    for node in range(len(PathNodeList)-1):
                        try:
                            LinkID = NodeToLinkIDDict[PathNodeList[node]][PathNodeList[node+1]]
                            outputList = [tripID, UserTripData[datadate][tripID].TripStartTimestamp, UserTripData[datadate][tripID].TripEndTimestamp, LinkID]
                            outputCSV(fo, outputList)
                            
                            try:
                                PathLinkDict[LinkID] += 1
                            except KeyError:
                                PathLinkDict.update({LinkID:1})
                        except KeyError:
                            pass
                    
                PreNode = NowNode
            
        fo.close()
    
    return PathLinkDict
