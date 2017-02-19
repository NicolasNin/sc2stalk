import _mysql
import MySQLdb as mdb
import time
import datetime
import json
from urllib.request import urlopen
from urllib.error import HTTPError
import urllib.parse


if __name__ == '__main__':	
sql=Ladder_DatabaseSQL()
	#test	
sql.addNewPlayer("EU",3000,2000,150,120,5,123456,1111,789,1,"moi",'/aseazse/',"Z",0,0)
sql.addNewGame(1,"daybreak","1v1","win","faster",124167,3650)

#season current donne id, year, timestamp start et timestamp end
https://eu.api.battle.net/data/sc2/season/current?access_token=ts7yw3qvxntcn6q54rw229p5
# league id
https://eu.api.battle.net/data/sc2/league/:SEASON_ID/:QUEUE_ID/:TEAM_TYPE/:LEAGUE_ID
https://eu.api.battle.net/data/sc2/league/31/201/0/6?access_token=ts7yw3qvxntcn6q54rw229p5
#history of player
https://eu.api.battle.net/sc2/profile/2101268/1/Stephano/matches?locale=en_GB&apikey=rgvqqgg6tue3g5f5fu4r82v2xgy2dk7z

#ladder ranking and mmr
https://eu.api.battle.net/data/sc2/ladder/189166?access_token=kkcbfz8ask4568aprq3v5aue
63870


class Ladder_DatabaseSQL():
	""" a class that query an sql database with player table, and games tables"""
	def __init__(self):
		#to connect to db
		self.user="testuser"
		self.password="testpass"
		self.db="starcraft"
	
	def escapeString(self, txt):
		""" escape single quote into double"""
		return txt.replace("'","''")	
	def addNewGame(self,player_id,sc2map,sc2type,decision,speed,date,mmr,rank,ladderid,win,losses,ties,deltaMMR):
		""" this add a basic new game	 """
		query="""INSERT INTO `starcraft`.`Games` (`server`, `player_id`, `map`, `type`, `decision`, `speed`, `date`,`Current_MMR`,`Current_Rank`,`Current_league`,`Current_win`,`Current_losses`,`Current_ties`,`GuessMMRChange`)VALUES """
		query+="""('EU', '{0}', '{1}', '{2}', '{3}', '{4}', '{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}');""".format(player_id,self.escapeString(sc2map),sc2type,decision,speed,date,mmr,rank,str(ladderid),str(win),str(losses),str(ties),str(deltaMMR))
		print("adding a new game to database")
		self.executeQuery(query)
		
	def addNewPlayer(self,server,rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,name,path,mainrace,clan_id,idblizz,Battletag):
		query="""INSERT INTO `starcraft`.`Players` (`name`, `server`, `rating`, `points`, `wins`, `loses`, `ties`, `last_played`, `join_time`,
		 `legacy_id`, `realm`, `path`, `Clan_id`, `idblizz`, `mainrace`, `Battletag`) VALUES 
		 ('{0}', 'eu', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}','{14}')
		 """.format(self.escapeString(name),rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,path,clan_id,idblizz,mainrace,self.escapeString(Battletag))
		print("adding player to database")
		self.executeQuery(query)
	def getAllPlayer(self):
		query="""SELECT * FROM starcraft.Players """+""";"""
		return self.executeQuery(query)
	def getAllGames(self,id_in_db):
		query="""SELECT * FROM starcraft.Games where player_id="""+ str(id_in_db) +""" ORDER BY date asc;"""
		return self.executeQuery(query)		
	def getPLayerByBlizzId(self,blizz_id):
		query="""SELECT * FROM starcraft.Players where idblizz="""+str(blizz_id)+""";"""
		return self.executeQuery(query)
	def getPlayerByLegacyId(self,legacy_id):	
		query="""SELECT * FROM starcraft.Players where legacy_id="""+str(legacy_id)+""";"""#there can be many
		return self.executeQuery(query)

	def getPlayerById(self,id_in_db):	
		query="""SELECT * FROM starcraft.Players where idPlayer="""+str(id_in_db)+""";"""#there can be many
		return self.executeQuery(query)
	def getGamesBydateAndPlayer(self,date,player_id):
		query="""SELECT * FROM starcraft.Games where date="""+str(date)+""" and player_id="""+str(player_id)+""";"""
		return self.executeQuery(query)
	def getGamesById(self,gameid):
		query="""SELECT * FROM starcraft.Games where idGames="""+str(gameid)+""";"""
		return self.executeQuery(query)	
	def getLastGames(self,player_id):
		query="""SELECT *,date FROM starcraft.Games where player_id="""+str(player_id)+""" and date=(select max(date)  FROM starcraft.Games where player_id="""+str(player_id)+""");"""
		return self.executeQuery(query)	
	def getNoOpponent(self):
		query="""SELECT * FROM starcraft.NoOpponent;"""
		return self.executeQuery(query)	
	def updateOpponent(self,gameid,opponentid):
		query="""UPDATE `starcraft`.`Games` SET `GuessOpId`='"""+str(opponentid)+"""' WHERE `idGames`='"""+str(gameid)+"""';"""
		return self.executeQuery(query)
				
	def updateDeltaMMR(self,gameid,delta):
		query="""UPDATE `starcraft`.`Games` SET `GuessMMRChange`='"""+str(delta)+"""' WHERE `idGames`='"""+str(gameid)+"""';"""
		return self.executeQuery(query)
				
	def executeQuery(self,query):
		ret=""	 
		try:
			con=mdb.connect('localhost', 'testuser', 'testpass', 'starcraft')
			con.set_character_set('utf8')
			cur = con.cursor()
			#utf8 issue
			cur.execute('SET NAMES utf8;')
			cur.execute('SET CHARACTER SET utf8;')
			cur.execute('SET character_set_connection=utf8;')
			#
			cur.execute(query)
			ret=cur.fetchall()
			con.commit()
				
		except mdb.Error as e:
			print(e)
			print(query)
		con.close()
		return ret
		
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
		self.ladders_id={"GM":[191177],"M":[190560,190651,190328,190718,190806,190901,191018,190662,191087,190608,190791,191148,191579,191159,190353,191349,190321,190914,
		191281,190847,190682,191036,191443]}
		self.tierM1=5192
		#request that failed
		self.requestPool=[]
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
					self.players_blizz[idblizz]={"last_played":last_played,"name":name,"last_game":last_games_played,"db_id":id_in_db,"mmr":last_mmr}
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
				
	def updatePlayer(self,name,id_blizz,legacy_id,realm=1,mmr=1000,rank=1000,league=0,win=-1,losses=-1,ties=-1):
		if mmr>self.tierM1:
			print("Looking for new game for",name,legacy_id, id_blizz,mmr,win,losses)
			legacy_id
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
						deltaMMR=0 #if we add more than one game then we dont really know the mmr change
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
					print("first Time seing this long blizz id")
					self.db.addNewPlayer("EU",rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,name,path,mainrace,clan_id,id_blizz,battletag)
				#	db_id=self.db.getPlayerByLegacyId(legacy_id)[0][0] #TO CHANGE THERE CAN BE many name change
					db_id=self.db.getPLayerByBlizzId(id_blizz)[0][0] 
					self.players_blizz[id_blizz]={"last_played":last_played,"name":name,"last_game":0,"db_id":db_id,"mmr":rating}
					self.players[legacy_id]={"last_played":last_played,"name":name,"last_game":0,"db_id":db_id,"mmr":rating}
					self.updatePlayer(name.split("#")[0],id_blizz,legacy_id,realm,rating,current_rank,ladder_id,wins,loses,ties)
				else:
					change_reason=""	
					if self.players_blizz[id_blizz]["last_played"]!=last_played:
						change_reason="Last played went from "+str(self.players_blizz[id_blizz]["last_played"])+" to "+str(last_played)+"\n"
					if self.players_blizz[id_blizz]["mmr"]!=rating:
						change_reason+="MMR went from "+ str(self.players_blizz[id_blizz]["mmr"])+" to "+ str(rating)
					if change_reason!="":
						print("-----------------------------------",change_reason)
						isUpdateSucces=self.updatePlayer(name.split("#")[0],id_blizz,legacy_id,realm,rating,current_rank,ladder_id,wins,loses,ties)
						if isUpdateSucces:
							self.players_blizz[id_blizz]["last_played"]=last_played
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
	def showPlayerHistory(self,legacy_id):
		id_in_db=self.players[legacy_id]["db_id"]
		name=self.players[legacy_id]["name"]
		print("---------- Games History of ",name,legacy_id,"----------------------------------")
		print("""# Date  \t\tOpponent \t\t Map \t\t\t Result MMR """)
		allgames=self.db.getAllGames(id_in_db)		 
		for games in allgames:
			date=datetime.datetime.fromtimestamp(games[7]).strftime('%Y-%m-%d %H:%M')
			result=games[5]
			sc2map=games[3]
			mmr=games[12]
			pad=""
			if games[8]!=None:
				op=self.db.getPlayerById(games[8])
				opname=op[0][1].split("#")[0]
				oprace=op[0][15]
				if len(opname)<=11:
					pad="\t"
				if len(opname)<=4:
					pad+="\t"			
			else:
				opname="NA     "
				oprace="NA"
				pad="\t"
			print("""{0} {1}\t{2}({3}){7} \t {4}\t {5} \t{6}""".format(games[0],date,opname,oprace,sc2map[0:min(20,len(sc2map))],result,mmr,pad))
GM=updateDB()
GM.checkConsistencyWithDb(True)
GM.updateLeagues()


##check for offracing
listeplayer=db1.getAllPlayer()

count=0
exclude=[]
for i,p1 in enumerate(listeplayer):
	path1=p1[12]
	mmr=p1[3]
	disp=""
	if(mmr>5100):
		for j,p2 in enumerate(listeplayer[i+1:]):
			path2=p2[12]
			if path2 not in exclude:
				if path1==path2:				
					disp+=str(p2)+"\n"
		if disp!="":
			exclude.append(path1)
			count+=1
			print(" ---------------- ", count, "-----------------")
			print(p1)
			print(disp)		
	
			
	    
	
	
		
