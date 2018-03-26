from .views import renderrandomtitle
from ..models import Players,Games,Global
from django.db.models import Max,Min,Sum,Count
import datetime,time
import pytz
import json

##################################
#DEFINE WCS PARAMETER

#EU
eutz=pytz.timezone('Europe/Paris')
ustz=pytz.timezone('America/New_York')
euconfig={
"startdate":eutz.localize(datetime.datetime(2018,3,20,21)),
"lastday":	eutz.localize(datetime.datetime(2018,4,1,23,59)),
"lastQualif":4,
"thresh":6300		}
usconfig={
"startdate":ustz.localize(datetime.datetime(2018,3,20,21)),
"lastday":	ustz.localize(datetime.datetime(2018,4,1,23,59)),
"lastQualif":4,
"thresh":6000		}
wcsRegion={"eu":"EU","us":"NA"}
#############################
def NowDateTimeRegion(region=""):
	#ret
	if region=="cest":
		tz= pytz.timezone('Europe/Paris')
	elif region=="pdt":
		tz= pytz.timezone('America/New_York')
	else:
		tz=pytz.utc
	utcnow=pytz.utc.localize(datetime.datetime.utcnow())
	utcnow=utcnow-datetime.timedelta(microseconds=utcnow.microsecond)
	return utcnow.astimezone(tz)

def getTimeDelta(ts):
	dif=int(time.time())-ts
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
	#we are utc time on the server
	#cest= pytz.timezone('Europe/Paris')
	utc = pytz.utc
	now=pytz.utc.localize(datetime.datetime.now())
	now_local=now.astimezone(utc)
	#promotion is between 21h each day
	if now_local.hour>=21:
		start=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		end=(start+datetime.timedelta(days=1))
	else:
		end=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		start=(end-datetime.timedelta(days=1))
	return (start.timestamp(),end.timestamp())
def getListePlayerWcs2(server="eu",thresh=6300):
	currentseason=int(Global.objects.filter(name="currentseason")[0].value)
	if server=="us":
		thresh=usconfig["thresh"]
	playerwcs=Players.objects.filter(wcs=1,
	smurf__wcsregion=wcsRegion[server],season=currentseason,server=server,
		rating__gte=thresh).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	return playerwcs


def getNumberGamesAt(date,playerid):
	""" we look for the first game with win loss ties date BEFORE the date"""
	g=Games.objects.filter(player=playerid,date__lte=date).order_by("-date").first()

	if g!=None:
		return (g.current_win,g.current_losses,g.current_ties,g.current_mmr)
	else:
		if hasattr(g, 'decision'):

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
				if g.guessmmrchange!=None:
					return (g.current_win-dwin,g.current_losses-dloss,g.current_ties-dtie,
					g.current_mmr-g.guessmmrchange)
				else:
					return (g.current_win-dwin,g.current_losses-dloss,g.current_ties-dtie,
					g.current_mmr)
	return(0,0,0,0)
def getDates(start,server):
	date=[]
	#if server=="us":
	#		tz= pytz.timezone('America/New_York')
	#	else:
	#		tz= pytz.timezone('Europe/Paris')
	#	start=tz.localize(start)
	date.append(start.timestamp())
	date.append(start.timestamp()+86400)
	date.append(start.timestamp()+2*86400)
	date.append(start.timestamp()+3*86400)
	date.append(start.timestamp()++3*86400+10800)
	return date
def wcs(request,server):
	if server=="us":
		tz= pytz.timezone('America/New_York')
		timetoadd=-4*3600
		html="starcraftHistory/wcsus.html"
		thresh=6000
		lastday=usconfig["lastday"]
	else:
		html="starcraftHistory/wcseu.html"
		tz= pytz.timezone('Europe/Paris')
		timetoadd=2*3600##SHITTY HAC
		thresh=euconfig["thresh"]
		startdate=euconfig["startdate"]
		getDates(startdate,"eu")
		lastday=euconfig["lastday"]
	lastQualif=4

	timetowait=str(lastday-NowDateTimeRegion())

	(start,end)=getPromotionWindows(server)

	#might be 16 or other in 2017 its 8 on eu
	"""
	playerwcs=Players.objects.filter(
	smurf__wcsregion=server,season=33,server=server,
		rating__gte=thresh).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	"""
	playerwcs=getListePlayerWcs2(server,thresh)
	if len(playerwcs)>=lastQualif:
		basemmr=int(playerwcs[lastQualif-1]['rating'])
	else:
		basemmr=0

	num=1
	listegoodplayerid=[]
	gamesbetween=Games.objects.filter(server=server,date__range=(start,end),
	player__wcs=1,type="SOLO").exclude(ranked="unrank")
	for p in playerwcs:

	#	(win,loss,ties,mmr)=getNumberGamesAt(start,p["idplayer"])
	#	print(p["numgames"],p["wins"]-win,p["loses"]-loss)
		p["numgames"]=len(gamesbetween.filter(player_id=p["idplayer"]))
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
	v=Global.objects.filter(name="listewcs"+server+"player").update(value=json.dumps(listegoodplayerid))

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


	#	timetostream=lastday-datetime.datetime.fromtimestamp(7200+int(time.time()))
	timetostream=datetime.timedelta(seconds=10)
	if (timetostream<datetime.timedelta(seconds=0)):
		timetostream="LIVE"
	else:
		timetostream="in "+str(timetostream)
	timetopromotion=str(datetime.timedelta(seconds=end-int(time.time())))
	print(timetopromotion,end,end-int(time.time()),server)
	context={"players":playerwcs,"basemmr":-basemmr,"games":recentwcsgames,
	"wait":timetowait,"promotime":timetopromotion,"server":server,
	"stream":timetostream}
	return renderrandomtitle(request, html,context)

def graphmmr(request,server):
	if server=="us":
		thresh=6000
	else:
		thresh=6300
	deb=time.time()
	current_seasonDB=Global.objects.filter(name="currentseason")[0].value
	playerwcs=Players.objects.filter(server=server,smurf__wcsregion=wcsRegion[server],
	rating__gte=thresh,season=current_seasonDB,wcs=1).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	lastQualif=4
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
			if num==lastQualif:
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
		m8.append({"current_mmr":listmmrstart[lastQualif-1][0],"date":datestart,"player__name":"mmr4"})
		m9.append({"current_mmr":listmmrstart[lastQualif][0],"date":datestart,"player__name":"mmr5"})
		current8=listmmrstart[lastQualif-1]
		current9=listmmrstart[lastQualif]
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
			if listmmrstart[lastQualif-1]!=current8:
				current8=listmmrstart[lastQualif-1]
				m8.append( {"current_mmr":listmmrstart[lastQualif-1][0],"date":g.date,"player__name":"mmr4"})
			if listmmrstart[lastQualif]!=current9:
				current9=listmmrstart[lastQualif]
				m9.append({"current_mmr":listmmrstart[lastQualif-1][0],"date":g.date,"player__name":"mmr5"} )

		m8.append({"current_mmr":listmmrstart[lastQualif-1][0],"date":time.time(),"player__name":"mmr4"})
		m8.extend(g2)
	except IndexError as e:
		print("indexerror",e)
		print(listmmrstart,listegoodplayerid)

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

def wcsdata(request,server):
	deb=time.time()
	if server=="us":
		timetoadd=-4*3600
		html="starcraftHistory/wcseudata.html"
		thresh=5500
		startdate=datetime.datetime(2017,6,1,21)
		dates=getDates(startdate,"us")
		lastday=datetime.datetime(2017,6,4,23,59)
	else:
		html="starcraftHistory/wcseudata.html"
		timetoadd=2*3600
		thresh=6300
		startdate=datetime.datetime(2017,5,25,21)
		dates=getDates(startdate,"eu")
		lastday=datetime.datetime(2017,5,28,23,59)

	(start,end)=getPromotionWindows(server)
	print((dates[1]-time.time())/60)

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
	if len(playerwcs)>=lastQualif:
		basemmr=int(playerwcs[lastQualif-1]['rating'])
	else:
		basemmr=0
	print(basemmr)
	num=1
	listegoodplayerid=[]
	gamesbetween=Games.objects.filter(server=server,date__range=(dates[0],dates[4]),player__wcs=1,type="SOLO")
	for p in playerwcs:
		n=[]
		n.append(getNumberGamesAt(dates[0],p["idplayer"]))
		n.append(getNumberGamesAt(dates[1],p["idplayer"]))
		n.append(getNumberGamesAt(dates[2],p["idplayer"]))
		#n.append(getNumberGamesAt(dates[3],p["idplayer"]))
		n.append(getNumberGamesAt(dates[4],p["idplayer"]))
		for i in range(3):
			p["mmr"+str(i+1)]=int(n[i+1][3])-int(n[i][3])
			p["win"+str(i+1)]=n[i+1][0]-n[i][0]
			p["loss"+str(i+1)]=n[i+1][1]-n[i][1]
			p["ties"+str(i+1)]=n[i+1][2]-n[i][2]
			p["total"+str(i+1)]=n[i+1][0]-n[i][0]+n[i+1][1]-n[i][1]+n[i+1][2]-n[i][2]
		p["totalwin"]=p["win1"]+p["win2"]+p["win3"]
		p["totalloss"]=p["loss1"]+p["loss2"]+p["loss3"]
		p["total"]=p["total1"]+p["total2"]+p["total3"]
		p["totalmmr"]=p["mmr1"]+p["mmr2"]+p["mmr3"]
		if p["idplayer"]==1945:
			p["name"]='ShadoWn*'
		p["numgames"]=len(gamesbetween.filter(player_id=p["idplayer"]))
		(win,loss,ties,mmr)=getNumberGamesAt(start,p["idplayer"])
	#	print(p["name"],p["numgames"],p["wins"]-win,p["loses"]-loss,n[1][1],n[2][1])
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
	context={"players":playerwcs,"basemmr":-basemmr,"games":recentwcsgames,
	"wait":timetowait,"promotime":timetopromotion,"server":server}
	print(time.time()-deb)
	return renderrandomtitle(request, html,context)


def statswcs(request,server):
	lastQualif=8#might be 16 or other in 2017 its 8 on eu
	playerwcs=Players.objects.filter(wcs=1,
	smurf__wcsregion=server,season=32,server=server,
		rating__gte=6300).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	num=1
	basemmr=0
	listegoodplayerid=[]
	listename=[]
	startjeudi=datetime.datetime(2017,5,25,19,0)
	startvendredi=datetime.datetime(2017,5,12,19,0)
	startsamedi=datetime.datetime(2017,5,13,19,0)
	startdimanche=datetime.datetime(2017,5,28,19,0)
	gamesbetween=Games.objects.filter(
		date__gte=startjeudi.timestamp(),
		date__lte=startdimanche.timestamp())
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
			p["numgames"]=len(gamesbetween.filter(player_id=p["idplayer"]))
			listegoodplayerid.append(p["idplayer"])
			listename.append(p["smurf__pseudo"])
			p["num"]=num
			if num<=lastQualif:
				p["qualif"]="qualif"
			else:
				p["qualif"]="notqualif"
			if num==lastQualif:
				basemmr=p["rating"]
			num+=1
		p["LP"]=str(datetime.timedelta(
		seconds=int(time.time())-p["last_played"]))[0:7]
		if p["smurf__pseudo"]!=None:
			p["name_human"]=p["smurf__pseudo"]+"("+p["name"] +")"
		else:
			p["name_human"]=p["name"]
	#recent games of thoses players last 12h
	DELTATIME=3600*6
	#count the game between promotion

	recentwcsgames=Games.objects.filter(server=server,
	date__gte=startjeudi.timestamp(),date__lte=startdimanche.timestamp(),
	player__in=listegoodplayerid).select_related(
	"player").order_by(
	"-date")

	worstgames=recentwcsgames.order_by("guessmmrchange").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player"
	)[:10]
	bestgames=recentwcsgames.order_by("-guessmmrchange").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player"
	)[:10]
	dangerousgames=recentwcsgames.filter(guessmmrchange__gte=0).order_by(
	"guessmmrchange").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player"
	)[:10]

	for g in worstgames:
		g["date_human"]=datetime.datetime.fromtimestamp(
		g["date"]).strftime('%d %b %H:%M')
		if g["guessopid__smurf__pseudo"]!= None:
			g["guessopid__name"]=g["guessopid__smurf__pseudo"]
		if g["guessopid__name"]==None:
			g["guessopid__name"]=g["guessopgameid__path"]
	for g in bestgames:
		g["date_human"]=datetime.datetime.fromtimestamp(
		g["date"]).strftime('%d %b %H:%M')
		if g["guessopid__smurf__pseudo"]!= None:
			g["guessopid__name"]=g["guessopid__smurf__pseudo"]
		if g["guessopid__name"]==None:
			g["guessopid__name"]=g["guessopgameid__path"]
	for g in dangerousgames:
		g["date_human"]=datetime.datetime.fromtimestamp(
		g["date"]).strftime('%d %b %H:%M')
		if g["guessopid__smurf__pseudo"]!= None:
			g["guessopid__name"]=g["guessopid__smurf__pseudo"]
		if g["guessopid__name"]==None and g["guessopgameid__path"]!=None :
			g["guessopid__name"]=g["guessopgameid__path"].split("/")[-1]
	data=[]
	for (i,idplayer) in enumerate(listegoodplayerid):
		for (j,idplayer2) in enumerate(listegoodplayerid):
			g=recentwcsgames.filter(player=idplayer,
			guessopid=idplayer2)
			s=g.aggregate(Sum("guessmmrchange"))["guessmmrchange__sum"]
			l=len(g)
			if s==None:
				s=0
			data.append([j,i,(s,l)])
	otherid=recentwcsgames.exclude(guessopid__in=listegoodplayerid ).values("guessopid").order_by("guessopid").annotate(
	n=Count("guessopid")).filter(n__gte=10).order_by("-n")
	listotherid=[]
	nameother=[]
	for g in otherid:
		listotherid.append(g["guessopid"])
		p=Players.objects.get(pk=g["guessopid"])
		if p.smurf!=None:
			name=p.smurf.pseudo+"("+p.name+")"
		else:
			name=p.name
		nameother.append(name)


	othergames=recentwcsgames.filter(guessopid__in=listotherid)
	dataother=[]
	for (i,idplayer) in enumerate(listegoodplayerid):
		ligne=[]
		for (j,idother) in enumerate(listotherid):

			g=othergames.filter(player=idplayer,
			guessopid=idother)
			s=g.aggregate(Sum("guessmmrchange"))["guessmmrchange__sum"]
			if s==None:
				s=0
			ligne.append(s)
			l=len(g)
			dataother.append([i,j,(-s,l)])


	context={"players":playerwcs,"basemmr":-basemmr,"games":worstgames,
	"best":bestgames,"dangerous":dangerousgames,"names":listename,"data":data,
	"dataother":dataother,"nameother":nameother}
	return renderrandomtitle(request, 'starcraftHistory/statswcs.html',context)
