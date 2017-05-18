from ..models import League,Games,Global
from django.shortcuts import render
import time
import json
from django.http import HttpResponse,JsonResponse
from django.core import serializers
def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def gamesDict(date):
    print(date)
    return  Games.objects.filter(
        	pk__gt=date).select_related(
        	"player").order_by(
        	"-date").values(
        	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
        	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
        	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player",
        	"guessopid__mainrace","player__mainrace","pk"
        	)
def last20games():

    return  Games.objects.all().select_related(
        	"player").order_by(
        	"-date").values(
        	"date","guessopgameid__current_mmr","guessopgameid__guessmmrchange",
        	"player__name","current_mmr","guessmmrchange","guessopid__name","player",
        	"guessopgameid__path","guessopid__smurf__pseudo","guessopgameid__player",
        	"guessopid__mainrace","player__mainrace","pk"
        	)
def recentlive(request):
    maxpk=Games.objects.latest("pk").pk
    games=gamesDict(maxpk-10)
    context={"time":time.time(),"games":games,"server":"","maxpk":maxpk-5}
    return render(request,'starcraftHistory/testlive.html',context)
def lastmatchsince(request):
    print("azeazeze")
    print(request.GET)
    print(request.POST)
    print(request.GET["date"])
    if RepresentsInt(request.GET["date"]):
        date=int(request.GET["date"])
        games={"games":list(gamesDict(date))}
        #print((games))
    else:
        games={}
#    return HttpResponse(games,
#                    content_type='application/json; charset=utf8')
    return JsonResponse(games,safe=False)
