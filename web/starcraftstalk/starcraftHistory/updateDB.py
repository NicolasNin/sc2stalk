from .apiRequest import apiRequest
from .models import League, Players, Games, Progamer
from django.db.models import  Max
from django.db import IntegrityError
from background_task import background
from django.db import transaction
from math import log10

def gettingLadderPlayers(liste_ladderid):
	""" from a liste of ladder_id we return a dict  of player from
	 the    sc2api with keys the ladderid"""
	api = apiRequest()
	api_players = {}
	print("Getting the ladder:", end=" ")
	for lid in liste_ladderid:
		print(lid, end="  ")
		ladder = api.getLadder(lid)
		if type(ladder) == dict:
			api_players[lid] = ladder["team"]
			print("success", end=" | ")
		else:
			#error in retrieving
			print(ladder[0])
	print("--")
	return api_players


def beautifulPlayer(player):
	"""player is a dict of bnet api from ladder["team"],return a
	 dict with keys such as rating wins etc from the dict of blizzard"""
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
	return p


def updatePlayer(pobj, p, lid,lastMHupdate):
	"""update the Player object pobj with the data from api"""
	pobj.name = p["name"]
	pobj.server = "eu"
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
	pobj.league = int(str(lid))
	pobj.lastmhupdate=lastMHupdate
	pobj.save()

@background(schedule=10)
def updateCycle():
	""" we get the ladders date from all the league, then
	 update each player when needed"""
	print("RUN AN UPDATE")
	print("-----------------------------------------------------")
	player_in_db = Players.objects.all()
	db_players = {}
	for player in player_in_db:
		db_players[player.idblizz] = player
	liste_ladderid = League.objects.all()

	player_from_api = gettingLadderPlayers(
		liste_ladderid)  # a dict on which we loop to update
	newgames=[]
	for lid in liste_ladderid:
		for player in player_from_api[lid]:
			p = beautifulPlayer(player)
			if str(p["id_blizz"]) in db_players:
				pdb = db_players[str(p["id_blizz"])]
				#big loop start here
				(lastMHupdate,newgamesp)=addNewGamePlayer(pdb,p,lid)
				newgames.extend(newgamesp)
			#	print("cycle",lastMHupdate)
				updatePlayer(pdb, p, lid,lastMHupdate)
			else:
				updatePlayer(Players(),p,lid,0)
#				Players(name=p["name"], server="eu", rating=p["rating"], wins=p["wins"],
#				 loses=p["losses"], ties=p["ties"], last_played=p["last_played"],
#				  join_time=p["join_time"], legacy_id=p["legacy_id"],
#						realm=p["realm"], path=p["path"], clan_id=p["clan_id"],
#						 idblizz=p["id_blizz"], mainrace=p["mainrace"], battletag=p["battletag"],
#						  race_count=p["race_count"], points=p["points"],
#						current_win_streak=p["current_win_streak"], league=int(str(lid)),
#						lastMHupdate=0).save()
	#we look for opponent of newgames
	print(newgames)
	findOpList(newgames,save=True)

	print("update finished")

def addNewGamePlayer(pdb,p,lid):
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
	maxdate=Players.objects.filter(path=p["path"]).aggregate(Max('lastmhupdate'))["lastmhupdate__max"]
	if b==True and msg!="nothing":
		print("-----------------------------")
		lmhu=0
		if maxdate!=None:
			lmhu=maxdate
		(newinMH,maxdate)=getNewMatchHistory(p["path"],pdb.alternate_path,lmhu)
		#print("indaddNew",maxdate,end= "   ")
		if newinMH!="error":
			#we add the notsolo
			for g in newinMH["notSOLO"]:
				returngame=addGamesinDB(p,g["map"],g["type"],g["decision"],
					g["speed"],g["date"],deltaMMR,msg,lid,player_id,True)
				list_newgamesid.append(returngame)

			#we add the solo match or update the one in db
			nomapsgame=Games.objects.filter(path=p["path"],map="")
			otherlist=compareDbandHistory(nomapsgame,newinMH["SOLO"],p,pdb,msg,lid,
					deltaMMR,deltawins,deltalosses,deltaties)

			list_newgamesid.extend(otherlist)
		else:#pas de match history on ajoute l'unique game sans map
			#ranked ou many=> partie ranked, on ajoute le count
			if msg=="ranked" or msg=="many":
				msg=str(deltacount)
			returngame=addGamesinDB(p,"","SOLO",getDecision(deltawins,deltalosses,deltaties),"FASTER",p["last_played"],
				deltaMMR,msg,lid,player_id)
			list_newgamesid.append(returngame)
	return (maxdate,list_newgamesid)

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
		elif match_db.filter(date=date+1).exists():
			mdb=match_db.filter(date=date+1)[0]
			mdb.map=m["map"]
			mdb.decision=m["decision"]
			mdb.date=date
			mdb.save()
			print("we updated the date to the one in MH",p["path"],date)
		else:
			# we dont know who played that we might know after looking at LP and dc
			returngame=addGamesinDB(p,m["map"],m["type"],m["decision"],m["speed"],m["date"],
				deltaMMR,"Unknown",lid,pdb.idplayer,True)
			list_newgamesid.append(returngame)
	return list_newgamesid

def addGamesinDB(p,sc2map,sc2type,decision,speed,date,deltaMMR,ranked,lid,player_id,unknown=False):
	print(p["path"],date,unknown,lid,deltaMMR,decision)
	sc2map=sc2map[0:44]
	try:
		with transaction.atomic():
			if unknown:#in those game we dont know the player but we know the map (from MH)
				g=Games(server="eu",map=sc2map,type=sc2type,speed=speed,date=date,ranked=ranked,
				  path=p["path"],decision=decision,current_league=lid)

				g.save()

				return g.pk
			else:
				#In those games we know the player, map might be empty (from MH and/or LP)
				g=Games(server="eu",map=sc2map,type=sc2type,speed=speed,date=date,current_mmr=p["rating"],
				  current_rank=p["current_rank"],current_league=lid,current_win=p["wins"],current_losses=p["losses"],
				  current_ties=p["ties"],current_points=p["points"],player_id=player_id,ranked=ranked,
				  path=p["path"],current_win_streak=p["current_win_streak"],guessmmrchange=deltaMMR,
				  lastplayed_date=p["last_played"],decision=decision)
				g.save()

				return g.pk
	except 	IntegrityError as e:
			print("error",e)
			print(p,unknown,player_id,sc2type,sc2map)

			l=Games.objects.filter(path=p["path"])
			for ga in l:
				print(ga.date,ga.decision,ga.type)
			print("############END LISTE GAME IN DB FOR PATH##############")
			return 0

def getNewMatchHistory(path,alternate_path,lastMHupdate):
	""" return match in match history since last matchHistory lookup"""
	api=apiRequest()
	matchHistory=api.getMatchHistoryByPath(path)
	if type(matchHistory)!=dict and alternate_path!=None:
		print("trying alternate path with old endpoint")
		matchHistory=api.getMatchHistoryByPath(alternate_path)

	newgame={"SOLO":[],"notSOLO":[]}
	maxdate=lastMHupdate
	if type(matchHistory)==dict:
		for m in matchHistory["matches"]:
			date=m["date"]
			if date>maxdate:
				maxdate=date
			sc2type=m["type"]
			if date>lastMHupdate:
				if sc2type=="SOLO":
					newgame["SOLO"].append((date,m))
				else:
					newgame["notSOLO"].append(m)
		return (newgame,maxdate)
	else:
		return ("error",maxdate)
def getDecision(deltawins,deltalosses,deltaties):
	if deltawins==1:
		return "WIN"
	elif deltalosses==1:
		return "LOSS"
	elif deltaties==1:
		return "TIE"
	else:
		return "NA"
def lookForDiscrepancy(dmmr, dwin, dloss, dties, dcount, dlp):
	""" we check many possible configuration according to what
	 should be returned, False should never be returned """
	if dcount < 0:
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


def updateOldPath(up=False):
	api=apiRequest()
	for league in League.objects.all():
		lid=league.ladderid
		print("getting old endpoint",lid)
		l=api.getOldLadder(lid)
		if type(l)==dict:
			for p in l["ladderMembers"]:
				path=p["character"]["profilePath"]
				legacy_id=p["character"]["id"]
				for pobj in Players.objects.filter(legacy_id=legacy_id):
					if up:
						pobj.alternate_path=path
						pobj.save()
					else:
						if pobj.alternate_path!=path:
							print("new alternate",path,"old_alternate",pobj.alternate_path,
								"current path",pobj.path)
##########Opp lookup#################
def findOpList(listgames,save=False):
	for g in listgames:
		print(g)
		findOppNewgame(Games.objects.get(pk=g),save)
def findOppNewgame(g,save=False):
	""" we do the basic, no same id, same date, same type, then we check map and decision"""
	base_game=Games.objects.exclude(idgames=g.idgames).filter(type=g.type
		,date=g.date,guessopgameid__isnull=True)
	if len(base_game)==1:
		opgame=base_game[0]
		if checkGamesIsOpponent(g.decision,g.map,opgame):
			if save:
				g.guessopgameid=opgame.idgames
				if opgame.player_id!=None:
					g.guessopid=opgame.player_id

				opgame.guessopgameid=g.idgames

				if g.player_id!=None:
					opgame.guessopid=g.player_id
				opgame.save()
				g.save()
				print(g.date,g.idgames,opgame.idgames)
			else:
				print(g.date,g.idgames,opgame.idgames)
			return (1,0)
	elif len(base_game)>1:
		print("more than 1 date match")
		return (0,1)
	return (0,0)
def updateDbOpponent(save=False,datelimit=0):
	allgames=Games.objects.all().exclude(guessopgameid__isnull=False).filter(date__gt=datelimit)
	c=0
	ok=0
	okplus=0
	for g in allgames:
		(un,plus)=findOppNewgame(g,save)
		ok+=un
		okplus+=plus
		c+=1
		print(c,ok,okplus)
	print(c,ok,okplus)
def checkGamesIsOpponent(decision,sc2map,gameop):
	opmap=gameop.map
	if sc2map=="" or opmap=="":
		ismapok=True
	else:
		if  sc2map==opmap:
			ismapok=True
		else:
			return False #if map="" we cant decide
	#idem for decision if its NA on either side we are cant decide
	opdecision=gameop.decision
	otherdecision=oppositeDecision(decision)
	if decision=="NA" or opdecision=="NA":
		isdecisionok=True
	else:
		if opdecision==otherdecision:
			isdecisionok=True
		else:
			return False
	return True

def oppositeDecision(decision):
	if decision=="WIN":
		return "LOSS"
	if decision=="LOSS":
		return "WIN"
	if decision=="TIE" or "BAILER" or "NA" or "WATCHER":
		return decision

####################################


def FindAllOpponent():
	allgames=Games.objects.all().exclude(guessopgameid__isnull=False)
	c=0
	cok=0
	for g in allgames:
		cok+=LookForOpponentBygames(g)
		c+=1
		print(c,cok)
	print(c,cok)

def FindAllOpponentNomap():
	allgames=Games.objects.all().exclude(guessopgameid__isnull=False)
	c=0
	cok=0
	for g in allgames:
		cok+=LookForOpponentNomap(g)
		c+=1
		#print(c,cok)
	print(c,cok)
		#print("-----------------")
def LookForOpponentNomap(g):
	idgame=g.idgames
	date=g.date
	decision=g.decision
	sc2map=g.map
	sc2type=g.type
	guessmmrchange=g.guessmmrchange
	games=Games.objects.exclude(idgames=idgame).filter(type=sc2type
		,date=date,guessopgameid__isnull=True)
	games2=games.exclude(decision=decision)
	if len(games)==1 and len(games2)==0 and sc2type=="SOLO":
		if sc2map!=""  and sc2map==games[0].map :
			print(games[0].idgames)
			print(date,idgame)
			return 1
		else:
			return 0
	else:
		return 0

def LookForOpponentEZ(g):
	idgame=g.idgames
	date=g.date
	decision=g.decision
	sc2map=g.map
	sc2type=g.type
	guessmmrchange=g.guessmmrchange
	games=Games.objects.exclude(idgames=idgame,guessopgameid__isnull=False).filter(type=sc2type
		,date=date)

	if len(games)==1:
		if games[0].map==sc2map and games[0].decision==oppositeDecision(decision):
			if True: #games[0].guessmmrchange!= None and guessmmrchange != None :
				if True:#abs(games[0].guessmmrchange +guessmmrchange)<=1:
					g.guessopgameid=games[0].idgames

					if games[0].player_id!=None:
						g.guessopid=games[0].player_id
					g.save()
					games[0].guessopgameid=idgame
					if g.player_id!=None:
						games[0].guessopid=g.player_id
					games[0].save()

					print(idgame,date)
					return 1
	return 0

def LookForOpponent(idgame,date,decision,sc2map,sc2type):
	""" we look for the opponent of the game with id idgame
		if map="" this means we have less data to find match
		moreover the date could be "lp" in this case so we should
		also look at date=lp-1 this might add uncertainty to result in case
		of mutliple same date within 1sec
	"""
	if map=="":
		print("")
	else:
		games=Games.objects.exclude(idgames=idgame).filter(guessopgameid__isnull=True,type=sc2type)
		### if 2 date are equal and other stuff are good
		gamesdate=games.filter(date=date)
		if len(gamesdate)!=0 :
			count=0
			for g in gamesdate:

				#print("potential",g.idgames)
				if checkGamesIsOpponent(date,decision,sc2map,sc2type,g):
					count+=1
			if count>1:
				print("many matches",count,date,idgame)

		#on va chercher avec date-1 car on a LP
		# si opmap=="" alors ca sert a rien car lui aussi a LP
		# si opmap!="" alors ok
		#=> donc on cherche a matcher date-1 avec un map!=""





def poolOfPossibleOpponnent(game):
	"""return a queryset of games that might be opponent according to date
		since a games without map can have a date that is slighly off
		ie if map="" we can have lastplayed_date==date+1
		so we have to look into date-1
	"""

	gdate=Games.objects.filter(type=game.type,date=g.date)
	c=0
	if len(gdate>2):
		c+=1
	print(c)
	#for the moment we dont care about the shift

"""
for p in Players.objects.all():
	path=p.path
	maxdate=Games.objects.filter(path=path).aggregate(Max('date'))["date__max"]
	if maxdate!=None:
		p.lastmhupdate=maxdate
		p.save()
"""

def getMagicK(deltapoints):
	if deltapoints<=30  and deltapoints>=20:
		return 46
	if deltapoints>30:
		return 46+0.5*(deltapoints-30)
	else:
		return 46-0.5*(deltapoints-20)

def getMMRmagic(newMMR1,deltammr1):
	return getMMR(newMMR1,deltammr1,getMagicK(abs(deltammr1)))

def getMMR(newMMR1,deltammr1,K):
	if deltammr1==0:
		print("000000000")
		return 0
	if deltammr1>0:
		w=1
	else:
		w=0
	p=w-deltammr1/K

	if abs(deltammr1)>K or p==0:
	#	print(deltammr1)
		return 0
	if 1/p-1<=0:
	#	print(deltammr1,w,p)
		return 0
	return newMMR1+800*log10(1/p-1)
"""
r=Games.objects.all()
print(len(r))
r1=Games.objects.exclude(idgames=g.idgames)
print(len(r1))
r2=Games.objects.exclude(guessopgameid__isnull=False)
print(len(r2))
r11=r1.exclude(guessopgameid__isnull=False)
print(len(r11))
r3=Games.objects.exclude(idgames=g.idgames).exclude(guessopgameid__isnull=False)
print(len(r3))
r4=Games.objects.exclude(guessopgameid__isnull=False).exclude(idgames=g.idgames)
print(len(r4))
r5=Games.objects.exclude(idgames=g.idgames).filter(guessopgameid__isnull=True)
print(len(r5))
"""
