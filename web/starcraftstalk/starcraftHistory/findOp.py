from .models import Games
from mmr import *
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
				#we look at the mmr consistency if there is only one its good
				mmrmatch=checkMMRconsistencyGroup(g,base_game)
				if len(mmrmatch)==1:
					print(g.date,g.idgames,mmrmatch[0].idgames,"mmr decided, many maps")
					return(1,0,mmrmatch[0])
				else:
					print("more than 2 date, more than 1 map,mmrdontmatch",
					len(mmrmatch),g.date,g.idgames)
					return(0,1,"")
		else:
			#we look at mmr when map failed
			mmrmatch=checkMMRconsistencyGroup(g,base_game)
			if len(mmrmatch)==1:
				print(g.date,g.idgames,mmrmatch[0].idgames,'mmr decision not map')
				return(1,0,mmrmatch[0])
			else:
				print("nor mmr nor map can decide",len(base_game),
				      len(mmrmatch),g.date,g.idgames)
				return(0,1,"")
		return (0,1,"")
	return (0,0,"")
def checkMMRconsistencyGroup(g1,listegame):
	OK=[]
	if g1.current_mmr==None:
		return []
	for g in listegame:
		if g.current_mmr!=None:
			if checkMMRconsistency(g1,g):
				OK.append(g)
	return OK
def checkMMRconsistency(g1,g2):
	"""  we lookt at mmr in case of multiple match"""
	MMR1=int(g1.current_mmr)
	deltammr1=g1.guessmmrchange
	MMR2=int(g2.current_mmr)
	deltammr2=g2.guessmmrchange
	if abs(deltammr2+deltammr1)<=1:
		ddmmr=(deltammr1-deltammr2)/2
		if deltammr1>0:
			deltammr1=abs(ddmmr)
			deltammr2=-abs(ddmmr)

		else:
			deltammr1=-abs(ddmmr)
			deltammr2=abs(ddmmr)
		estimmmr2=getMMRmagic(MMR1,deltammr1)
		estimmmr1=getMMRmagic(MMR2,deltammr2)
		d1=estimmmr1-MMR1
		d2=estimmmr2-MMR2

		if abs(d1)>50 or abs(d2)>50 or abs(d1+d2)>1 :
			print(g1.date,g1.idgames,g2.idgames,estimmmr1-MMR1,
			estimmmr2-MMR2, deltammr2)
			return False
		else:
			return True
	else:
		return False
def checkAllMMR(liste):
	total=0
	a=0
	b=0
	c=0
	#	for g in  Games.objects.filter(guessopgameid__isnull=False,
	#	guessopgameid__guessmmrchange__isnull=False,
	#	guessmmrchange__isnull=False):
	for (k,g) in enumerate(liste):
		(d,e,f)=checkMMRconsistency(g,g.guessopgameid)
		a+=d
		b+=e
		c+=f
		total+=1
	print(total,a,b,c)
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
