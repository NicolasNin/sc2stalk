from .useapi import Useapi
############NEW add new games

def syncDbwithMH(p,save=False):
	""" we update games in the db from games in MH
	p is a player instance	"""
	useapi=Useapi()
	matchHistory=useapi.getPlayerMatchHistory(p.path,p.alternate_path)
	#a liste of all the new game we create ot the one we update
	liste_newgame=[]
	if matchHistory!=[]:
		games_player=Games.objects.filter(path=p.path)
		for m in matchHistory:
			islastplayed=False
			indb=False
			if m["date"]==p.last_played or m["date"]==p.last_played-1:
				islastplayed=True
				if games_player.filter(date=m["date"]+1).exists():
					indb=True
					gdb=games_player.filter(date=m["date"]+1)[0]
			if games_player.filter(date=m["date"]).exists():
				gdb=games_player.filter(date=m["date"])[0]
				indb=True
			## we know if in db or not and lp or not
			if not indb:
				print("new game not in db",m["date"],"LP",islastplayed)
				newgame=updateGamefromMH(
				basicGamesFromPath(p.path,p.server),m)
				liste_newgame.append(newgame)
			else:
				(res,reason)=checkGamesindbwithMH(m,gdb)
				if  not res :
					print("in db not same",islastplayed,gdb.idgames,reason,m["date"],
					m["map"][0:5],gdb.map[0:5],m["decision"],
					gdb.decision,m["type"],gdb.type,m["date"],gdb.date)
					newgame=updateGamefromMH(gdb,m)
					liste_newgame.append(newgame)
				else:
					newgame=gdb
			if islastplayed:
				if newgame.player!=p:
					updateGameFromPlayerLP(newgame,p)
					liste_newgame.append(newgame)
		if save:
			for g in liste_newgame:
				g.save()
	return liste_newgame #eventually empty
def basicGamesFromPath(path,server):
	g=Games(server=server,path=path)
	return g
def updateGameFromPlayerLP(game,p):
	game.lastplayed_date=p.last_played
	game.player=p
	game.current_win=p.wins
	game.current_losses=p.loses
	game.current_ties=p.ties
	game.current_points=p.points
	game.current_rank=p.rank
	game.current_mmr=p.rating
	game.current_win_streak=p.current_win_streak
	game.current_league=p.league
def updateGamefromMH(game,m):
	game.date=m["date"]
	game.map=m["map"]
	game.decision=m["decision"]
	game.type=m["type"]
	game.speed=m["speed"]
	return game
def	checkGamesindbwithMH(m,gdb):
	if gdb.date!=m["date"]:
		return (False,"date")
	if gdb.map!= m["map"]:
		return (False,"map")
	if gdb.decision!=m["decision"]:
		return (False,"decision")
	if gdb.type!=m["type"]:
		return (False,"type")
	return (True,"OK")
########################
#mantis and claire, GUru Hellraiser etc
#syncDbwithMH(Players.objects.get(pk=1198),True)
#syncDbwithMH(Players.objects.get(pk=1213),True)
#syncDbwithMH(Players.objects.get(pk=1288),True)

#Games.objects.filter(path="/profile/2851847/1/Guru").
#update(player=Players.objects.get(pk=1025))
def attributeAllgameToPlayer(playerid):
	p=Players.objects.get(pk=playerid)
	games=Games.objects.filter(path=p.path)
	games.update(player=p)

#########
def compareDbandHistory(match_db,mh,p,pdb,msg,lid,deltaMMR,deltawins,deltalosses,deltaties):
	""" match_db is the games list without maps, we try to reconstruct the match
		history (ranked unranked ) by comparing with actual data from MH
	"""
	list_newgamesid=[]
	mh.sort(reverse=True) #most recent ones first
	#the first match should be the last_played_one from p
	shiftMH=0
	if len(mh)!=0  :
		m=mh[0][1]
		firstMH=mh[0][0]
		if firstMH==p["last_played"] or firstMH==p["last_played"]-1:

			returngame=addGamesinDB(p,m["map"],m["type"],m["decision"],
						m["speed"],m["date"],deltaMMR,msg,lid,pdb.idplayer)
			list_newgamesid.append(returngame)
			shiftMH=1
		else:
			print("last played not in match history",p["path"],p["last_played"])
			returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),
				"FASTER",p["last_played"],				deltaMMR,msg,lid,pdb.idplayer)
			list_newgamesid.append(returngame)
			shiftMH=0
	else:
		print("last played not in match history",p["path"],p["last_played"])
		returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),
			"FASTER",p["last_played"],deltaMMR,msg,lid,pdb.idplayer)
		list_newgamesid.append(returngame)
		shiftMH=0

	for (date,m) in mh[shiftMH:]:
		if match_db.filter(date=date).exists():
			mdb=match_db.filter(date=date)[0]
			mdb.map=m["map"]
			mdb.decision=m["decision"]
			mdb.save()
			print("update of map ",p["path"],date,mdb.idgames)
		elif match_db.filter(date=date+1).exists():
			mdb=match_db.filter(date=date+1)[0]
			mdb.map=m["map"]
			mdb.decision=m["decision"]
			mdb.date=date
			mdb.save()
			print("we updated the date to the one in MH",p["path"],date,mdb.idgames)
		else:
			# we dont know who played that we might know after looking at LP and dc
			returngame=addGamesinDB(p,m["map"],m["type"],m["decision"],m["speed"],m["date"],
				deltaMMR,"Unknown",lid,pdb.idplayer,True)
			list_newgamesid.append(returngame)
	return list_newgamesid
#unrank player Mantis OnFire
