from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from background_task import background
from django.http import HttpResponse
from django.template import loader

#from .apiRequest import apiRequest
from .models import League
from .updateDB import *

import datetime
import time

def index(request):
	return render(request, 'starcraftHistory/index.html')
###########	
def recent(request):
	games_dict=Games.objects.filter(date__gte=int(time.time()-1800)).order_by("-date").values("date",
		"path","map","type","decision","current_mmr","guessmmrchange","player__mainrace",
		"current_win",
		"current_losses")
	for g in games_dict:
		g["date_human"]=datetime.datetime.fromtimestamp(g["date"]).strftime('%Y-%m-%d %H:%M:%S')
		g["path_human"]=g["path"].split("/")[-1]
	context={"games":games_dict,"name":" last 30min"}
	return render(request, 'starcraftHistory/player.html', context)


def playerbypath(request,path):
	games_dict=Games.objects.filter(path=path).order_by("-date").values("date",
		"path","map","type","decision","current_mmr","guessmmrchange","player__mainrace","current_win",
		"current_losses")
	for g in games_dict:
		g["date_human"]=datetime.datetime.fromtimestamp(g["date"]).strftime('%Y-%m-%d %H:%M:%S')
		g["path_human"]=g["path"].split("/")[-1]
	context={"games":games_dict,"name":path.split("/")[-1]}
	return render(request, 'starcraftHistory/player.html', context)
		
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
	player_in_db=Players.objects.all().order_by("-rating").values()
	
	context={"players":player_in_db}
	return render(request, 'starcraftHistory/players.html', context)
	#return HttpResponse(template.render(context, request))


	
def updateLeagues():
	#first we retrieve the already existing leagues
	existingLeagues=League.objects.all()
	liste_existing_ladderid=[]
	for exl in existingLeagues:
		liste_existing_ladderid.append(exl.ladderid)
	
	api=apiRequest()
	#GM
	l=api.getLadderId(6)
	season=l["key"]["season_id"]
	ladderid=l["tier"][0]["division"][0]["ladder_id"]
	if ladderid not in liste_existing_ladderid:
		
		L=League(ladderid=int(ladderid),season=int(season),level=6)
		L.save()
	#Master1
	leaguesM1=api.getLadderId(5)["tier"][0]
	for l in leaguesM1["division"]:
		if l["ladder_id"] not in liste_existing_ladderid:
			League(ladderid=int(l["ladder_id"]),season=int(season),level=5).save()


def about(request):
	return render(request, 'starcraftHistory/about.html')
def contact(request):
	return render(request, 'starcraftHistory/contact.html')