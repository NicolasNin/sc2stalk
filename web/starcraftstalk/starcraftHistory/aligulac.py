# code to interface with aligulac api
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse
from starcraftHistory.models import Progamer
key="K3W7uVs2NCF67DRyg05d"
def getJsonData(url):
    #we change url to avoid unicode problem
    url = urllib.parse.urlsplit(url)
    url=list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    try:
        html=urlopen(url).read()
        return json.loads(html.decode('utf-8'))
    except 	HTTPError as e:
        print ("error",e.reason)
        return ("error",e.reason)

url="http://aligulac.com/api/v1/player/10/?format=json&apikey=K3W7uVs2NCF67DRyg05d"
#print(getJsonData(url))
wcsRegion={"FR":"EU","FI":"EU","KR":"KR","US":"NA","CA":"NA","PL":"EU","NL":"EU",
    "NO":"EU","MX":"MA","DE":"EU","IT":"EU","UA":"EU",
    "SE":"EU","SI":"EU","AT":"EU","RU":"EU","LT":"EU","UK":"EU","ES":"EU","DK":"EU",
    "SR":"EU","SK":"EU","HR":"EU","RO":"EU"}
def getPlayerById(id):
    url="http://aligulac.com/api/v1/player/"+str(id)+"/?format=json&apikey="+key
    data=getJsonData(url)
    if type(data)==dict:
        civilname=data["name"]
        name=data["lp_name"]
        country=data["country"]
        race=data["race"]
        tag=data["tag"]
        if name=="":
            name=tag
        if country in wcsRegion:
            wcs=wcsRegion[country]
        else:
            wcs="Unknown"
        print(name,country,race,wcs)
        return (tag,country,race,wcs)
    else:
        return ("error","error","error")
def createPlayerInDb(aligulac_id):
    (name,country,race,wcs)=getPlayerById(aligulac_id)
    if len(Progamer.objects.filter(aligulac=aligulac_id))==0 and name!="error":
        p=Progamer(pseudo=name,aligulac=aligulac_id,mainrace=race,nationality=country,wcsregion=wcs)
        p.save()
        return p
    else:
        print("creation failed")

def addPlayerHighRating(limit=10,offset=0,ratingtresh=0.47):
    url="http://aligulac.com/api/v1/player/?current_rating__rating__gte="
    url+=str(ratingtresh)+"&limit="+str(limit)+"&offset="+str(offset)+"&format=json&apikey=K3W7uVs2NCF67DRyg05d"
    data=getJsonData(url)
    print(data.keys())
    list_player=data["objects"]
    for p in list_player:
        if p["country"]!="KR":
            createPlayerInDb(p["id"])
    return list_player
