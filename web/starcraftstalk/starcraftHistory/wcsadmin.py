##function to initialize add and remove wcs player
from .models import League, Players, Games, Progamer,Global

def isbarcode(name):
    name=name.lower()
    for letter in name:
        if letter!="l" and letter!="i":
            return False
    return True
def isSimiliar(name,pseudo):
    name=name.lower()
    pseudo=pseudo.lower()
    ##special case
    if pseudo=="uthermal" and name.find("thermy")!=-1:
        return True
    ##
    if name==pseudo:
        return True
    if name.find(pseudo)!=-1:
        return True
    else:
        return False
def init(server):
    if server=="us":
        wcsRegion="NA"
    else:
        wcsRegion="EU"
    liste_player=Players.objects.filter(server=server,smurf__wcsregion=wcsRegion,wcs=None)
    #we remove barcode
    for pdb in liste_player:
        name=pdb.name.split("#")[0]
        pseudo=pdb.smurf.pseudo
        if not isbarcode(name):
            if isSimiliar(name,pseudo):
                pdb.wcs=1
                pdb.save()
                print("accepted",name,pseudo)
            else:
                print("not same",name,pseudo)

def updateWcsRegion(init=False):
    wcsRegion={"FR":"EU","FI":"EU","KR":"KR","US":"NA","CA":"NA","PL":"EU","NL":"EU",
    "NO":"EU","MX":"MA","DE":"EU","IT":"EU","UA":"EU",
    "SE":"EU","SI":"EU","AT":"EU","RU":"EU","LT":"EU","UK":"EU","ES":"EU","DK":"EU",
    "SR":"EU","SK":"EU","HR":"EU","RO":"EU"}
    liste_pro=Progamer.objects.filter(wcsregion="Unknown")
    for pro in liste_pro:
        pays=pro.nationality
        if pays in wcsRegion:
            pro.wcsregion=wcsRegion[pays]
            pro.save()
    if init:
        # we change the not back
#elazer serral uthermal Nerchio cause already quali
toremoveeu=[162,44,191,122]
toremoveus=[121,157,204,108]
def removeWcsPlayers(liste_pro,server):
    for idpro in liste_pro:
        pro=Progamer.objects.get(pk=idpro)
        pro.wcsregion="not"
        pro.save()
