#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import LatLonCalc

class trajectoryDotData:
    def __init__(self, timestamp,lat, lon, timediff, distancediff, velocity, state, nearestNode):
        self.timestamp = timestamp
        self.lat = lat
        self.lon = lon
        self.timediff = timediff
        self.distancediff = distancediff
        self.velocity = velocity
        self.state = state
        self.nearestNode = nearestNode

class tripData:
    def __init__(self, tripDate, tripID, 
                 TripStartTimestamp, TripEndTimestamp, TripDuration, TripDistance, TripAverageVelocity,
                 OriginPlaceID, OriginPlacePOI, OriginPlaceCategory, OriginPlaceLat, OriginPlaceLon,
                 DestinationPlaceID, DestinationPlacePOI, DestinationPlaceCategory, DestinationPlaceLat, DestinationPlaceLon,
                 TimestampSequence, LatSequence, LonSequence, NodeSequence
                 ):
        self.tripDate = tripDate
        self.tripID = tripID
        self.TripStartTimestamp = TripStartTimestamp
        self.TripEndTimestamp = TripEndTimestamp
        self.TripDuration = TripDuration
        self.TripDistance = TripDistance
        self.TripAverageVelocity = TripAverageVelocity
        self.OriginPlaceID = OriginPlaceID
        self.OriginPlacePOI = OriginPlacePOI
        self.OriginPlaceCategory = OriginPlaceCategory
        self.OriginPlaceLat = OriginPlaceLat
        self.OriginPlaceLon = OriginPlaceLon
        self.DestinationPlaceID = DestinationPlaceID
        self.DestinationPlacePOI = DestinationPlacePOI
        self.DestinationPlaceCategory = DestinationPlaceCategory
        self.DestinationPlaceLat = DestinationPlaceLat
        self.DestinationPlaceLon = DestinationPlaceLon
        self.TimestampSequence = TimestampSequence
        self.LatSequence = LatSequence
        self.LonSequence = LonSequence
        self.NodeSequence = NodeSequence

class stayData:
    def __init__(self, tripDate, tripID, 
                 TripStartTimestamp, TripEndTimestamp, TripDuration, TripDistance, TripAverageVelocity,
                 OriginPlaceID, OriginPlacePOI, OriginPlaceCategory, OriginPlaceLat, OriginPlaceLon,
                 DestinationPlaceID, DestinationPlacePOI, DestinationPlaceCategory, DestinationPlaceLat, DestinationPlaceLon,
                 LatSequence, LonSequence
                 ):
        self.tripDate = tripDate

def MakeTrajectoryDataPerDay(src):
    itr = 0
    preTimestamp = 0
    preLat = 0
    preLon = 0
    UserData = {}
    for line in open(src):
        line = line.strip()
        line = line.split("\t")
        timestamp = line[0]#line[1]
        lat = line[1]#line[3]
        lon = line[2]#line[4]
        
        year = int(timestamp[0:4])
        month = int(timestamp[4:6])
        day = int(timestamp[6:8])
        hour = int(timestamp[9:11])
        minute = int(timestamp[11:13])
        second = int(timestamp[13:15])
        
        timestamp = datetime.datetime(year, month, day, hour, minute, second)
        basedate = datetime.datetime(year, month, day, 4, 0, 0)
        if (timestamp - basedate).total_seconds() >= 0:
            datadate = str(timestamp.date())
        else:
            t2 = timestamp - datetime.timedelta(days=1)
            datadate = str(t2.date())
        
        if timestamp == preTimestamp:
            pass
        else:
            if itr == 0:
                timediff = 0
                distancediff = 0
                velocity = 0
            else:
                timediff = (timestamp - preTimestamp).total_seconds()
                distancediff = LatLonCalc.CalcDistance(lat, lon, preLat, preLon)
                velocity = (distancediff/1000)/(timediff/3600)
        
            try:
                UserData[datadate].update({timestamp:trajectoryDotData(timestamp, lat, lon, timediff, distancediff, velocity, 0, 0)})
                itr += 1
            except KeyError:
                UserData.update({datadate:{}})
                UserData[datadate].update({timestamp:trajectoryDotData(timestamp, lat, lon, timediff, distancediff, velocity, 0, 0)})
                itr += 1
        
        preTimestamp = timestamp
        preLat = lat
        preLon = lon
    return (UserData)

def MakeTripDataPerDay(UserData):
    #初期設定
    ChangeNum = 0
    preState = 0
    for day in sorted(UserData.keys()):
        for timestamp in sorted(UserData[day].keys()):
            if (UserData[day][timestamp].velocity >= 3 and UserData[day][timestamp].distancediff >= 30) or UserData[day][timestamp].distancediff >= 500:
                UserData[day][timestamp].state = 1
            if UserData[day][timestamp].state != preState:
                ChangeNum += 1
            preState = UserData[day][timestamp].state
    
    #挟み込み処理
    for day in sorted(UserData.keys()):
        for i in range(len(UserData[day].keys())-1):
            try:
                UserData[day][sorted(UserData[day].keys())[i-1]].state, UserData[day][sorted(UserData[day].keys())[i]].state, UserData[day][sorted(UserData[day].keys())[i+1]].state
                if UserData[day][sorted(UserData[day].keys())[i-1]].state == 1 and UserData[day][sorted(UserData[day].keys())[i]].state == 0 and UserData[day][sorted(UserData[day].keys())[i+1]].state == 1 and UserData[day][sorted(UserData[day].keys())[i]].timediff <= 300 and UserData[day][sorted(UserData[day].keys())[i+1]].timediff <= 300:
                    UserData[day][sorted(UserData[day].keys())[i]].state = 1
            except KeyError:
                pass
            except IndexError:
                pass
    
    for day in sorted(UserData.keys()):
        for i in range(len(UserData[day].keys())-1):
            try:
                UserData[day][sorted(UserData[day].keys())[i-1]].state, UserData[day][sorted(UserData[day].keys())[i]].state, UserData[day][sorted(UserData[day].keys())[i+1]].state
                if UserData[day][sorted(UserData[day].keys())[i-1]].state == 0 and UserData[day][sorted(UserData[day].keys())[i]].state == 1 and UserData[day][sorted(UserData[day].keys())[i+1]].state == 0 and UserData[day][sorted(UserData[day].keys())[i]].timediff <= 300 and UserData[day][sorted(UserData[day].keys())[i+1]].timediff <= 300:
                    UserData[day][sorted(UserData[day].keys())[i]].state = 0
            except KeyError:
                pass
            except IndexError:
                pass
    
    ChangeNum = 0
    preState = 0
    for day in sorted(UserData.keys()):
        for timestamp in sorted(UserData[day].keys()):
            if UserData[day][timestamp].state != preState:
                ChangeNum += 1
            preState = UserData[day][timestamp].state
    
    tripID = 0
    preTimestamp = 0
    initialTripDict = {}
    tripList = []
    for day in sorted(UserData.keys()):
        for timestamp in sorted(UserData[day].keys()):
            if UserData[day][timestamp].state == 1:
                if len(tripList) == 0:
                    tripList.append(UserData[day][timestamp])
                    preTimestamp = UserData[day][timestamp].timestamp
                else:
                    if (UserData[day][timestamp].timestamp - preTimestamp).total_seconds() <= 900:
                        tripList.append(UserData[day][timestamp])
                        preTimestamp = UserData[day][timestamp].timestamp
                    else:
                        if len(tripList) >= 2:
                            triptimediff = (tripList[-1].timestamp - tripList[0].timestamp).total_seconds()/60
                            tripdistancediff = LatLonCalc.CalcDistance(tripList[0].lat, tripList[0].lon, tripList[-1].lat, tripList[-1].lon)/1000
                            
                            if triptimediff >= 5 and tripdistancediff >= 0.5:
                                initialTripDict.update({tripID:tripList})
                                tripID += 1
                        else:
                            initialTripDict.update({tripID:tripList})
                            tripID += 1
                        tripList = [UserData[day][timestamp]]
                        preTimestamp = UserData[day][timestamp].timestamp
    
    preLat = 0
    preLon = 0
    for tripID in initialTripDict.keys():
        if len(initialTripDict[tripID]) > 1:
            preLat = initialTripDict[tripID][-1].lat
            preLon = initialTripDict[tripID][-1].lon
        if len(initialTripDict[tripID])==1:
            if LatLonCalc.CalcDistance(initialTripDict[tripID][0].lat, initialTripDict[tripID][0].lon, preLat, preLon) >= 500:
                preTimestamp = initialTripDict[tripID][0].timestamp - datetime.timedelta(minutes=5)
                first = trajectoryDotData(preTimestamp, preLat, preLon, 0, 0, 0, 1, 0)
                second = initialTripDict[tripID][0]
                initialTripDict.update({tripID:[first, second]})
            else:
                preLat = initialTripDict[tripID][0].lat
                preLon = initialTripDict[tripID][0].lon
                del initialTripDict[tripID]
    
    UserTripData = {}
    for tripID in initialTripDict.keys():
        tripDate = initialTripDict[tripID][0].timestamp.date()
        TripStartTimestamp = initialTripDict[tripID][0].timestamp
        TripEndTimestamp = initialTripDict[tripID][-1].timestamp
        TripDuration = (TripEndTimestamp - TripStartTimestamp).total_seconds()
        TripDistance = LatLonCalc.CalcDistance(initialTripDict[tripID][0].lat, initialTripDict[tripID][0].lon, initialTripDict[tripID][-1].lat, initialTripDict[tripID][-1].lon)
        TripAverageVelocity = (TripDistance/1000)/(TripDuration/3600)
        OriginPlaceID = 0
        OriginPlacePOI = ""
        OriginPlaceCategory = ""
        OriginPlaceLat = initialTripDict[tripID][0].lat
        OriginPlaceLon = initialTripDict[tripID][0].lon
        DestinationPlaceID = 0
        DestinationPlacePOI = ""
        DestinationPlaceCategory = ""
        DestinationPlaceLat = initialTripDict[tripID][-1].lat
        DestinationPlaceLon = initialTripDict[tripID][-1].lon
        
        TimestampSequence = []
        LatSequence = []
        LonSequence = []
        NodeSequence = []
        
        if len(initialTripDict[tripID]) > 2:
            for i in range(1,len(initialTripDict[tripID])):
                TimestampSequence.append(initialTripDict[tripID][i].timestamp)
                LatSequence.append(initialTripDict[tripID][i].lat)
                LonSequence.append(initialTripDict[tripID][i].lon)
        
        trip = tripData(tripDate, tripID, 
                 TripStartTimestamp, TripEndTimestamp, TripDuration, TripDistance, TripAverageVelocity,
                 OriginPlaceID, OriginPlacePOI, OriginPlaceCategory, OriginPlaceLat, OriginPlaceLon,
                 DestinationPlaceID, DestinationPlacePOI, DestinationPlaceCategory, DestinationPlaceLat, DestinationPlaceLon,
                 TimestampSequence, LatSequence, LonSequence, NodeSequence)
        
        try:
            UserTripData[tripDate].update({tripID:trip})
        except KeyError:
            UserTripData.update({tripDate:{}})
            UserTripData[tripDate].update({tripID:trip})
    
    return UserTripData
        
        
        
def ReadUserTrajectoryData(src):
    itr = 0
    UserData = {}
    for line in open(src):
        line = line.strip()
        line = line.split("\t")
        timestamp = line[0]
        lat = line[1]
        lon = line[2]
        
        year = int(timestamp[0:4])
        month = int(timestamp[4:6])
        day = int(timestamp[6:8])
        hour = int(timestamp[9:11])
        minute = int(timestamp[11:13])
        second = int(timestamp[13:15])
        
        timestamp = datetime.datetime(year, month, day, hour, minute, second)
        basedate = datetime.datetime(year, month, day, 4, 0, 0)
        if (timestamp - basedate).total_seconds() >= 0:
            datadate = str(timestamp.date())
        else:
            t2 = timestamp - datetime.timedelta(days=1)
            datadate = str(t2.date())
        
        try:
            UserData[datadate].update({timestamp:trajectoryDotData(timestamp, lat, lon, 0)})
            itr += 1
        except KeyError:
            UserData.update({datadate:{}})
            UserData[datadate].update({timestamp:trajectoryDotData(timestamp, lat, lon, 0)})
            itr += 1
    
    UserTripData = {}
    for datadate in sorted(UserData.keys()):
        itr = 0
        stateDict = {}
        stateItr = 0
        for t in sorted(UserData[datadate]):
            if itr == 0:
                #print datadate, UserData[datadate][t].timestamp, 0, 0, "move"
                stateDict.update({stateItr:["move", UserData[datadate][t]]})
                preLat = UserData[datadate][t].lat
                preLon = UserData[datadate][t].lon
                preTimestamp = UserData[datadate][t].timestamp
                preState = "move"
            else:
                distanceDiff = LatLonCalc.CalcDistance(UserData[datadate][t].lat, UserData[datadate][t].lon, preLat, preLon)
                timeDiff = (UserData[datadate][t].timestamp - preTimestamp).total_seconds()
                velocity = (distanceDiff/1000)/(timeDiff/3600)
                if distanceDiff >= 150 or (distanceDiff >= 10 and velocity >= 4):
                    state = "move"
                else:
                    state = "stay"
                
                if preState == state:
                    try:
                        stateDict[stateItr].append(UserData[datadate][t])
                    except KeyError:
                        stateDict.update({stateItr:[state, UserData[datadate][t]]})
                else:
                    stateItr += 1
                    stateDict.update({stateItr:[state, UserData[datadate][t]]})
                preLat = UserData[datadate][t].lat
                preLon = UserData[datadate][t].lon
                preTimestamp = UserData[datadate][t].timestamp
                preState = state
            itr += 1
        
        preLastTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
        for stateItr in stateDict.keys():
            NumDot = len(stateDict[stateItr]) - 1
            distanceDiff = LatLonCalc.CalcDistance(stateDict[stateItr][1].lat, stateDict[stateItr][1].lon, stateDict[stateItr][-1].lat, stateDict[stateItr][-1].lon)
            timeDiff = (stateDict[stateItr][-1].timestamp - stateDict[stateItr][1].timestamp).total_seconds()
            
            if stateDict[stateItr][0] == "stay" and (stateDict[stateItr][1].timestamp - preLastTime).total_seconds() <= 90:
                for dot in stateDict[stateItr][1:]:
                    stateDict[stateItr-1].append(dot)
            preLastTime = stateDict[stateItr][-1].timestamp
        
        moveItr = 0
        tripDict = {}
        for stateItr in stateDict.keys():
            if stateDict[stateItr][0] == "move":
                if moveItr != 0:
                    timeDiff = (stateDict[stateItr][1].timestamp - preLastTime).total_seconds()
                    preLastTime = stateDict[stateItr][-1].timestamp
                    if timeDiff <= 200:
                        for dot in stateDict[stateItr][1:]:
                            tripDict[moveItr-1].append(dot)
                    else:
                        if len(stateDict[stateItr][1:]) == 1:
                            for dot in stateDict[stateItr][1:]:
                                tripDict[moveItr-1].append(dot)
                        else:
                            tripDict.update({moveItr:stateDict[stateItr][1:]})
                            moveItr += 1
                else:
                    tripDict.update({moveItr:stateDict[stateItr][1:]})
                    preLastTime = tripDict[moveItr][-1].timestamp
                    moveItr += 1
        if len(tripDict.keys()) > 0:
            UserTripData.update({datadate:tripDict})
       
    return UserTripData