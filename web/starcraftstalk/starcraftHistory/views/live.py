from ..models import League,Games,Global
from django.shortcuts import render
import time,datetime
import json
from django.http import HttpResponse,JsonResponse
from django.core import serializers
def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def gamesDict(date,listeid,reverse=True):
    if reverse:
        order="-date"
    else:
        order="date"
    return  Games.objects.filter(
        	date__gt=date,date__isnull=False,player__in=listeid).select_related(
        	"player").order_by(
        	order).values(
        	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
        	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
        	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player",
        	"guessopid__mainrace","player__mainrace","pk"
        	)
def addHumanDate(games2,timetoadd=0):
    if type(games2)==dict:
        games=games2["games"]
    else:
        games=games2
    for g in games:
        g["date_human"]=datetime.datetime.fromtimestamp(
        g["date"]).strftime('%d %b %H:%M')

        if g["guessopid__smurf__pseudo"]!= None:
            g["guessopid__name"]=g["guessopid__smurf__pseudo"]
        if g["guessopid__name"]==None:
            g["guessopid__name"]=g["guessopgameid__path"]

    return games
def getListePlayerWcs(server="us"):
    v=Global.objects.filter(name="listewcsusplayer")[0].value
    jsonDec = json.decoder.JSONDecoder()
    return jsonDec.decode(v)
def recentlive(request):
    listegoodplayer=getListePlayerWcs("us")
    print(listegoodplayer)
    maxpk=Games.objects.latest("pk").pk
    maxdate=Games.objects.latest("date").date
    games=gamesDict(maxdate-3600,listegoodplayer)
    games=addHumanDate(games)
    context={"time":time.time(),"games":games,"server":"","maxpk":maxpk,
    "maxdate":maxdate,"playersid":listegoodplayer}
    return render(request,'starcraftHistory/testlive.html',context)
def lastmatchsince(request):
    print(request.GET)
    if RepresentsInt(request.GET["date"]):
        date=int(request.GET["date"])
        listegoodplayer=getListePlayerWcs("us")
        games=gamesDict(date,listegoodplayer,False)
        games=addHumanDate(games)
        games={"games":list(games)}
        print(games)
        #print((games))
    else:
        games={}
#    return HttpResponse(games,
#                    content_type='application/json; charset=utf8')
    return JsonResponse(games,safe=False)
