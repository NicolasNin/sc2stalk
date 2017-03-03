from .models import Players, Progamer
def isBarcode(name):
    for i in name:
        if i.lower()!="i" and i.lower()!="l":
            return False
    return True

def displayNamePlayer(p):
    """ being given a player we want a *nice* name to be displayed"""
    #if smurt exist we use the pseud
    pseudo=""
    if p.smurf!=None:
        pseudo= p.smurf.pseudo+ " aka "

    if isBarcode(p.name.split("#")[0]):
        return pseudo+p.name
    else:
        return pseudo +p.name

def displayNameGame(game):
    if game.player!=None:
        return displayNamePlayer(game.player)
    else:
        return g["path"].split("/")[-1]

def displayNameGameOpponent(game):
    if game.guessopid!=None:
        return displayNamePlayer(Games.objects.get(pk=game.guessopid))
    elif game.guessopgameid!=None:
        return displayNameGame(Games.objects.get(pk=game.guessopgameid))
    return ""

def displayNameAccount(path):
    players=Players.objects.filter(path=path)
    smurfplayer=players.filter(smurf__isnull=False)
    if len(smurfplayer)!=0 :
        smurf=smurfplayer.values("smurf__pseudo")[0]["smurf__pseudo"]
        return smurf
    if isBarcode(players[0].name.split('#')[0]):
        return players[0].name
    else:
         return players[0].name.split('#')[0]
def getBneturl(path):
    return 'http://eu.battle.net/sc2/en/'+ path+'/'
