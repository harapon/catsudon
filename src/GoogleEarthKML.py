#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def outputCSV(fo, outputList):
    text = ""
    for i in range(len(outputList)-1):
        text = text + str(outputList[i]) + ","
    text = text + str(outputList[len(outputList)-1]) + "\n"
    fo.write(text)

def DecideColor(value, thresholdList):
    colorList = ["0000FF", "008CFF", "00FFFF", "32CD32", "EBCE87"]
    for i in range(5):
        if float(value) >= thresholdList[i]:
            color = colorList[i]
            break
    return color

def DecideLineWidth(value, thresholdList):
    widthList = ["5", "4", "3", "2.5", "2"]
    for i in range(5):
        if float(value) >= thresholdList[i]:
            lineWidth = widthList[i]
            break
    return lineWidth

def WritePathLinkData(PathLinkDict, outputPATH, filename):
    NumOfPassedLinks = len(PathLinkDict.keys())
    AllSecondMeshList = []
    NotOneLinks = 0
    dstPath = outputPATH + filename + "_pathall.csv"
    fo = open(dstPath, 'w')
    for linkID, v in sorted(PathLinkDict.items(), key=lambda x:x[1]):
        secondMesh = linkID.split('_')[0]
        if secondMesh not in AllSecondMeshList:
            AllSecondMeshList.append(secondMesh)
        
        outputList = [linkID, v]
        outputCSV(fo, outputList)
        if v != 1:
            NotOneLinks += 1
    fo.close()
    
    OneLinks = NumOfPassedLinks - NotOneLinks
    LinkThreshold = NotOneLinks/4
    LinkThresholdList = [sorted(PathLinkDict.items(), key=lambda x:x[1])[OneLinks + int(LinkThreshold*3.5)][1], 
                         sorted(PathLinkDict.items(), key=lambda x:x[1])[OneLinks + LinkThreshold*3][1], 
                         sorted(PathLinkDict.items(), key=lambda x:x[1])[OneLinks + LinkThreshold*2][1], 
                         sorted(PathLinkDict.items(), key=lambda x:x[1])[OneLinks + LinkThreshold][1], 1]
    return (LinkThresholdList, AllSecondMeshList)

def ReadPathLatLonData(PathLinkDict, AllSecondMeshList, networkDataPATH):
    #ネットワークデータの読み込みと描画用LinkDictの作成
    NetworkData = {}
    LinkDict = {}
    for secondMesh in AllSecondMeshList:
        jsonFile = networkDataPATH + str(secondMesh) + "_RoadLink.json"
        f = open(jsonFile, 'r')
        NetworkData = json.load(f)
        
        for thirdMesh in NetworkData.keys():
            for LinkID in NetworkData[thirdMesh].keys():
                try:
                    PathLinkDict[LinkID]
                    Olat = NetworkData[thirdMesh][LinkID][u"Olat"]
                    Olon = NetworkData[thirdMesh][LinkID][u"Olon"]
                    Dlat = NetworkData[thirdMesh][LinkID][u"Dlat"]
                    Dlon = NetworkData[thirdMesh][LinkID][u"Dlon"]
                    InterNodeLat = NetworkData[thirdMesh][LinkID][u"InterNodeLat"]
                    InterNodeLon = NetworkData[thirdMesh][LinkID][u"InterNodeLon"]
            
                    LatList = [Olat]
                    LonList = [Olon]
                    if len(InterNodeLat) > 0:
                        LatList +=  InterNodeLat
                        LonList +=  InterNodeLon
                    LatList.append(Dlat)
                    LonList.append(Dlon)
                    LinkDict.update({LinkID:[LatList, LonList]})
                except KeyError:
                    pass
        #print secondMesh, len(LinkDict.keys())
    
    return LinkDict
    
def WriteGoogleEarthKML(PathLinkDict, LinkDict, LinkThresholdList, outputPATH, filename):
    
    dst1 = outputPATH + filename + "_path.kml"
    fo = open(dst1, 'w')
    
    fo.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    fo.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
    fo.write("<Document>\n")
    fo.write("\t<name>Trajectory</name>")
    fo.write("\t<open>1</open>")
    
    for LinkID in PathLinkDict.keys():
        value = PathLinkDict[LinkID]
        
        fo.write("\t<Placemark>\n\t\t<name>" + str(LinkID) + "</name>\n")
        fo.write("\t<LineString>\n\t\t\t<extrude>1</extrude>\n\t\t\t<tessellate>1</tessellate>\n")
        fo.write("\t\t\t<coordinates>\n")
        for point in range(len(LinkDict[str(LinkID)][0])):
            fo.write("\t\t" + str(LinkDict[str(LinkID)][1][point]) + "," + str(LinkDict[str(LinkID)][0][point]) + ",0\n")
        fo.write("\t\t\t</coordinates>\n\t\t</LineString>\n")
        fo.write("\t\t<Style>\n \t\t\t<LineStyle>\n")
        fo.write("\t\t\t<color>#FF" + DecideColor(value, LinkThresholdList) + "</color>\n")
        fo.write("\t\t\t<width>" + DecideLineWidth(value, LinkThresholdList) + "</width>\n")
        fo.write("\t\t\t</LineStyle>\n\t\t</Style>\n")  
        fo.write("\t</Placemark>\n")
        
    fo.write("</Document>\n</kml>")
    