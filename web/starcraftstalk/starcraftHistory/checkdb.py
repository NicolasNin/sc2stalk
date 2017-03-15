from .useapi import Useapi
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

def findHoles(player):
    """ find games in db where games are not attributed to player
    but wins/loss can do, we dont look at all the account race     """

    games=Games.objects.filter(type="SOLO",path=player.path).order_by("date")
    #there can be many account playing on this
    first=True
    between=0
    can=0
    cannot=0
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

def allHoles(thresh=6000):
    can=0
    cannot=0
    for p in Players.objects.filter(rating__gte=thresh):
        (c,cn)=findHoles(p)
        can+=c
        cannot+=cn

    print(can,cannot)

def findDuplicate(player):
    games=Games.objects.filter(path=player.path)

    for (i,g1) in enumerate(games):
        for g2 in games[i+1:]:
            if g1.date==g2.date:
                print(g1.idgames,g2.idgames,g1.date)
