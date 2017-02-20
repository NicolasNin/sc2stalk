from sqlhandle import *
from apiRequest import *
import time
import datetime

if __name__ == '__main__':	
	sql=Ladder_DatabaseSQL()
	#test	

#we go fetch ladder
# if new player we add and  go fetch player history
#if old player we compare last_played_time_stamp
#potential error: an error can happen when we request via the api, when we request the db, and between the db and the in memory consistency in self.players
class 	updateDB():
	def __init__(self):
		self.api=apiRequest()
		self.db=Ladder_DatabaseSQL()
		#dict of players with name,legacy_id,newid,lastMMR
		self.players={}
		self.players_blizz={}	#blizz as key cause legacy id is NOT unique ie name change 
		#dict of current season ladder id
		#only GM and Master X24
		self.season_id=31
		self.ladders_id={"GM":[191177],"M":[]}
		self.getLadderId()
		self.tierM1=5192
		#game that have just been added to the db in the last update, we can use this to findOpponent and display the result
		self.newGames=[]
		self.msg=[]
	def getLadderId(self,lvl=5):
		"""update liste of self.ladders_id"""
		M1=self.api.getLadderId(lvl)["tier"][0]["division"] #only M1
		id_M1=[]
		for l in M1:
			id_M1.append(l["ladder_id"])
		self.ladders_id["M"]=id_M1
		
	def checkConsistencyWithDb(self,create=False):
		players=self.db.getAllPlayer()
		for p in players:
			id_in_db=p[0]
			name=p[1]
			server=p[2]
			rating=p[3]
			points=p[4]
			wins=p[5]
			loses=p[6]
			ties=p[7]
			last_played=p[8]
			join_time=p[9]
			legacy_id=int(p[10])
			realm=p[11]
			path=p[12]
			clan_id=p[13]
			idblizz=str(p[14])
			race=p[15]
			battletag=p[16]
			smurf=p[17]
			offrace=p[18]
			if offrace==None:
				offrace="NULL"
			last_game_in_db=self.db.getLastGames(id_in_db) 
			if last_game_in_db==():
				last_games_played=0
				last_mmr=rating
			else:
				last_games_played=last_game_in_db[0][-1] #date of last game in games table for player_id set to 0 if none
				last_mmr=int(last_game_in_db[0][10])
			
			if idblizz not in self.players_blizz.keys():
				print("player in SQL db but not in memory")
				if create:
					self.players_blizz[idblizz]={"last_played":last_played,"name":name,"last_game":last_games_played,"db_id":id_in_db,"mmr":last_mmr,"main":offrace}
			else:
				p2=self.players_blizz[idblizz]
				#"last_played":last_played,"name":name,"last_game":0,"db_id":db_id,"mmr":rating}
				#last_played is not currently not updated nor mmr
				if p2["name"]!=name:
					print("different name",p2["name"],name)				
				if p2["db_id"]!=id_in_db:
					print("different id in db",p2["db_id"],id_in_db)
					
				if p2["last_game"]!=last_games_played:
					print("different last game date",p2["last_game"],last_games_played)
					
				#if p2["mmr"]!=rating:
				#	print("different mmr",p2["mmr"],rating)
			
	def updateLeagues(self,All=False):
		#update or create GM
		self.updateLadder(self.ladders_id["GM"][0])
		#update the master league and update history of player above self.tierM1 MMR or a given MMR (not to to too much request on lower MMR player)
		if All:
			for league_id in self.ladders_id["M"]:
				self.updateLadder(league_id)
		self.displayNewGames()		
		self.newGames=[]		
	def updatePlayer(self,name,id_blizz,legacy_id,realm=1,mmr=1000,rank=1000,league=0,win=-1,losses=-1,ties=-1):
		if mmr>self.tierM1 and self.players_blizz[id_blizz]["main"]=="NULL":
			print("Looking for new game for",name,legacy_id, id_blizz,mmr,win,losses)
			db_id=self.players_blizz[id_blizz]["db_id"]
			#last_game_in_db=self.db.getLastGames(player_id)
			last_game_in_db=self.players_blizz[id_blizz]["last_game"]
			last_mmr=self.players_blizz[id_blizz]["mmr"]
			deltaMMR=mmr-last_mmr
			history=self.api.getMatchHistory(name,legacy_id,realm)
			maxdate=last_game_in_db
			if history!="error":
				for m in history["matches"]:
					date=m["date"]
					if date>last_game_in_db:
						sc2map=m["map"]
						sc2type=m["type"]
						decision=m["decision"]
						speed=m["speed"]
						self.db.addNewGame(db_id,sc2map,sc2type,decision,speed,date,mmr,rank,league,win,losses,ties,deltaMMR)
						game_id_in_db=self.db.getGamesBydateAndPlayer(date,db_id)[0][0]
						self.newGames.append(game_id_in_db)
						self.findOneOpponent(game_id_in_db)
						deltaMMR=0 #if we add more than one game then we dont really know the mmr change this is a pretty crappy solution 
						self.players_blizz[id_blizz]["mmr"]=mmr #this is here because we want to change mmr only when we add game because API strange behavior (mmr back and forth)
						if date>maxdate:
							maxdate=date
				self.players_blizz[id_blizz]["last_game"]=maxdate
				
				return True
			else:
				""" add request to the pool"""
				return False
		else:
			return False		
	def updateLadder(self,ladder_id):
		ladder=self.api.getLadder(ladder_id)
		if ladder!="error":
			for player in ladder["team"]:
				clan_id=0	
				""" player is a dict with rating losses  wins ties points"""
				id_blizz=str(player["id"])
				rating=player["rating"]
				points=player["points"]
				wins=player["wins"]
				loses=player["losses"]
				ties=player["ties"]
				current_rank=player["current_rank"]
				join_time=player["join_time_stamp"]
				name=player["member"][0]["legacy_link"]["name"]
				path=player["member"][0]["legacy_link"]["path"]
				realm=player["member"][0]["legacy_link"]["realm"]
				battletag=player["member"][0]["character_link"]["battle_tag"]
				legacy_id=player["member"][0]["legacy_link"]["id"]
				raceplayed=player["member"][0]["played_race_count"][0]["race"]["en_US"]
				count=player["member"][0]["played_race_count"][0]["count"]
				current_rank
				mainrace="R"
				if raceplayed=="Zerg":
					mainrace="Z"
				if raceplayed=="Terran":
					mainrace="T"
				if raceplayed=="Protoss":
					mainrace="P"
				last_played=player["last_played_time_stamp"]
				# we check if the player exist with idblizz !
				if id_blizz not in self.players_blizz.keys():
					print("first Time seing this long blizz id",id_blizz)
					#we check if the path exist ie legacy/name/realm which is the data for the match history in this case we add id_in_db of said player as main
					main_id="NULL"
					samepath=self.db.getPlayerByPath(path)
					if samepath!=():
						main_id=0
						print("player already exist with a different blizz id but same path")
						if len(samepath)==1:
							main_id=samepath[0][0]
						else:
							for p in samepath:
								if p[18]!=None:
									main_id=p[18]
							
					self.db.addNewPlayer("EU",rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,name,path,mainrace,clan_id,id_blizz,battletag,main_id)
					
					db_id=self.db.getPLayerByBlizzId(id_blizz)[0][0] 
					self.players_blizz[id_blizz]={"last_played":last_played,"name":name,"last_game":0,"db_id":db_id,"mmr":rating,"main":main_id}
					self.updatePlayer(name.split("#")[0],id_blizz,legacy_id,realm,rating,current_rank,ladder_id,wins,loses,ties)
				else:
					change_reason=""	
					if self.players_blizz[id_blizz]["last_played"]!=last_played:
						change_reason="LP |"
					if self.players_blizz[id_blizz]["mmr"]!=rating:
						change_reason+="MMR: "+ str(self.players_blizz[id_blizz]["mmr"])+" to "+ str(rating)
					if change_reason!="":
						print("-----------------------------------",change_reason)
						isUpdateSucces=self.updatePlayer(name.split("#")[0],id_blizz,legacy_id,realm,rating,current_rank,ladder_id,wins,loses,ties)
						if isUpdateSucces:
							self.players_blizz[id_blizz]["last_played"]=last_played
							self.db.updateWhere("Players",["rating","last_played","wins","loses","ties"],[rating,last_played,wins,loses,ties],"idblizz",id_blizz)
	def deltaMMR(self):
		for blizzid in self.players_blizz:
			print("computing delta MMR for", blizzid)
			id_in_db=self.players_blizz[blizzid]["db_id"]
			allgames=self.db.getAllGames(id_in_db)
			last=False
			last_mmr=0
			
			for g in allgames:
				delta=0
				newmmr=g[10]
				if last==True:
					if last_mmr!=newmmr:
						delta=int(newmmr)-int(last_mmr)
						gameid=g[0]
						self.db.updateDeltaMMR(gameid,delta)
				last_mmr=newmmr
				last=True
	def findOneOpponent(self,gameid):
		game=self.db.getWhere("Games",["idGames"],[gameid])[0]
		id_in_db=game[2]
		sc2map=game[3]
		sc2type=game[4]
		decision=game[5]
		date=game[7]
		if decision=="TIE" or decision=="BAILER":
			decision2=decision
		else:
			if decision=="WIN":
				decision2="LOSS" 
			else:
				decision2="WIN"
		games=self.db.getWhere("NoOpponent",["map","type","decision","date"],[sc2map,sc2type,decision2,date])
		if len(games)>1:
			print("many possible match",date,sc2map)
			self.msg.append("many possible match "+str(date))
		if len(games)==1:
			opgameid=games[0][0]
			opid=games[0][2]
			self.db.updateWhere("Games",["GuessOpId","GuessOpGameId"],[opid,opgameid],"idGames",gameid)
			self.db.updateWhere("Games",["GuessOpId","GuessOpGameId"],[id_in_db,gameid],"idGames",opgameid)
					
	def displayNewGames(self):
		print("New game found in this update:",len(self.newGames))
		print("-------------------------------------------------------------")
		for gameid in self.newGames:
			game=self.db.getGamesById(gameid)[0]
			print(game)
									
	def findOpponent(self):
		noOpponent=self.db.getNoOpponent()
		num=0
		for i,game in enumerate(noOpponent):
			sc2map=game[3]
			decision=game[5]
			date=game[7]
			gametype=game[4]
			gameid=game[0] 
			playerid=game[2]
			for game2 in noOpponent[i:]:
				sc2map2=game2[3]
				decision2=game2[5]
				date2=game2[7]
				gametype2=game2[4]
				gameid2=game2[0]
				playerid2=game2[2]
				if sc2map2!=sc2map:
					break #because it is ordered by map first
				if sc2map==sc2map2 and date==date2 and gametype== gametype2:
					if ((decision=="WIN" and decision2=="LOSS") or (decision2=="WIN" and decision=="LOSS") or (decision=="BAILER" and decision2=="BAILER") or (decision=="TIE" and decision2=="TIE")) and (playerid!=playerid2):
						print("game found",date,decision,decision2,playerid,playerid2,num)
						self.db.updateOpponent(gameid,playerid2)
						self.db.updateOpponent(gameid2,playerid)
		return num				

GM=updateDB()
GM.checkConsistencyWithDb(True)
GM.updateLeagues()


##check for offracing
listeplayer=db1.getAllPlayer()
count=0
exclude=[]
idem={}
for i,p1 in enumerate(listeplayer):
	path1=p1[12]
	mmr=p1[3]
	disp=""
	none=0
	if p1[18]==None:
		none=1
	if(mmr>4000):
		for j,p2 in enumerate(listeplayer[i+1:]):
			path2=p2[12]
		
			if path2 not in exclude:
				if path1==path2:
					if path1 not in idem.keys():
						idem[path1]=[p1]
					idem[path1].append(p2)
					if 	p2[18]==None:
						none+=1		
					disp+=str(p2)+"\n"
		if disp!="" and none>1:
			exclude.append(path1)
			count+=1
			print(" ---------------- ", count,none, "-----------------")
			print(p1)
			print(disp)		
for group in idem:
	mmrmax=0
	totalmax=0
	imaxmmr=-1
	imaxtotal=-1
	print("-----------------",group,"---------------------------------------------")	
	for i,p in enumerate(idem[group]):
		print(i,p)
		mmri=p[3]
		totalgamei=p[5]+p[6]
		if mmri>mmrmax:
			imaxmmr=i
			mmrmax=mmri			
		if totalgamei>totalmax:
			imaxtotal=i
			totalmax=totalgamei
	if imaxmmr==imaxtotal:
		print("best mmr ", imaxmmr," bestotal ", imaxtotal, "decided main ",imaxmmr,idem[group][imaxmmr][0])
		main_id=idem[group][imaxmmr][0]
		for i,p in enumerate(idem[group]):
			if i!=imaxmmr:
				id_in_db=p[0]
				print("updating ",id_in_db, "with offrace of main", main_id)
				#db1.updateOffrace(id_in_db,main_id)			
	else:
		print("best mmr ", imaxmmr," bestotal ", imaxtotal)
				
			
	    

		
