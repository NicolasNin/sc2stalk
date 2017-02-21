import _mysql
import MySQLdb as mdb
class Ladder_DatabaseSQL():
	""" a class that query an sql database with player table, and games tables"""
	def __init__(self):
		#to connect to db
		self.user=""
		self.password=""
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
		
	def addNewPlayer(self,server,rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,name,path,mainrace,clan_id,idblizz,Battletag,offrace):
		query="""INSERT INTO `starcraft`.`Players` (`name`, `server`, `rating`, `points`, `wins`, `loses`, `ties`, `last_played`, `join_time`,
		 `legacy_id`, `realm`, `path`, `Clan_id`, `idblizz`, `mainrace`, `Battletag`,`offrace`) VALUES 
		 ('{0}', 'eu', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}','{14}',{15})
		 """.format(self.escapeString(name),rating,points,wins,loses,ties,last_played,join_time,legacy_id,realm,path,clan_id,idblizz,mainrace,self.escapeString(Battletag),offrace)
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
	def getPlayerRealName(self,id_in_db):
		query="""SELECT * FROM starcraft.realName where idPlayer="""+str(id_in_db)+""";"""
		return 	self.executeQuery(query)
	def getPlayerByLegacyId(self,legacy_id):	
		query="""SELECT * FROM starcraft.Players where legacy_id="""+str(legacy_id)+""";"""#there can be many
		return self.executeQuery(query)
	def getPlayerByPath(self,path):	
		query="""SELECT * FROM starcraft.Players where path='"""+str(path)+"""';"""#there can be many
		return self.executeQuery(query)
	def getPlayerById(self,id_in_db):	
		query="""SELECT * FROM starcraft.Players where idPlayer="""+str(id_in_db)+""";"""
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
	def updateOffrace(self,player_id,main_player_id):
		query="""UPDATE `starcraft`.`Players` SET `offrace`="""+str(main_player_id)+""" WHERE `idPlayer`='"""+str(player_id)+"""';"""
		return self.executeQuery(query)	
	#more general queries
	def quotify(self,val):
		if type(val)==int:
			return str(val)+" "
		else:
			return "'"+self.escapeString(val)+"' "
	def getWhere(self,table,fields,values):
		query="SELECT * from "+table+" where "
		for i,field in enumerate(fields):
			val=values[i]
			query+=field+"="+self.quotify(val)
			if i!=len(fields)-1:
				query+=" and "
		return  self.executeQuery(query)
	def updateWhere(self,table,fields,values,wherefields,wherevalues):

		query="UPDATE "+table+" SET "
		for i,field in enumerate(fields):
			val=values[i]
			query+=field+"="+self.quotify(val)
			if i!=(len(fields)-1):
				query+=" , "
		query+=" WHERE "+ wherefields+"="+self.quotify(wherevalues)
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
