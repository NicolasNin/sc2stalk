import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse
from .apisettings import access_token, api_key

class apiRequest():
	def __init__(self,server="eu"):
		self.server=server
		self.access_token=access_token[server]
		self.apikey=api_key
		self.current_season="32"
	def getCurrentSeason(self):
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
