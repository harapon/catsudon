#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import matplotlib.pyplot as plt

def TripTimeWindowAnalysis(UserTripData):
    
    TripTimeWindow = []
    for i in range(288):
        TripTimeWindow.append(0)
    
    standardTime = datetime.datetime(2000, 1, 1, 0, 0, 0)
    for datadate in sorted(UserTripData.keys()):
        for tripID in UserTripData[datadate].keys():
            tripStartTimeWindow = (UserTripData[datadate][tripID].TripStartTimestamp - standardTime).seconds/300
            tripEndTimeWindow = (UserTripData[datadate][tripID].TripEndTimestamp - standardTime).seconds/300
            if tripStartTimeWindow == tripEndTimeWindow:
                pass
            else:
                if tripEndTimeWindow > tripStartTimeWindow:
                    for i in range(tripStartTimeWindow, tripEndTimeWindow):
                        TripTimeWindow[i] += 1
                else:
                    for i in range(tripStartTimeWindow, 288):
                        TripTimeWindow[i] += 1
                    for i in range(0, tripEndTimeWindow):
                        TripTimeWindow[i] += 1
    return TripTimeWindow

def VidualizeTripTimeWindowHistgram(TripTimeWindow, outputFolder, filename):
    timeList = []
    for i in range(288):
        timeList.append(i)
    timeList2 = []
    for i in range(288):
        if i%12 == 0:
            timeList2.append(str(i/12))
        else:
            timeList2.append("")
    
    TripTimeWindow2 = TripTimeWindow[48:] + TripTimeWindow[0:48]
    timeList3 = timeList2[48:] + timeList2[0:48]
    
    plt.figure(figsize=(16, 10))
    plt.plot(timeList, TripTimeWindow2, color="black", linewidth=2)
    plt.xticks(timeList, timeList3)
    plt.savefig(outputFolder + str(filename) + '_triptimeofday.png')
    plt.close()
    