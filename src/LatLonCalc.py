#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

def CalcDistance(lat1, lon1, lat2, lon2):
    #ヒュベニの公式で二地点間の距離を算出(m単位)
    lat1 = float(lat1)/180*math.pi
    lon1 = float(lon1)/180*math.pi
    lat2 = float(lat2)/180*math.pi
    lon2 = float(lon2)/180*math.pi

    a = 6378137
    e2 = 0.00669437999019758
    ae = 6335439.32729246

    dy = lat1 - lat2
    dx = lon1 - lon2
    muy = (lat1 + lat2)/2
    W = math.sqrt(1-e2*(math.sin(muy))**2)
    N = a/W
    M = ae/(W**3)
    
    d = math.sqrt((dy * M)**2 + (dx * N * math.cos(muy))**2)
    return d

def TransJpnLatLonWorld(JpnLat, JpnLon):
    JpnLat = float(JpnLat)
    JpnLon = float(JpnLon)
    worldLat = JpnLat - JpnLat * 0.00010695 + JpnLon * 0.000017464 + 0.0046017
    worldLon = JpnLon - JpnLat * 0.000046038 - JpnLon * 0.000083043 + 0.010040
    
    return (worldLat, worldLon)
