from .views import renderrandomtitle
from ..models import Players,Games,Global
import datetime,time
import pytz
import json
def getTimeDelta(ts):
	dif=int(time.time())-ts
	print(dif)
	if dif>86400:
		return	str(datetime.timedelta(seconds=dif)).split("day")[0] +" days"
	else:
		return	str(datetime.timedelta(seconds=dif))
def getPromotionWindows(server):
	""" return the start and end of promotion windows for today
	in UTC as a timestamp"""

	if server=="us":
		tz= pytz.timezone('America/New_York')
	else:
		tz= pytz.timezone('Europe/Paris')
	#we are cest time on the server
	cest= pytz.timezone('Europe/Paris')
	now=pytz.utc.localize(datetime.datetime.now())
	now_local=now.astimezone(tz)
	#promotion is between 21h each day
	if now_local.hour>=21:
		start=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		end=(start+datetime.timedelta(days=1))
	else:
		end=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		start=(end-datetime.timedelta(days=1))
	return (start.timestamp(),end.timestamp())
def getListePlayerWcs2(server="eu",thresh=6300):
	if server=="us":
		thresh=6000
	playerwcs=Players.objects.filter(wcs=1,
	smurf__wcsregion=server,season=32,server=server,
		rating__gte=thresh).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	return playerwcs

def getNumberGamesAt(date,playerid):
	""" we look for the first game with win loss ties date BEFORE the date"""
	g=Games.objects.filter(player=playerid,date__lte=date).order_by("-date").first()
	if g!=None:
		return (g.current_win,g.current_losses,g.current_ties)
	else:
		g=Games.objects.filter(player=playerid,date__gte=date).order_by("date").first()
		dloss=0
		dwin=0
		dtie=0
		if g.decison=="WIN":
			dwin+=1
		if g.decison=="LOSS":
			dloss+=1
		if g.decison=="TIE":
			dtie+=1
		if g!=None:
			return (g.current_win-dwin,g.current_losses-dloss,g.current_ties-dtie)
	return(0,0,0)
def getDates(start,server):
	date=[]
	if server=="us":
		tz= pytz.timezone('America/New_York')
	else:
		tz= pytz.timezone('Europe/Paris')
	start=tz.localize(start)
	date.append(start.timestamp())
	date.append(start.timestamp()+86400)
	date.append(start.timestamp()+86400)
	date.append(start.timestamp()+86400)
	date.append(start.timestamp()+10800)
	return date
def wcs(request,server):
	if server=="us":
		timetoadd=-4*3600
		html="starcraftHistory/wcsus.html"
		thresh=6000
		lastday=datetime.datetime(2017,6,4,23,59)
	else:
		html="starcraftHistory/wcseu.html"
		timetoadd=2*3600
		thresh=6300
		startdate=datetime.datetime(2017,5,25,21)
		getDates(startdate,"eu")
		lastday=datetime.datetime(2017,6,4,23,59)


	(start,end)=getPromotionWindows(server)
	""" we get the top GM player who are from the good wcs region
	with a good name (ie their true name)"""
	lastQualif=8#might be 16 or other in 2017 its 8 on eu
	"""
	playerwcs=Players.objects.filter(
	smurf__wcsregion=server,season=32,server=server,
		rating__gte=thresh).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	"""
	playerwcs=getListePlayerWcs2(server,thresh)
	if len(playerwcs)>=7:
		basemmr=int(playerwcs[7]['rating'])
	else:
		basemmr=0

	num=1
	listegoodplayerid=[]
	gamesbetween=Games.objects.filter(server=server,date__range=(start,end),player__wcs=1,type="SOLO")
	for p in playerwcs:
		p["numgames"]=len(gamesbetween.filter(player_id=p["idplayer"]))
		(win,loss,ties)=getNumberGamesAt(start,p["idplayer"])
		print(p["numgames"],p["wins"]-win,p["loses"]-loss)
		listegoodplayerid.append(p["idplayer"])
		p["num"]=num
		if num<=lastQualif:
			p["qualif"]="qualif"
		else:
			p["qualif"]="notqualif"
		num+=1
		p["LP"]=getTimeDelta(p["last_played"])
		if p["smurf__pseudo"]!=None:
			p["name_human"]=p["smurf__pseudo"]+"("+p["name"] +")"
		else:
			p["name_human"]=p["name"]
	#store this list
	v=Global.objects.filter(name="listewcsusplayer").update(value=json.dumps(listegoodplayerid))

	#recent games of thoses players last 12h
	DELTATIME=3600*6
	#count the game between promotion

	recentwcsgames=Games.objects.filter(server=server,
	date__gte=time.time()-DELTATIME,
	player__in=listegoodplayerid).select_related(
	"player").order_by(
	"-date").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player",
	"guessopid__mainrace","player__mainrace")
	for g in recentwcsgames:
		g["date_human"]=datetime.datetime.fromtimestamp(
		g["date"]+timetoadd).strftime('%d %b %H:%M')
		if g["guessopid__smurf__pseudo"]!= None:
			g["guessopid__name"]=g["guessopid__smurf__pseudo"]
		if g["guessopid__name"]==None and g["guessopgameid__path"]!=None :
			g["guessopid__name"]=g["guessopgameid__path"].split('/')[-1]

	timetowait=str(lastday-
	datetime.datetime.fromtimestamp(int(time.time())))
	timetopromotion=str(datetime.timedelta(seconds=end-int(time.time())))
	print(timetopromotion,end,end-int(time.time()),server)
	context={"players":playerwcs,"basemmr":-basemmr,"games":recentwcsgames,
	"wait":timetowait,"promotime":timetopromotion,"server":server}
	return renderrandomtitle(request, html,context)

def graphmmr(request,server):
	if server=="us":
		thresh=6000
	else:
		thresh=6300
	deb=time.time()
	leagueid=39 #inhard cause im lazy
	playerwcs=Players.objects.filter(server=server,smurf__wcsregion=server,
	rating__gte=thresh,season=32,wcs=1).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")

	listegoodplayerid=[]
	listemmr=[]
	mmr8=0
	num=1
	for p in playerwcs:
		####HACK we should add a flag wcs to player in db
		name2=p["name"].lower().split("#")[0]
		if name2[0:6]=="liquid":
			name2=name2[6:]
		p["truename"]= name2==p["smurf__pseudo"].lower()
		if name2=="thermy" and p["smurf__pseudo"].lower()=="uthermal":
			p["truename"]=True
		######################
		if p["truename"]:
			listegoodplayerid.append(p["idplayer"])
			listemmr.append(p["rating"])
			if num==8:
				mmr8=p["rating"]
			num+=1
	datestart=int(time.time())-3600*12


	g2=[]
	listmmrstart=[]
	curent_pos={}
	for playerid in listegoodplayerid:
		player=Players.objects.get(pk=playerid)
		mmrstart=getMMRatDate(player,datestart)
		listmmrstart.append((int(mmrstart),playerid))

		g2.append({"date":datestart,"player__name":player.name,
		"current_mmr":mmrstart})
		g2.extend(Games.objects.filter(server=server,player=player,date__gte=datestart).order_by("date").values(
			"player__name","current_mmr","date","guessopid__name",
			"guessopid__mainrace","guessmmrchange"))
		g2.append({"date":int(time.time()),"player__name":player.name,
		"current_mmr":player.rating})
		listmmrstart.sort(reverse=True)
	recentgames=Games.objects.filter(server=server,player__in=listegoodplayerid,
	date__gte=datestart).order_by("date")
	m8=[]
	m9=[]
	try:
		m8.append({"current_mmr":listmmrstart[7][0],"date":datestart,"player__name":"mmr8"})
		m9.append({"current_mmr":listmmrstart[8][0],"date":datestart,"player__name":"mmr9"})
		current8=listmmrstart[7]
		current9=listmmrstart[8]
		minmmr=listmmrstart[-1][0]
		for g in recentgames:
			newmmr=int(g.current_mmr)
			oldmmr=int(g.current_mmr)-g.guessmmrchange
			try:
				listmmrstart.remove((oldmmr,g.player.idplayer))
			except ValueError:
				for (mmr,pid) in listmmrstart:
					if pid==g.player.idplayer:
						listmmrstart.remove((mmr,pid))

				print(listmmrstart)
				print((oldmmr,g.player.idplayer))
			listmmrstart.append((newmmr,g.player.idplayer))
			listmmrstart.sort(reverse=True)
			if listmmrstart[-1][0]<minmmr:
				minmmr=listmmrstart[-1][0]
			if listmmrstart[7]!=current8:
				current8=listmmrstart[7]
				m8.append( {"current_mmr":listmmrstart[7][0],"date":g.date,"player__name":"mmr8"})
			if listmmrstart[8]!=current9:
				current9=listmmrstart[8]
				m9.append({"current_mmr":listmmrstart[8][0],"date":g.date,"player__name":"mmr9"} )

		m8.append({"current_mmr":listmmrstart[7][0],"date":time.time(),"player__name":"mmr8"})
		m8.extend(g2)
	except IndexError:
		print("indexerror")

	#m9.append({"current_mmr":listmmrstart[8][0],"date":time.time(),"player__name":"mmr9"})
	#g2.extend(m9)
	context={"games":m8,"min":max(minmmr,mmr8-200),"max":7000,"name":"test","mmr8":mmr8,
	"listemmr":listemmr,"mmrtop":mmr8+100,"mmrbottom":mmr8-200,"server":server}
	return renderrandomtitle(request, 'starcraftHistory/graphtest3.html',context)

def getMMRatDate(player,date):
	g=Games.objects.filter(date__lte=date,player=player,
	current_mmr__isnull=False).order_by("-date").first()
	if g!=None:
		return g.current_mmr
	else:
		g=Games.objects.filter(date__gte=date,player=player,
		current_mmr__isnull=False).order_by("date").first()
		if g!=None:
			return g.current_mmr
	return player.rating

def wcsold(request):
	return wcs(request,server="eu")
