from math import log10
def getMagicK(deltapoints):
	if deltapoints<=30  and deltapoints>=20:
		return 46
	if deltapoints>30:
		return 46+0.5*(deltapoints-30)
	else:
		return 46-0.5*(deltapoints-20)

def getMMRmagic(newMMR1,deltammr1):
	return getMMR(newMMR1,deltammr1,getMagicK(abs(deltammr1)))

def getMMR(newMMR1,deltammr1,K):
	if deltammr1==0:
		print("000000000")
		return 0
	if deltammr1>0:
		w=1
	else:
		w=0
	p=w-deltammr1/K

	if abs(deltammr1)>K or p==0:
	#	print(deltammr1)
		return 0
	if 1/p-1<=0:
	#	print(deltammr1,w,p)
		return 0
	return newMMR1+800*log10(1/p-1)
