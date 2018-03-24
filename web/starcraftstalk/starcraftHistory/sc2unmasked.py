#interface with sc2unmasked
from starcraftHistory.aligulac import *
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse
from starcraftHistory.models import Progamer,Players
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
def findSmurfHighMMR(server="eu",mmrthresh=6500):
    try :
        list_players=Players.objects.filter(server="eu",smurf=None,rating__gte=mmrthresh)
        for pdb in list_players:
            race=pdb.mainrace
            name=pdb.name.split("#")[0]
            server=pdb.server
            print("looking for ",race,name,server,pdb.legacy_id)
            url="http://sc2unmasked.com/API/Player?server="+str(server)+"&name="+str(name)+"&race="+str(race)
            data=getJsonData(url)
            for p in data["players"]:
                accid=p["acc_id"].split("/")
                legacyid=accid[0]
                realm=accid[1]
                race=p["race"].upper()
                aligulac=p["aligulac"]
    #            print(legacyid,pdb.legacy_id,type(realm),type(pdb.realm),race==pdb.mainrace,aligulac)
                if legacyid==pdb.legacy_id and realm==str(pdb.realm) and race==pdb.mainrace and aligulac!=None:
                    print("player found in sc2unmasked")
                    pros=Progamer.objects.filter(aligulac=aligulac)
                    if len(pros)==1:
                        print("smurf found")
                        pro_db=pros[0]
                        pdb.smurf=pro_db
                        pdb.save()
                        break
                    else:
                        print("creating aligulac",aligulac)
                        pro_db=createPlayerInDb(aligulac)
                        pdb.smurf=pro_db
                        pdb.save()
                        break
    except UnicodeEncodeError as e:
        print(e,url)

def getServer(server="eu"):
    url="http://sc2unmasked.com/API/Player?server="+str(server)
    data=getJsonData(url)
    for p in data["players"]:
        accid=p["acc_id"].split("/")
        legacyid=accid[0]
        realm=accid[1]
        race=p["race"].upper()
        aligulac=p["aligulac"]

        #print(race,legacyid,realm,aligulac)
        pdb=Players.objects.filter(server=server,legacy_id=legacyid,realm=realm,mainrace=race)
        if len(pdb)!=0 and aligulac!=None:
            if len(pdb)==1:
                player_in_db=pdb[0]
                pros=Progamer.objects.filter(aligulac=aligulac)
                print(player_in_db,pros,aligulac)
                if len(pros)==1:
                    print("smurf found")
                    pro_db=pros[0]
                    player_in_db.smurf=pro_db
                    player_in_db.save()

                else:
                    print(aligulac, "not in db")
