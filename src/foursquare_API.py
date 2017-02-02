#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2


#Client_id = "1W2BDERGL3GNHLJI0EIWJU55DT54E1YFWBRN0HW0B3AIKFNW"
#Client_secret = "F3OEH5CV2KDQZSCKZ2WCYMKHJ1L0BZ0NPFNP52ANNIJYA2RO"


def request_4sq(lat, lon, Client_id, Client_secret):
    foursq = "https://api.foursquare.com/v2/venues/search?&ll="
    url = foursq + str(lat) + "," + str(lon) + "&client_id=" + Client_id + "&client_secret=" + Client_secret + "&v=20140208&locale=ja"
    
    placeDict = {}
    try:
        f = urllib2.urlopen(url)
        
        data = json.load(f)
        for place in range(len(data["response"]["venues"])):
            distance = data["response"]["venues"][place][u'location'][u'distance']
            placeLat = data["response"]["venues"][place][u'location'][u'lat']
            placeLon = data["response"]["venues"][place][u'location'][u'lng']
            checkinsCount = data["response"]["venues"][place][u'stats'][u'checkinsCount']
            usersCount = data["response"]["venues"][place][u'stats'][u'usersCount']
            placeName = data["response"]["venues"][place]['name']
            placeName = placeName.replace(',', '')
            if len(data["response"]["venues"][place]["categories"]) > 0:
                placeCategory = data["response"]["venues"][place]["categories"][0]["pluralName"]
                placeCategory = placeCategory.replace(',', '')
            else:
                placeCategory = "no-category"
            
            placeDict.update({distance:{"name":placeName, "category":placeCategory, "lat":placeLat, "lon":placeLon, "distance":distance, "checkinsCount":checkinsCount, "usersCount":usersCount}})
                
        
    except urllib2.HTTPError:
        pass
        #print u"HTTP Error"
    
    return placeDict