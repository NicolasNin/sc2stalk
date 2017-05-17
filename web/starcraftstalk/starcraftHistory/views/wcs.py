from .views import renderrandomtitle
from ..models import Players,Games
import datetime,time
import pytz

def getPromotionWindows(server):
	""" return the start and end of promotion windows for today
	in UTC as a timestamp"""

	if server=="us":
		tz= pytz.timezone('America/New_York')
	else:
		tz= pytz.timezone('Europe/Paris')
	#we are cest time on the server
	cest= pytz.timezone('Europe/Paris')
	now=cest.localize(datetime.datetime.now())
	now_local=now.astimezone(tz)
	#promotion is between 21h each day
	if now_local.hour>=21:
		start=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		end=(start+datetime.timedelta(days=1))
	else:
		end=tz.localize(datetime.datetime(now_local.year,now_local.month,now_local.day,21)).astimezone(pytz.utc)
		start=(end-datetime.timedelta(days=1))
	return (start.timestamp(),end.timestamp())

def wcs(request,server):
	if server=="us":
		timetoadd=-4*3600
		html="starcraftHistory/wcsus.html"
		thresh=6000

	else:
		html="starcraftHistory/wcs2.html"
		thresh=6300
	(start,end)=getPromotionWindows(server)
	""" we get the top GM player who are from the good wcs region
	with a good name (ie their true name)"""
	lastQualif=8#might be 16 or other in 2017 its 8 on eu
	playerwcs=Players.objects.filter(
	smurf__wcsregion=server,season=32,server=server,
		rating__gte=thresh).order_by("-rating").values("rating",
	"name","mainrace","wins","loses","league","smurf__pseudo","idplayer","rank",
	"league__sigle","last_played","idplayer")
	num=1
	basemmr=0
	listegoodplayerid=[]
	gamesbetween=Games.objects.filter(server=server,
		date__gte=start,date__lte=end)
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
	date__gte=time.time()-DELTATIME,
	player__in=listegoodplayerid).select_related(
	"player").order_by(
	"-date").values(
	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player",
	"guessopid__mainrace","player__mainrace"
	)
	for g in recentwcsgames:
		g["date_human"]=datetime.datetime.fromtimestamp(
		g["date"]+timetoadd).strftime('%d %b %H:%M')
		if g["guessopid__smurf__pseudo"]!= None:
			g["guessopid__name"]=g["guessopid__smurf__pseudo"]
		if g["guessopid__name"]==None:
			g["guessopid__name"]=g["guessopgameid__path"]

	timetowait=str(datetime.datetime(2017,5,14,21,59)-
	datetime.datetime.fromtimestamp(int(time.time())))
	context={"players":playerwcs,"basemmr":-basemmr,"games":recentwcsgames,"wait":timetowait}
	return renderrandomtitle(request, html,context)

def wcsold(request):
	return wcs(request,server="eu")
