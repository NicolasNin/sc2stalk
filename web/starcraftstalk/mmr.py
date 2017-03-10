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


def getMagicK2(deltapoints):
	magic={}
	if deltapoints<1 or deltapoints>57:
		return getMagicK(deltapoints)
	magic[1.0]=40.0
	magic[1.5]=70.0
	magic[2.0]=48.0
	magic[2.5]=70.0
	magic[3.0]=48.0
	magic[3.5]=42.5
	magic[4.0]=52.0
	magic[4.5]=59.0
	magic[5.0]=58.5
	magic[5.5]=58.5
	magic[6.0]=49.0
	magic[6.5]=58.5
	magic[7.0]=52.0
	magic[7.5]=56.5
	magic[8.0]=52.5
	magic[8.5]=58.0
	magic[9.0]=53.5
	magic[9.5]=53.5
	magic[10.0]=52.5
	magic[10.5]=51.0
	magic[11.0]=51.0
	magic[11.5]=46.5
	magic[12.0]=49.0
	magic[12.5]=47.0
	magic[13.0]=49.5
	magic[13.5]=46.0
	magic[14.0]=47.0
	magic[14.5]=47.0
	magic[15.0]=47.0
	magic[15.5]=45.5
	magic[16.0]=46.5
	magic[16.5]=47.5
	magic[17.0]=46.0
	magic[17.5]=47.5
	magic[18.0]=47.5
	magic[18.5]=47.0
	magic[19.0]=47.0
	magic[19.5]=46.0
	magic[20.0]=46.5
	magic[20.5]=44.0
	magic[21.0]=45.0
	magic[21.5]=47.5
	magic[22.0]=45.5
	magic[22.5]=47.5
	magic[23.0]=45.5
	magic[23.5]=45.0
	magic[24.0]=45.5
	magic[24.5]=44.5
	magic[25.0]=45.5
	magic[25.5]=47.0
	magic[26.0]=45.0
	magic[26.5]=44.5
	magic[27.0]=45.5
	magic[27.5]=48.0
	magic[28.0]=46.0
	magic[28.5]=45.5
	magic[29.0]=47.0
	magic[29.5]=47.0
	magic[30.0]=46.0
	magic[30.5]=46.5
	magic[31.0]=46.5
	magic[31.5]=48.0
	magic[32.0]=46.5
	magic[32.5]=47.5
	magic[33.0]=47.5
	magic[33.5]=48.0
	magic[34.0]=47.5
	magic[34.5]=47.0
	magic[35.0]=47.5
	magic[35.5]=49.0
	magic[36.0]=48.0
	magic[36.5]=49.0
	magic[37.0]=48.0
	magic[37.5]=49.5
	magic[38.0]=49.5
	magic[38.5]=48.0
	magic[39.0]=49.5
	magic[39.5]=49.0
	magic[40.0]=50.0
	magic[40.5]=49.5
	magic[41.0]=50.0
	magic[41.5]=51.5
	magic[42.0]=51.0
	magic[42.5]=50.5
	magic[43.0]=52.0
	magic[43.5]=51.5
	magic[44.0]=52.0
	magic[44.5]=53.0
	magic[45.0]=52.5
	magic[45.5]=53.5
	magic[46.0]=53.5
	magic[46.5]=53.5
	magic[47.0]=54.0
	magic[47.5]=54.0
	magic[48.0]=54.5
	magic[48.5]=54.5
	magic[49.0]=55.5
	magic[49.5]=56.0
	magic[50.0]=56.5
	magic[50.5]=57.0
	magic[51.0]=57.0
	magic[52.0]=57.5
	magic[52.5]=57.5
	magic[54.0]=59.0
	magic[55.0]=59.5
	magic[57.5]=61.0
	return magic[deltapoints]
