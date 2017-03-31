from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from background_task import background
from django.http import HttpResponse
from django.template import loader
from django.db.models import F
from django.db.models import Max,Min
#from .apiRequest import apiRequest
from .models import League
from .updateDB import *
from mmr import *

import datetime
import time
from .displayname import *
from random import randrange
def index(request):
	return renderrandomtitle(request, 'starcraftHistory/index.html',{})
###########

def getalldict(games,orderbydate=True):
	if orderbydate:
		games=games.order_by("-date")
	games_dict=games.values("date",
		"path","map","type","decision","current_mmr","guessmmrchange"
		,"player__mainrace",
		"current_win",
		"current_losses","guessopid__name","guessopid"
		,"guessopgameid","ranked","player__smurf__pseudo","current_league",
		"guessopid__smurf__pseudo","guessopid__mainrace","current_league__sigle",
		"guessopgameid__current_league__sigle")
	statMU={"Z":{},"T":{},"P":{},"R":{}}
	previousgame=None
	lastmatch=0
	for g in games_dict:
		if previousgame==None:
			previousgame=g
			lastmatch=int(time.time()-g["date"])
		else:
			previousgame["timesincelastgame"]=datetime.timedelta(
			seconds=previousgame["date"]-g["date"])
			previousgame=g

		g["map"]=g["map"].split("(")[0]

		g["date_human"]=datetime.datetime.fromtimestamp(g["date"]).strftime('%d %b %H:%M')
		g["path_human"]=g["path"].split("/")[-1]
		if g["player__smurf__pseudo"]!=None:
			g["path_human"]=g["player__smurf__pseudo"]+"("+g["path_human"] +")"
		#op
		if g["guessopgameid"]!=None:
			opgame=Games.objects.get(pk=g["guessopgameid"])
			g["opmmr"]=opgame.current_mmr
			g["opdmmr"]=opgame.guessmmrchange
			g["nameop"]=opgame.path.split("/")[-1]
			g["oppath"]=opgame.path
		if g["guessopid"]!=None:
			p=Players.objects.get(pk=g["guessopid"])
			g["nameop"]=p.name
			if g["guessopid__smurf__pseudo"]!=None:
				g["nameop"]=g["guessopid__smurf__pseudo"]


		if g["current_mmr"]== None or g["guessmmrchange"]==None:
			g["estimated_mmr"]="NA"
		else:
			g["estimated_mmr"]=int(getMMRmagic(int(g["current_mmr"]),int(g["guessmmrchange"])))
		#ranked or not
		if g["type"]=="SOLO":
			g["type_human"]="1v1"
			if g["ranked"]=="unrank":
				g["type_human"]+="(urk)"
		else:
			g["type_human"]=g["type"]
		g["decision_human"]=g["decision"][0]
		#stats

		if g["guessopid"]!=None and g["player__mainrace"]!=None:
			drace=statMU[g["player__mainrace"]]
			prev=drace.get(g["guessopid__mainrace"],[0,0,0,0])
			if g["decision"]=="WIN":
				drace[g["guessopid__mainrace"]]=[prev[0]+1,prev[1],prev[2]+1,
				round(100*(prev[0]+1)/(prev[2]+1))]

			elif g["decision"]=="LOSS":
				drace[g["guessopid__mainrace"]]=[prev[0],prev[1]+1,prev[2]+1,
								round(100*(prev[0])/(prev[2]+1))]
	return (games_dict,statMU,datetime.timedelta(seconds=lastmatch))
def randomTitle():
	titles=["sc2stalk or is your boyfriend ditching you to play starcraft",
	"sc2stalk, because pornhub was down",
	"sc2stalk because everybodies love a good graph",
	"sc2stalk because graph is life, nana na nana!"]
	return titles[randrange(0,len(titles))]
def renderrandomtitle(request,page,context):
	context["title"]=randomTitle()
	return render(request,page,context)

def recent(request):
	games=Games.objects.filter(date__gte=int(time.time()-1800))
	(games_dict,stat,lastmatch)=getalldict(games)
	context={"games":games_dict,"name":" last 30min"}
	return render(request, 'starcraftHistory/player.html', context)
def highmmr(request):
	games=Games.objects.filter(
	date__gte=int(time.time()-5000)).select_related(
	"guessopgameid")
	games=games.annotate(
	sum=F("current_mmr")+F("guessopgameid__current_mmr")).filter(
	sum__gte=12000	).order_by("-date")
#	,current_mmr__gte=6000)
	#games=games.order_by("-current_mmr")
	#games=games.extra(
	#select={"summmr":'current_mmr+guessopgameid__current_mmr'})
	(games_dict,stat,lastmatch)=getalldict(games,False)
	context={"games":games_dict,"name":" last 24h"}
	return renderrandomtitle(request, 'starcraftHistory/highmmr.html',context)
#	highmmr=Games.objects.filter()
def last100(request):
	lastid=Games.objects.latest("idgames").idgames
	games=Games.objects.filter(idgames__gte=lastid-100)
	(games_dict,stat,lastmatch)=getalldict(games)
	context={"games":games_dict,"name":" last 30min"}
	return render(request, 'starcraftHistory/player.html', context)
def playerbypath(request,path):

	games=Games.objects.filter(path=path)
	(games_dict,stat,lastmatch)=getalldict(games)
	realm=int(path.split("/")[3])
	legacyid=int(path.split("/")[2])
	raceplayers=Players.objects.filter(realm=realm,legacy_id=legacyid).select_related("league")
	racep=[]
	statrace=[]
	raceandstat=[]
	for p in raceplayers:
		racep.append(p)
		statrace.append(stat[p.mainrace])
		raceandstat.append((p,stat[p.mainrace]))
	print(raceandstat)
	##hack after name change raceplayer is empty cause path is :=

	context={"games":games_dict,"name":racep[0].name,
	"displayname":displayNameAccount(path),"racep":racep,
	"bneturl":getBneturl(path),"offset":int(12/(len(racep)+2)),"stat":statrace,
	"rs":raceandstat,"lm":lastmatch}
	return render(request, 'starcraftHistory/player2.html', context)

def graph(request,playerid):
	player=Players.objects.get(pk=playerid)
	games=Games.objects.filter(player=player,
	current_mmr__isnull=False).order_by("-date").values(
	"date","current_mmr","guessopid__mainrace","decision",
	"guessmmrchange","guessopid__name","guessopgameid__current_mmr"	)
	maxmmr=games.aggregate(Max("current_mmr"))["current_mmr__max"]
	minmmr=games.aggregate(Min("current_mmr"))["current_mmr__min"]
	for g in games:
		if g["decision"]=="WIN":
			g["color"]="#66b3ff"
		else:
			g["color"]="#ff6666"
	context={"games":games,"min":minmmr,"max":maxmmr,"name":player.name}
	return render(request, 'starcraftHistory/graphtest2.html', context)

def graphmmr(request):
	deb=time.time()
	leagueid=14 #inhard cause im lazy
	playerwcs=Players.objects.filter(
	league_id=leagueid,smurf__wcsregion="eu",
	rating__gte=6300).order_by("-rating").values("rating",
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

#	games=Games.objects.filter(
	#date__gte=datestart,
	#player__in=listegoodplayerid).order_by("path","date").values(
	#"player__name","current_mmr","date"	)
	g2=[]
	for playerid in listegoodplayerid:
		player=Players.objects.get(pk=playerid)
		g2.append({"date":datestart,"player__name":player.name,
		"current_mmr":getMMRatDate(player,datestart)})
		g2.extend(Games.objects.filter(player=player,date__gte=datestart).values(
			"player__name","current_mmr","date","guessopid__name",
			"guessopid__mainrace","guessmmrchange"))
		g2.append({"date":int(time.time()),"player__name":player.name,
		"current_mmr":player.rating})
	context={"games":g2,"min":6300,"max":7000,"name":"test","mmr8":mmr8,
	"listemmr":listemmr,"mmrtop":mmr8+100,"mmrbottom":mmr8-200}
	print(time.time()-deb)
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
def player2(request,legacy,realm,name):
	#gamesdb=Players.objects.get(pk=sc2id)
	path="/profile/"+legacy+"/"+realm+"/"+name
	return playerbypath(request,path)


def player(request,sc2id):
	path=Players.objects.get(pk=sc2id).path
	return playerbypath(request,path)
############################

def update(request):
	#updateCycle(repeat=60, repeat_until=None)

	return HttpResponse("updating database")

def players(request):
	player_in_db=Players.objects.all().order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played")
	for p in player_in_db:
		p["LP"]=datetime.timedelta(
		seconds=int(time.time())-p["last_played"])
		if p["smurf__pseudo"]!=None:
			p["name_human"]=p["smurf__pseudo"]+"("+p["name"] +")"
		else:
			p["name_human"]=p["name"]

	context={"players":player_in_db}
	return render(request, 'starcraftHistory/players.html', context)

def pro(request):
	pro=Progamer.objects.all()
	prodict=[]
	for pgm in pro:
		d={}
		accounts=pgm.players_set.all()
		d["pseudo"]=pgm.pseudo
		d["race"]=pgm.mainrace
		d["nation"]=pgm.nationality
		d["maxmmr"]=accounts.aggregate(Max("rating"))["rating__max"]
		prodict.append(d)
	prodict=sorted(prodict, key=lambda col: (col["nation"]!="kr",col["maxmmr"]),reverse=True)
	context={"pro":prodict}
	return renderrandomtitle(request, 'starcraftHistory/pro.html',context)

def wcs(request):
	""" we get the top GM player who are from the good wcs region
	with a good name (ie their true name)"""
	leagueid=14 #inhard cause im lazy
	lastQualif=8#might be 16 or other in 2017 its 8 on eu
	playerwcs=Players.objects.filter(
	league_id=leagueid,smurf__wcsregion="eu",
		rating__gte=6300).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	num=1
	basemmr=0
	listegoodplayerid=[]
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
			p["num"]=num
			if num<=lastQualif:
				p["qualif"]="qualif"
			else:
				p["qualif"]="notqualif"
			if num==lastQualif:
				basemmr=p["rating"]
			num+=1
		p["LP"]=datetime.timedelta(
		seconds=int(time.time())-p["last_played"])
		if p["smurf__pseudo"]!=None:
			p["name_human"]=p["smurf__pseudo"]+"("+p["name"] +")"
		else:
			p["name_human"]=p["name"]
	#recent games of thoses players last 12h
	DELTATIME=3600*12
	recentwcsgames=Games.objects.filter(
	date__gte=int(time.time())-DELTATIME,
	player__in=listegoodplayerid).select_related(
	"player").order_by(
	"-date").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name"
	)
	for g in recentwcsgames:
			g["date_human"]=datetime.datetime.fromtimestamp(
			g["date"]).strftime('%d %b %H:%M')
	timetowait=str(datetime.datetime(2017,4,2,21,59)-
	datetime.datetime.fromtimestamp(int(time.time())))
	print(timetowait)
	context={"players":playerwcs,"basemmr":-basemmr,"games":recentwcsgames,"wait":timetowait}
	return renderrandomtitle(request, 'starcraftHistory/wcs2.html',context)


def league(request,league):
	player_in_db=Players.objects.filter(
	league_id=league).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played")
	for p in player_in_db:
		p["LP"]=datetime.timedelta(
		seconds=int(time.time())-p["last_played"])
		if p["smurf__pseudo"]!=None:
			p["name_human"]=p["smurf__pseudo"]+"("+p["name"] +")"
		else:
			p["name_human"]=p["name"]

	context={"players":player_in_db}
	return renderrandomtitle(request, 'starcraftHistory/players.html',context)

def about(request):
	return render(request, 'starcraftHistory/about.html')
def contact(request):
	return render(request, 'starcraftHistory/contact.html')
