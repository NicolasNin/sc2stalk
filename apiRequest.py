import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse

class apiRequest():
	def __init__(self):
		self.access_token="ts7yw3qvxntcn6q54rw229p5"
		self.apikey="rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"	
	
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
			return "error"	
	def getLadder(self,ladderid):
		url="""https://eu.api.battle.net/data/sc2/ladder/"""+str(ladderid)+"""?access_token="""+self.access_token
		return self.getJsonData(url)
	def getMatchHistory(self,name,player_id,realm=1):
		url="""https://eu.api.battle.net/sc2/profile/"""+str(player_id)+"""/"""+str(realm)+"""/"""+name+"""/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z"""
		print(url)
		return self.getJsonData(url)	
	def getLadderId(self,lvl=5):
		""" lvl: 5 is master, 6 is GM"""
		url="""https://eu.api.battle.net/data/sc2/league/31/201/0/5?access_token="""+self.access_token	
		print(url)
		return self.getJsonData(url)
