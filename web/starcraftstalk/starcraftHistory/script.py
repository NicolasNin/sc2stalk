#to automate one day
from starcraftHistory.newgames import *
#mantis and claire, GUru Hellraiser etc
syncDbwithMH(Players.objects.get(pk=1198),True)
syncDbwithMH(Players.objects.get(pk=2089),True)
syncDbwithMH(Players.objects.get(pk=1213),True)
syncDbwithMH(Players.objects.get(pk=1288),True)
syncDbwithMH(Players.objects.get(pk=1452),True)
syncDbwithMH(Players.objects.get(pk=63),True)
#guru
attributeAllgameToPlayer(2089)

from starcraftHistory.findOp import *
found=findOpListObject(Games.objects.filter(idgames__gte=400000))
checkReciprocal(found,True)

from starcraftHistory.checkdb import *
allHoles(5000,save=True)
findGamewithoutp()
