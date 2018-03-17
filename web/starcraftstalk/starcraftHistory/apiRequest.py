import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse
from .apisettings import client_secret, api_key
import os.path
import datetime
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
def gettoken(region,api_key,client_secret):
    url="https://"+str(region)
    url+=".battle.net/oauth/token?grant_type=client_credentials&client_id="+str(api_key)
    url+="&client_secret="+str(client_secret)
    j=getJsonData(url)
    if type(j)==type({}):
        if "access_token" in j:
            return j["access_token"]
    return "error"
def updateAccessToken():
	global client_secret,api_key
	access_token={}
	filename="access_token.txt"
	delta=2591998
	newupdatetime=datetime.datetime.now().timestamp()+delta
	access_token["eu"]={"access_token":gettoken("eu",api_key,client_secret),"updateTime":newupdatetime}
	access_token["us"]={"access_token":gettoken("us",api_key,client_secret),"updateTime":newupdatetime}
	access_token["kr"]={"access_token":gettoken("kr",api_key,client_secret),"updateTime":newupdatetime}
	with open(filename, 'w') as f :
		json.dump(access_token,f)
	return access_token
def readAccesstoken(region):
	#check the file access_token.txt
	filename="access_token.txt"
	if os.path.isfile(filename):
		with open(filename, 'r') as f :
			access_token=json.load(f)
			eu=access_token["eu"]
			token=eu["access_token"]
			updateTime=eu["updateTime"]
			now=datetime.datetime.now().timestamp()
			if now>(updateTime-86400):
				return updateAccessToken()
			else:
				return token
	else:
		return updateAccessToken()

class apiRequest():
	def __init__(self,server="eu",season=35):
		self.server=server
		self.access_token=readAccesstoken(self.server)
		self.apikey=api_key
		self.current_season=str(season)
	def getCurrentSeason(self):
		print(self.access_token)
		url='https://'+self.server+".api.battle.net/data/sc2/season/current?access_token="+self.access_token
		return self.getJsonData(url)
	def checkNameConsistencyBnet(self,url):
		return url
	def getJsonData(self,url):
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
	def getOldPlayerLadder(self,path):
		url="https://"+self.server+".api.battle.net/sc2"+path+"/ladders?locale=en_GB&apikey="+self.apikey
		return self.getJsonData(url)
	def getOldProfile(self,path):
		url="https://"+self.server+".api.battle.net/sc2"+path+"/?locale=en_GB&apikey="+self.apikey
		return self.getJsonData(url)
	def getOldLadder(self,ladderid):
		url="https://"+self.server+".api.battle.net/sc2/ladder/"+str(ladderid)+"?locale=en_GB&apikey="+self.apikey
		return self.getJsonData(url)
	def getLadder(self,ladderid):
		url="""https://"""+self.server+""".api.battle.net/data/sc2/ladder/"""+str(ladderid)+"""?access_token="""+self.access_token
		return self.getJsonData(url)
	def getMatchHistoryByPath(self,path):
		url="https://"+self.server+".api.battle.net/sc2"+path+"/matches?locale=en_GB&apikey="+self.apikey
		print(url)
		return self.getJsonData(url)

	def getMatchHistory(self,name,player_id,realm=1):
		url="""https://"""+self.server+""".api.battle.net/sc2/profile/"""+str(player_id)+"""/"""+str(realm)+"""/"""+name+"""/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"""
		print(url)
		return self.getJsonData(url)
	def getLadderId(self,lvl=5):
		""" lvl: 5 is master, 6 is GM"""
		url="""https://"""+self.server+""".api.battle.net/data/sc2/league/"""+self.current_season+"""/201/0/"""+str(lvl)+"""?access_token="""+self.access_token
		print(url)
		return self.getJsonData(url)
	def getInfoCurrent(self):
		""" get the current season start timestamp and end timestamp"""
		url="https://"+self.server+".api.battle.net/data/sc2/season/current?access_token="+self.access_token
		return self.getJsonData(url)


if __name__=="__main__":
	#a=updateAccessToken()
	a=readAccesstoken("eu")
	print(a)
	api=apiRequest("eu")
	print(api.getCurrentSeason())

	print(api.getLadderId(lvl=6))
