from .useapi import Useapi
from .models import *
def consistencyMHDB(player):
    useapi=Useapi()
    MH=useapi.getPlayerMatchHistory(player.path,player.alternate_path)
    if MH!=[]:
        gamesdb=Games.objects.filter(path=player.path)
        for g in MH:
            if gamesdb.filter(date=g["date"]).exists():
                gdb=gamesdb.filter(date=g["date"])[0]
                if gdb.map=="":

                    if gdb.guessopgameid!=None and gdb.guessopgameid>0 :
                        opgame=Games.objects.get(pk=gdb.guessopgameid)
                        if opgame.map!="" and opgame.map!=g["map"]:
                            print("map different",gdb.idgames,opgame.idgames)
                    print(gdb.idgames,g["map"],g["date"],player.path)


def consistencyMHDBListe(liste_players):
    for p in liste_players:
        consistencyMHDB(p)
        print("")

def findHoles2(player,save=False):
    games=Games.objects.filter(type="SOLO",path=player.path).order_by("date")
    liste_inbetween=[]
    can=0
    cannot=0
    wins=0.5
    for g in games:
        if  g.current_win!=None and g.current_losses!=None and g.current_ties!=None :
            if liste_inbetween==[]:
                wins=g.current_win
                losses=g.current_losses
                ties=g.current_ties
            else:
                deltawin=g.current_win-wins
                deltalosses=g.current_losses-losses
                deltaties=g.current_ties-ties
                count=deltawin+deltalosses+deltaties
                if count!=1 :
                    if count>1:
                        if len(liste_inbetween)==count-1:
                            print(g.path,"HOLE WE CAN FILL",count,g.date,wins,losses)
                            print(liste_inbetween)
                            fillWinLoss(wins,losses,ties,liste_inbetween,player,save=save)
                            can+=1
                        else:
                            print(g.path,"hole we CANNOT fill",count,g.date,wins,losses)
                            cannot+=1
                    if count==0:
                        if deltawin==0 and deltalosses==0:
                            pass #unrank
                        else:
                            print(g.path," Reset?",count,g.date,
                            wins,losses,deltawin,deltalosses)
                wins=g.current_win
                losses=g.current_losses
                ties=g.current_ties
                liste_inbetween=[]
        else:
            if wins!=0.5:
                liste_inbetween.append(g)
    return (can,cannot)
def fillWinLoss(startwin,startloss,startties,games,player,save=False):
    w=startwin
    l=startloss
    t=startties
    for g in games:
        if g.decision=="WIN":
                w+=1
        elif g.decision=="LOSS":
            l+=1
        elif g.decision=="TIES":
            t+=1
        else:
            print("problem not a decision")
        g.player=player
        g.current_win=w
        g.current_losses=l
        g.current_ties=t
        #print(w,l)
        if save:
            g.save()


def findHoles(player):
    """ find games in db where games are not attributed to player
    but wins/loss can do, we dont look at all the account race     """

    games=Games.objects.filter(type="SOLO",path=player.path).order_by("date")
    #there can be many account playing on this
    first=True
    between=0
    can=0
    cannot=0
    liste_games_with_info=[]
    for g in games:
        if g.player==player and  g.current_win!=None:
            if first:
                first=False
                between=0
                wins=g.current_win
                losses=g.current_losses
                ties=g.current_ties
            else:
                deltawin=g.current_win-wins
                deltalosses=g.current_losses-losses
                deltaties=g.current_ties-ties
                wins=g.current_win
                losses=g.current_losses
                ties=g.current_ties
                count=deltawin+deltalosses+deltaties
                if count!=1 :
                    if count>1:
                        if between==count-1:
                            print(g.path,"HOLE WE CAN FILL",count,g.date,wins,losses,between)
                            can+=1
                        else:
                            print(g.path,"hole we CANNOT fill",count,g.date,wins,losses,between)
                            cannot+=1
                    if count==0:
                        if deltawin==0 and deltalosses==0:
                            pass #unrank
                        else:
                            print(g.path," Reset?",count,g.date,
                            wins,losses,deltawin,deltalosses)
            between=0
        else:
            between+=1
    return (can,cannot)

def allHoles(thresh=6000,save=False):
    can=0
    cannot=0
    for p in Players.objects.filter(rating__gte=thresh):
        (c,cn)=findHoles2(p,save=save)
        can+=c
        cannot+=cn

    print(can,cannot)

def findGamewithoutp():
    """ for when you find holes"""
    games=Games.objects.filter(guessopgameid__isnull=False,
    guessopid__isnull=True,guessopgameid__player__isnull=False)
    for g in games:
        print(g)
        g.guessopid=g.guessopgameid.player
        g.save()

### find game that are played by the same player at same date
### happen when we add a game with a NA then go through match history
###since current game adding is so awfullt bad and onlychek first game for LP
def findDuplicate(player,save=False):
    games=Games.objects.filter(path=player.path)
    count=0
    liste_modified_games=[]
    for (i,g1) in enumerate(games):
        for g2 in games[i+1:]:
            if g1.date==g2.date or abs(g1.date-g2.date)==1:
                print("----------",player.path)
                goodgame=None
                if g1.map=="" and g2.map!="":
                    goodgame=g2
                    badgame=g1
                if g2.map=="" and g1.map!="":
                    goodgame=g1
                    badgame=g2
                if goodgame!=None:
                    print(g1.decision,g2.decision,"True",goodgame.decision,
                    goodgame.map)
                    #we change map and decision in bad game
                    #then delete goodgame
                    #we also remove guessop in potentially 4 game
                    if save:
                        removeallguess(badgame)
                        removeallguess(goodgame)
                        badgame.map=goodgame.map
                        badgame.decision=goodgame.decision
                        badgame.date=goodgame.date
                        badgame.type=goodgame.type
                        goodgame.delete()
                        badgame.save()
                        liste_modified_games.append(badgame)
                    else:
                        print(badgame.idgames,badgame.map,badgame.decision,
                        badgame.date,badgame.guessopgameid)
                        print(goodgame.idgames,goodgame.map,goodgame.decision,
                        goodgame.date,goodgame.guessopgameid)
                else:
                    print(g1.map,"|",g2.map)
            count+=1
    return (count,liste_modified_games)
def removeallguess(g):
    if g.guessopgameid!=None:
        opgame=g.guessopgameid
        opgame.guessopgameid=None
        opgame.guessopid=None
        opgame.save()
    g.guessopgameid=None
    g.guessopid=None
    g.save()
def findAllduplicate(save=False):
    count=0
    liste_modified_games=[]
    for p in Players.objects.all():
        (c,liste)=findDuplicate(p,save=save)
        count+=c
        liste_modified_games.extend(liste)
    if save:
        found=findOpListObject(liste_modified_games,save=False)
        checkReciprocal(found,save=True)
    return c


## MAP DIFFERENT can happen when map is empty then modified
#since modified game are not looked up again
def findErrorWithOp(listegame,showdecision=False):
	for g in listegame:
		g1=g
		if g.guessopgameid!=None:
			g2=g.guessopgameid
			if g.map!="" and g2.map!="":
				if g.map!=g2.map:
					print("MAP",g1.date,g1,g2)

			if showdecision and g.decision!=oppositeDecision(g2.decision):
					print("decision",g1.date,g1.decision,g2.decision)
