#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import time
import datetime
import math
import os
import gc
import random

import numpy as np
from multiprocessing import Pool
from multiprocessing import Process


import ReadTrajectoryFile
import AreaMesh
import LatLonCalc
import foursquare_API
import TripTimeInDay
import DestinationAnalysis
import MeshKMeans
import MapMatchingEachDay
import GoogleEarthKML


def output(fo, outputList):
    text = ""
    for i in range(len(outputList)-1):
        text = text + str(outputList[i]) + "\t"
    text = text + str(outputList[len(outputList)-1]) + "\n"
    fo.write(text)

def outputCSV(fo, outputList):
    text = ""
    for i in range(len(outputList)-1):
        text = text + str(outputList[i]) + ","
    text = text + str(outputList[len(outputList)-1]) + "\n"
    fo.write(text)

def read4sqSetting(settingPATH):
    src = settingPATH + "4sq_setting.txt"
    settingList = []
    for line in open(src):
        line = line.strip()
        settingList.append(line)
    return settingList

if __name__ == '__main__':
    
    param = sys.argv
    try:
        filename = param[1]
    except IndexError:
        fileName = "testdata.tsv"
    
    
    print param
    
    CatsudonDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    
    networkDataPATH = CatsudonDirectory + "/networkSrc/"
    inputPATH = CatsudonDirectory + "/input/"
    outputPATH = CatsudonDirectory + "/output/"
    settingPATH = CatsudonDirectory + "/setting/"
    setting4sq = read4sqSetting(settingPATH)
    
    t0 = time.time()
    src = inputPATH + fileName
    outputfilename = fileName.split('.')[0]
    outputFileName2 = outputfilename + "_tripdata.csv"
        
    UserData = ReadTrajectoryFile.MakeTrajectoryDataPerDay(src)
    UserTripData = ReadTrajectoryFile.MakeTripDataPerDay(UserData)
    NumOfDayData = len(UserTripData.keys())
    print outputfilename, str(NumOfDayData) + "days data"
    
    ### Trip時間の処理
    TripTimeWindow = TripTimeInDay.TripTimeWindowAnalysis(UserTripData)
    NumOfTrip = sum(TripTimeWindow)
    TripTimeInDay.VidualizeTripTimeWindowHistgram([float(x)/NumOfTrip for x in TripTimeWindow], outputPATH, outputfilename)
    
    ### Origin, Destinationのクラスタリング
    (DestinationData, NumOfDestinationsAll) = DestinationAnalysis.MakeDestinationDataforClustering(UserTripData)
    NumOfCanopy = DestinationAnalysis.CalcNumOfCanopy(UserTripData, T1=500, T2=300)
    (UserTripData, clusteringLabelDict) = DestinationAnalysis.DestinationKMeans(DestinationData, UserTripData, K=NumOfCanopy)
    
    categoryFilePATH = settingPATH + "foursquare_category_all.tsv"
    POICategory = DestinationAnalysis.ReadPOICategory(categoryFilePATH)
    (POIDict, choiceSetDict) = DestinationAnalysis.AddPOICharacteristicsFrom4sq(clusteringLabelDict, POICategory, setting4sq)
    (UserTripData, POIDict) = DestinationAnalysis.IdentifyHomeWorkPlace(UserTripData, POIDict, clusteringLabelDict, NumOfDayData)
    
    DestinationAnalysis.WriteTripData(UserTripData, choiceSetDict, outputPATH, outputfilename)
    
    POIGroupeList = ["home", "work", u"フード", u"店舗サービス", u"芸術娯楽", u"旅行交通", u"アウトドアレクリエーション", 
                    u"イベント", u"カレッジ大学", u"ナイトスポット", u"専門その他", u"住宅"]
    
    #count dataの作成
    dst = outputPATH + outputfilename + "_activity.csv"
    fo = open(dst, 'w')
    POIGroupeStayDict = {}
    for poiGroupe in POIGroupeList:
        POIGroupeStayDict.update({poiGroupe:[0]*288})
        for poi in POIDict.keys():
            if POIDict[poi][1] == poiGroupe:
                for i in range(288):
                    POIGroupeStayDict[poiGroupe][i] += POIDict[poi][4][i]
        outputList = POIGroupeStayDict[poiGroupe]
        outputCSV(fo, outputList)
    fo.close()
    
    t0 = time.time()
    # 以降の処理の高速化のため，類似する日をKmeansでクラスタリング (前処理)
    AllSecondMeshList = AreaMesh.MakeAllSecondMeshList(UserTripData)
    MeshData = MeshKMeans.MakeMeshDataForClusteringDays(UserTripData)
    ClusterDataDate = MeshKMeans.ClusteringDaysData(MeshData, UserTripData, K=10)
    
    PathLinkDict = {}
    outputPATH2 = outputPATH + "path/"
    try:
        os.makedirs(outputPATH2)
    except OSError:
        pass
    
    # クラスターごとに各トリップのマップマッチング
    for cluster in ClusterDataDate.keys():
        t1 = time.time()
        UserTripDataOfCluster = MapMatchingEachDay.MakeUserTripDataOfCluster(UserTripData, ClusterDataDate, cluster)
        AllSecondMeshListOfCluster = AreaMesh.MakeAllSecondMeshList(UserTripDataOfCluster)
        
        NetworkDataOfCluster = MapMatchingEachDay.ReadOSM_NetworkData(AllSecondMeshListOfCluster, networkDataPATH)
        UserTripDataOfCluster = MapMatchingEachDay.ConvertDotToNetworkNode(UserTripDataOfCluster, NetworkDataOfCluster)
        
        (G, NodeToLinkIDDict, LinkDict) = MapMatchingEachDay.MakeGraphStructure(NetworkDataOfCluster)
        
        TripPathDataOfCluster = MapMatchingEachDay.MakeTripPathData(UserTripDataOfCluster, G, NodeToLinkIDDict, outputPATH2, outputfilename)
        for linkID in TripPathDataOfCluster.keys():
            try:
                PathLinkDict[linkID] += TripPathDataOfCluster[linkID]
            except KeyError:
                PathLinkDict.update({linkID:TripPathDataOfCluster[linkID]})
        t2 = time.time()
        #print cluster, str(len(ClusterDataDate[cluster]))+"days", str(len(AllSecondMeshListOfCluster))+"mesh", t2-t1
        del TripPathDataOfCluster, AllSecondMeshListOfCluster, NetworkDataOfCluster, G, NodeToLinkIDDict, LinkDict
        gc.collect()
    
    t7 = time.time()
    print u"finished", t7-t0
    
    #kmlで出力
    (LinkThresholdList, AllSecondMeshList) = GoogleEarthKML.WritePathLinkData(PathLinkDict, outputPATH, outputfilename)
    LinkDict = GoogleEarthKML.ReadPathLatLonData(PathLinkDict, AllSecondMeshList, networkDataPATH)
    GoogleEarthKML.WriteGoogleEarthKML(PathLinkDict, LinkDict, LinkThresholdList, outputPATH, outputfilename)
    t8 = time.time()
    print u"finished", t8 - t0
    
