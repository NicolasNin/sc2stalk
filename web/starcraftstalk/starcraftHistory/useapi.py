from .apiRequest import *
class Useapi(apiRequest):
	def __init__(self,server="eu"):
		""" function that use the api"""
		super().__init__(server)
	#function for getting players informations
	def getPlayerProfile(self,path,alternate_path=""):
		""" getting stats such as total season game via old endpoint
		 return a dict with keys define below"""
		profile=self.getOldProfile(path)
		if type(profile)!= dict and alternate_path!=None and alternate_path!="":
			profile=api.getOldProfile(path)
		retd={}
		if type(profile)==dict:
			retd["zwins"]=profile["career"]["zergWins"]
			retd["pwins"]=profile["career"]["protossWins"]
			retd["twins"]=profile["career"]["terranWins"]
			retd["totalwins"]=retd["twins"]+retd["zwins"]+retd["pwins"]
			retd["careerGames"]=profile["career"]["careerTotalGames"]
			retd["seasonTotalGames"]=profile["career"]["seasonTotalGames"]

			if "stats" in profile["season"]:
				retd["ranked_wins"]=profile["season"]["stats"][0]["wins"]
				retd["ranked_losses"]=profile["season"]["stats"][0]["games"]-retd["ranked_wins"]
		return retd
	def getPlayerMatchHistory(self,path,alt_path=""):
		""" getting the match history endpoint
		return the list of matches	which are dict	"""

		MH=self.getMatchHistoryByPath(path)
		if alternate_path[0:-1]
		if type(MH)!=dict and alt_path !=None and alt_path!="":
			MH=self.getMatchHistoryByPath(alt_path)
		if type(MH)==dict:
			return MH["matches"]
		return []
	#functions for getting ladder from two endpoint thus getting player stats
	#function for getting leagues id
	#function for getting season info


def main():"""
	from starcraftHistory.useapi import Useapi
	from starcraftHistory.models import *
	use=Useapi()
	use.getPlayerProfile("/profile/2851847/1/Guru")
	use.getPlayerMatchHistory("/profile/2851847/1/Guru")
	use.getPlayerMatchHistory("/profile/1108727/1/Sheppard")

	"""
if __name__ == "__main__":

    main()
