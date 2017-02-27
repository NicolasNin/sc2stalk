import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse
from .apisettings import access_token, api_key

class apiRequest():
	def __init__(self,server="eu"):
		self.server=server
		#if self.server=="eu":
		#	self.access_token="ts7yw3qvxntcn6q54rw229p5"
		#if self.server=="us":
		#	self.access_token="h88936j5q7gnqx88s7tg9gdy"
		#if self.server=="kr":
		#	self.access_token=""
		self.access_token=access_token[server]
		self.apikey=api_key
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
	def getOldLadder(self,ladderid):
		url="https://"+self.server+".api.battle.net/sc2/ladder/"+str(ladderid)+"?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"			
		return self.getJsonData(url)
	def getLadder(self,ladderid):
		url="""https://"""+self.server+""".api.battle.net/data/sc2/ladder/"""+str(ladderid)+"""?access_token="""+self.access_token
		return self.getJsonData(url)
	def getMatchHistoryByPath(self,path):
		url="https://"+self.server+".api.battle.net/sc2"+path+"/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"
		print(url)
		return self.getJsonData(url)	
		
	def getMatchHistory(self,name,player_id,realm=1):
		url="""https://"""+self.server+""".api.battle.net/sc2/profile/"""+str(player_id)+"""/"""+str(realm)+"""/"""+name+"""/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"""
		print(url)
		return self.getJsonData(url)	
	def getLadderId(self,lvl=5):
		""" lvl: 5 is master, 6 is GM"""
		url="""https://"""+self.server+""".api.battle.net/data/sc2/league/31/201/0/"""+str(lvl)+"""?access_token="""+self.access_token	
		print(url)
		return self.getJsonData(url)
	def getInfoCurrent(self):
		""" get the current season start timestamp and end timestamp"""
		url="https://"+self.server+".api.battle.net/data/sc2/season/current?access_token="+self.access_token
		return self.getJsonData(url)


#season current donne id, year, timestamp start et timestamp end
#https://eu.api.battle.net/data/sc2/season/current?access_token=ts7yw3qvxntcn6q54rw229p5
# league id
#https://eu.api.battle.net/data/sc2/league/:SEASON_ID/:QUEUE_ID/:TEAM_TYPE/:LEAGUE_ID
#https://eu.api.battle.net/data/sc2/league/31/201/0/6?access_token=ts7yw3qvxntcn6q54rw229p5
#history of player
#https://eu.api.battle.net/sc2/profile/2101268/1/Stephano/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z

#ladder ranking and mmr
#https://eu.api.battle.net/data/sc2/ladder/189166?access_token=kkcbfz8ask4568aprq3v5aue
#63870

	
