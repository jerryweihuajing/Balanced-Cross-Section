# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 16:41:55 2018

@author: whj
"""

def isInsidePolygon(pt, poly):
    c = False
    i = -1
    l = len(poly)
    j = l - 1
    while i < l-1:
        i += 1
        #print i,poly[i], j,poly[j]
        #print poly[0]
        if ((poly[i]["lat"] <= pt["lat"] and pt["lat"] < poly[j]["lat"]) or (poly[j]["lat"] <= pt["lat"] and pt["lat"] < poly[i]["lat"])):
            if (pt["lng"] < (poly[j]["lng"] - poly[i]["lng"]) * (pt["lat"] - poly[i]["lat"]) / (poly[j]["lat"] - poly[i]["lat"]) + poly[i]["lng"]):
                c = not c
        j = i
    return c


pt['lat'] = O.bodies[i].state.pos[0]
			pt['lng'] = O.bodies[i].state.pos[2]
			poly = [{'lat':(l*3/18), 'lng':0},{'lat':(l*4/18), 'lng':0},{'lat':(l*7/18), 'lng':sample_h*2/3},{'lat':(l*6/18), 'lng':sample_h*2/3}]
			if isInsidePolygon(pt, poly):