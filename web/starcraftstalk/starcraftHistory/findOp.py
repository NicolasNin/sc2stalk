from .models import Games
def checkReciprocal(founddict,save=False):
	""" we take a dict of games with games as key
		and we check that the finding in reciproqual
	"""
	for g1 in founddict:
		g2=founddict[g1]
		if g2 not in founddict and g2!="":
			#we have to comoute it maybe again
			(a,b,findee)=findOppNewgame(g2)
		elif g2!="":
			findee=founddict[g2]
		else:
			findee="space "
		if findee==g1:
			print(g1,g2,g1.date,"match reciproqual")
			if save:
				exchangeId(g1,g2)
		else:
			print(g1,g2,g1.date,"not reciproqual")
def findOpListObject(listobject,save=False):
	total=0
	ok=0
	many=0
	found={}
	for g in listobject:
		(a,b,opgame)=findOppNewgame(g,save)
		if opgame!="":
			found[g]=opgame
		total+=1
		ok+=b
		many+=a
	print("total",total," found",many," many",ok)
	return found
def findOpList(listgames,save=False):
	total=0
	ok=0
	found={}
	for g in listgames:
		print(g)
		(a,b,opgame)=findOppNewgame(Games.objects.get(pk=g),save)
		total+=a
		ok+=b
	print("total",total," found",ok)
def findOppNewgame(g,save=False):
	""" we do the basic, no same id, same date, same type, then we check map and decision"""
	if g!=0:
		base_game=Games.objects.exclude(idgames=g.idgames).filter(type=g.type
		,date=g.date,guessopgameid__isnull=True)
	else:#this means that addgameindDBfailed
		return (0,0,"")
	if len(base_game)==1:
		opgame=base_game[0]
		if checkGamesIsOpponent(g.decision,g.map,opgame):
			if save:
				exchangeId(g,opgame)
			print(g.date,g.idgames,opgame.idgames)
			return (1,0,opgame)
	elif len(base_game)>1:
		if g.map!="" and len(base_game.filter(map=""))==0:
			samemap=base_game.filter(map=g.map)
			if len(samemap)==1:
				opgame=samemap[0]
				if checkGamesIsOpponent(g.decision,g.map,opgame):
					if save:
						exchangeId(g,opgame)
					print(g.date,g.idgames,opgame.idgames)
					return(1,0,opgame)
				else:
					print("more thand 2date, only 1 map, decision fail",g.date,g.idgames)
			else:
				print("more than 2 date, more than 1 map",g.date,g.idgames)
				return(0,1,"")
		print("more than 2 date match",len(base_game),g.date,g.idgames)

		return (0,1,"")
	return (0,0,"")
def exchangeId(g1,g2):
	g1.guessopgameid=g2#.idgames
	if g2.player_id!=None:
		g1.guessopid=g2.player
	g2.guessopgameid=g1#.idgames
	if g1.player_id!=None:
		g2.guessopid=g1.player
	g2.save()
	g1.save()
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
