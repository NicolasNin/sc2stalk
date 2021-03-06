from .apiRequest import apiRequest
from .findOp import *
from .models import League, Players, Games, Progamer,Global
from django.db.models import  Max
from django.db import IntegrityError
from background_task import background
from django.db import transaction
from time import time
def updateAllSeason():
	updateSeason("eu")
	updateSeason("kr")
	updateSeason("us")
def updateSeason(server):
	print("NEW SEASON",server)
	api=apiRequest(server=server)
	season_data=api.getCurrentSeason()
	season_id=season_data["id"]
	season_start=season_data["start_timestamp"]
	season_end=season_data["end_timestamp"]
	current_seasonDB=Global.objects.filter(name="currentseason")[0]
	current_seasonDB.value=season_id
	current_seasonDB.save()
	current_season_endDB=Global.objects.filter(name="currentseason_end"+server)[0]
	current_season_endDB.value=season_end
	current_season_endDB.save()
	return season_id
def updateLeagues(server,force=False):
	if Global.objects.filter(name="lastupdateleagues"+server).exists():
		val=Global.objects.filter(name="lastupdateleagues"+server)[0]
		lastup=int(val.value)
	else:
		val=Global(name="lastupdateleagues"+server,value=str(int(time())))
		lastup=int(time())-3610
		val.save()
	#first we retrieve the already existing leagues
	if time()>lastup+3600 or force:
		print("updating leagues",server)
		updateOldPath(up=True,server=server)
		existingLeagues=League.objects.filter(server=server)
		liste_existing_ladderid=[]
		for exl in existingLeagues:
			liste_existing_ladderid.append(exl.ladderid)
		api=apiRequest(server=server)
		#GM
		l=api.getLadderId(6)
		notup=False
		try:
			season=l["key"]["season_id"]
			ladderid=l["tier"][0]["division"][0]["ladder_id"]

			if ladderid not in liste_existing_ladderid :
				L=League(ladderid=int(ladderid),season=int(season),level=6,
				sigle="GM",server=server)
				L.save()
		except  KeyError:
			print("GM not up yet")
		#Master1
		try:
			leaguesM1=api.getLadderId(5)["tier"][0]
			for l in leaguesM1["division"]:
				if l["ladder_id"] not in liste_existing_ladderid:
					League(ladderid=int(l["ladder_id"]),season=int(season),level=5
					,sigle="M",server=server).save()
			val.value=str(int(time()))
			val.save()
		except  KeyError:
			print("MASTER not up yet")
def gettingLadderPlayers(liste_ladderid,server):
	""" from a liste of ladder_id we return a dict  of player from
	 the    sc2api with keys the ladderid"""
	api = apiRequest(server=server)
	api_players = {}
	print("Getting the ladder:", end=" ")
	for lid in liste_ladderid:
		print(lid, end="  ")
		ladder = api.getLadder(lid)
		if type(ladder) == dict:
			api_players[lid] = ladder["team"]
			print("success", end=" | ")
		else:
			#error in retrieving we put an empty list
			api_players[lid]=[]
			print(ladder[0])
	print("--")
	return api_players
def beautifulPlayer(player):
	"""player is a dict of bnet api from ladder["team"],return a
	 dict with keys such as rating wins etc from the dict of blizzard"""
	try:
		p = {}
		p["id_blizz"] = player["id"]
		p["rating"] = player["rating"]
		p["points"] = player["points"]  # do not use
		p["wins"] = player["wins"]
		p["losses"] = player["losses"]
		p["ties"] = player["ties"]
		p["current_rank"] = player["current_rank"]
		p["join_time"] = player["join_time_stamp"]  # do not use
		p["name"] = player["member"][0]["legacy_link"]["name"]  # name with #
		p["path"] = player["member"][0]["legacy_link"]["path"]
		p["realm"] = player["member"][0]["legacy_link"]["realm"]
		p["battletag"] = player["member"][0]["character_link"]["battle_tag"]
		p["legacy_id"] = player["member"][0]["legacy_link"]["id"]
		p["raceplayed"] = player["member"][0][
			"played_race_count"][0]["race"]["en_US"]
		p["race_count"] = player["member"][0]["played_race_count"][0]["count"]
		if "clan_link" in player["member"][0].keys():
			p["clan_id"] = player["member"][0]["clan_link"]["id"]
			p["clan_tag"] = player["member"][0]["clan_link"]["clan_tag"]
			p["clan_name"] = player["member"][0]["clan_link"]["clan_name"]
		else:
			p["clan_id"] = -1
			p["clan_tag"] = ""
		p["mainrace"] = "R"
		if p["raceplayed"] == "Zerg":
			p["mainrace"] = "Z"
		if p["raceplayed"] == "Terran":
			p["mainrace"] = "T"
		if p["raceplayed"] == "Protoss":
			p["mainrace"] = "P"
		p["last_played"] = player["last_played_time_stamp"]
		p["current_win_streak"] = player["current_win_streak"]
		p["current_rank"] = player["current_rank"]
	except KeyError as e:
		print(e,player)
		return "error"
	return p
def updatePlayer(pobj, p, lid,lastMHupdate,season,server,msg):
	"""update the Player object pobj with the data from api"""
	if msg!="nothing":
		pobj.name = p["name"]
		pobj.server = server
		pobj.rating = p["rating"]
		pobj.wins = p["wins"]
		pobj.loses = p["losses"]
		pobj.ties = p["ties"]
		pobj.last_played = p["last_played"]
		pobj.join_time = p["join_time"]
		pobj.legacy_id = p["legacy_id"]
		pobj.realm = p["realm"]
		pobj.path = p["path"]
		pobj.clan_id = p["clan_id"]
		pobj.idblizz = p["id_blizz"]
		pobj.mainrace = p["mainrace"]
		pobj.battletag = p["battletag"]
		pobj.race_count = p["race_count"]
		pobj.points = p["points"]
		pobj.current_win_streak = p["current_win_streak"]
		pobj.league = lid
		pobj.lastmhupdate=lastMHupdate
		pobj.rank=p["current_rank"]
		pobj.season=season
		#we check if there exist a preivous player with same race and path for smurf
		if lastMHupdate==0:
			if Players.objects.filter(battletag=p["battletag"],mainrace=p["mainrace"]).exists():
				pold=Players.objects.filter(battletag=p["battletag"],mainrace=p["mainrace"])[0]
				if pold.smurf!=None:
					pobj.smurf=pold.smurf


		pobj.save()
@background(schedule=10)
def updateAll():
	updateServerCycle("eu")
	updateServerCycle("us")
	#	updateServerCycle("kr")
	print(" Cycle update finished")
	print("")

def updateServerCycle(server="eu"):
	""" we get the ladders date from all the league, then
	 update each player when needed"""
	print("RUN AN UPDATE "+server)
	print("-----------------------------------------------------")
	forceupdateleague=False
	currentseason=int(Global.objects.filter(name="currentseason")[0].value)
	current_season_end=int(Global.objects.filter(name="currentseason_end"+server)[0].value)
	## is this time for a new season?
	if time()>=current_season_end:
		current_season=updateAllSeason()
		forceupdateleague=True
	updateLeagues(server=server,force=forceupdateleague)
	player_in_db = Players.objects.filter(server=server)
	db_players = {}
	for player in player_in_db:
		db_players[player.idblizz] = player


	liste_ladderid = League.objects.filter(season=currentseason,server=server)

	player_from_api = gettingLadderPlayers(
		liste_ladderid,server=server)  # a dict on which we loop to update
	newgames=[]
	for lid in liste_ladderid:
		for player in player_from_api[lid]:
			p = beautifulPlayer(player)
			if p!="error":
				if str(p["id_blizz"]) in db_players:
					pdb = db_players[str(p["id_blizz"])]
					#big loop start here
					(lastMHupdate,newgamesp,msg)=addNewGamePlayer(pdb,p,lid,server)
					newgames.extend(newgamesp)
					updatePlayer(pdb, p, lid,lastMHupdate,currentseason,server,msg)
				else:
					updatePlayer(Players(),p,lid,0,currentseason,server,msg="new")
	print(newgames)
	found=findOpListObject(newgames,save=False)
	checkReciprocal(found,save=True)

def syncDbwithMH(player):
	"""we update the games without maps and add newgames if MH was
	never look at, if there is new game  """

	return 0
def addNewGamePlayer(pdb,p,lid,server):
	""" pdb is an object player, p is a dict from the api
		thus pdb is old state, while p i new
	"""
	list_newgamesid=[]
	player_id=pdb.idplayer
	deltaMMR = p["rating"] - pdb.rating
	deltawins = p["wins"] - pdb.wins
	deltalosses = p["losses"] - pdb.loses
	deltaties = p["ties"] - pdb.ties
	deltaLP = p["last_played"] - pdb.last_played
	deltacount = p["race_count"] - pdb.race_count
	(msg, b) = lookForDiscrepancy(deltaMMR, deltawins,
											  deltalosses, deltaties, deltacount, deltaLP)
	maxdate=Players.objects.filter(path=p["path"],server=server).aggregate(Max('lastmhupdate'))["lastmhupdate__max"]
	if b==True and msg!="nothing":
		print("-----------------------------")
		lmhu=0
		if maxdate!=None:
			lmhu=maxdate
		(newinMH,maxdate)=getNewMatchHistory(p["path"],pdb.alternate_path,lmhu,server)
		if newinMH!="error":
			#we add the notsolo
			for g in newinMH["notSOLO"]:
				returngame=addGamesinDB(p,g["map"],g["type"],g["decision"],
					g["speed"],g["date"],deltaMMR,msg,lid,player_id,True,server)
				list_newgamesid.append(returngame)

			#we add the solo match or update the one in db
			nomapsgame=Games.objects.filter(server=server,path=p["path"],map="")
			otherlist=compareDbandHistory(nomapsgame,newinMH["SOLO"],p,pdb,msg,lid,
					deltaMMR,deltawins,deltalosses,deltaties,server)

			list_newgamesid.extend(otherlist)
		else:#pas de match history on ajoute l'unique game sans map
			#ranked ou many=> partie ranked, on ajoute le count
			if msg=="ranked" or msg=="many":
				msg=str(deltacount)
			returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),"FASTER",p["last_played"],
				deltaMMR,msg,lid,player_id,False,server)
			list_newgamesid.append(returngame)
	return (maxdate,list_newgamesid,msg)

def compareDbandHistory(match_db,mh,p,pdb,msg,lid,deltaMMR,deltawins,deltalosses,deltaties,server):
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
						m["speed"],m["date"],deltaMMR,msg,lid,pdb.idplayer,False,server)
			list_newgamesid.append(returngame)
			shiftMH=1
		else:
			print("last played not in match history",p["path"],p["last_played"])
			returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),
				"FASTER",p["last_played"],deltaMMR,msg,lid,pdb.idplayer,False,server)
			list_newgamesid.append(returngame)
			shiftMH=0
	else:
		print("last played not in match history",p["path"],p["last_played"])
		returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),
			"FASTER",p["last_played"],deltaMMR,msg,lid,pdb.idplayer,False,server)
		list_newgamesid.append(returngame)
		shiftMH=0

	for (date,m) in mh[shiftMH:]:
		if match_db.filter(date=date).exists():
			mdb=match_db.filter(date=date)[0]
			mdb.map=m["map"].encode('latin-1').decode('utf-8')
			mdb.decision=m["decision"]
			mdb.save()
			print("update of map ",p["path"],date,mdb.idgames)
		elif match_db.filter(date=date+1).exists():
			mdb=match_db.filter(date=date+1)[0]
			mdb.map=m["map"].encode('latin-1').decode('utf-8')
			mdb.decision=m["decision"]
			mdb.date=date
			mdb.save()
			print("we updated the date to the one in MH",p["path"],date,mdb.idgames)
		else:
			# we dont know who played that we might know after looking at LP and dc
			returngame=addGamesinDB(p,m["map"],m["type"],m["decision"],m["speed"],m["date"],
				deltaMMR,"Unknown",lid,pdb.idplayer,True,server)
			list_newgamesid.append(returngame)
	return list_newgamesid

def addGamesinDB(p,sc2map,sc2type,decision,speed,date,deltaMMR,ranked,lid,player_id,
unknown=False,server="eu"):
	print(p["path"],date,unknown,lid,deltaMMR,decision)
	try:
		sc2map=sc2map[0:44].encode("utf-8").decode("utf-8")
	except UnicodeEncodeError as e:
		print(e)
		sc2map="error"
	try:
		with transaction.atomic():
			if unknown:#in those game we dont know the player but we know the map (from MH)
				g=Games(server=server,map=sc2map,type=sc2type,speed=speed,date=date,ranked=ranked,
				  path=p["path"],decision=decision,current_league=lid)

				g.save()

				return g
			else:
				#In those games we know the player, map might be empty (from MH and/or LP)
				g=Games(server=server,map=sc2map,type=sc2type,speed=speed,date=date,current_mmr=p["rating"],
				  current_rank=p["current_rank"],current_league=lid,current_win=p["wins"],current_losses=p["losses"],
				  current_ties=p["ties"],current_points=p["points"],player_id=player_id,ranked=ranked,
				  path=p["path"],current_win_streak=p["current_win_streak"],guessmmrchange=deltaMMR,
				  lastplayed_date=p["last_played"],decision=decision)
				g.save()

				return g
	except 	IntegrityError as e:
			print("error",e)
			print(p,unknown,player_id,sc2type,sc2map)

			l=Games.objects.filter(path=p["path"])
			for ga in l:
				print(ga.date,ga.decision,ga.type)
			print("############END LISTE GAME IN DB FOR PATH##############")
			return 0

def getNewMatchHistory(path,alternate_path,lastMHupdate,server):
	""" return match in match history since last matchHistory lookup"""
	api=apiRequest(server)
	matchHistory=api.getMatchHistoryByPath(path)
	if type(matchHistory)!=dict and alternate_path!=None:
		print("trying alternate path with old endpoint")
		matchHistory=api.getMatchHistoryByPath(alternate_path)

	newgame={"SOLO":[],"notSOLO":[]}
	maxdate=lastMHupdate
	prevdate=0
	if type(matchHistory)==dict:
		for m in matchHistory["matches"]:
			date=m["date"]
			if date>maxdate:
				maxdate=date
			sc2type=m["type"]
			if date>lastMHupdate:
				if prevdate==m["date"]:
					print("error TWOO GAME SAME DATE")
				else:
					if sc2type=="SOLO":
						newgame["SOLO"].append((date,m))
					else:
						newgame["notSOLO"].append(m)
			prevdate=m["date"]

		return (newgame,maxdate)
	else:
		return ("error",maxdate)
def getDecision(deltawins,deltalosses,deltaties):
	if deltawins>=1 and deltalosses==0 and deltaties==0:
		return "WIN"
	elif deltalosses>=1 and deltawins==0 and deltaties==0:
		return "LOSS"
	elif deltaties>=1 and deltawins==0 and deltalosses==0:
		return "TIE"
	else:
		return "NA"
def lookForDiscrepancy(dmmr, dwin, dloss, dties, dcount, dlp):
	""" we check many possible configuration according to what
	 should be returned, False should never be returned """
	if dcount < 0 or dwin<0 or dloss<0:
		return ("reset", True)
	if dlp == 0:
		if dmmr == 0 and dwin == 0 and dloss == 0 and dcount == 0 and dties == 0:
			return ("nothing", True)
		else:
			print("dlp==0 while rest is not zero", dlp,
				  dmmr, dwin, dloss, dties, dcount)
			return ("pb", False)
	else:  # dlp!=0
		if dloss + dwin + dties != dcount:
			print("total game different from total race")
			return ("pb", False)
		else:  # dlp>0 and count=total
			if dcount == 0:
				if dmmr != 0:
					print("dcount=0 and not dmmr")
					return ("pb", False)
				else:
					print("all zero excpet dlp")
					return ("unrank", True)
			if dcount == 1:
				if dmmr >= 0 and dwin != 1 or dmmr <= 0 and dloss != 1:
					return ("pb with mmr and wins/loss", False)
				else:
					return ("ranked", True)
			else:
				if (dloss+dties==0 and dmmr <= 0) or (dwin == 0 and dties == 0 and dmmr >= 0):
					print("many games, and mmr issue vs lost/wins issue")
					return ("pb", False)
				else:
					print("many games, we have missed some")
					return("many", True)
	if dlp < 0:
		print("dlp<0")
		return ("dlp negatif", False)
	print("wtf")
	return ("wtf", False)
##
def updateOldPath(up=False,server="eu"):
	api=apiRequest(server)
	for league in League.objects.filter(server=server):
		lid=league.ladderid
		print("getting old endpoint",lid)
		l=api.getOldLadder(lid)
		if type(l)==dict:
			for p in l["ladderMembers"]:
				path=p["character"]["profilePath"]
				realm=p["character"]["realm"]
				legacy_id=p["character"]["id"]
				for pobj in Players.objects.filter(server=server,legacy_id=legacy_id,realm=realm):
					if up:
						pobj.alternate_path=path
						pobj.save()
					else:
						if pobj.alternate_path!=path:
							print("new alternate",path,"old_alternate",pobj.alternate_path,
								"current path",pobj.path)

def compareDbandHistory2(match_db,mh,p,pdb,msg,lid,deltaMMR,deltawins,deltalosses,deltaties):
	""" match_db is the games list without maps, we try to reconstruct the match
		history (ranked unranked ) by comparing with actual data from MH
	"""
	list_newgamesid=[]
	mh.sort(reverse=True) #most recent ones first
	#the first match should be the last_played_one from p
	"""
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
	"""
	lpfound=False
	for (date,m) in mh:
		islp=False
		isindb=False
		if date==p["last_played"] or date==p["last_played"]-1:
			islp=True

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
