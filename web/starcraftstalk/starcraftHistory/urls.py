from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<server>.*)/players/$', views.players, name='players'),
    url(r'^(?P<server>.*)/wcs/$', views.wcs, name='wcs'),
    url(r'^(?P<server>.*)/wcs2/$', views.wcsdata, name='wcsdata'),
#    url(r'^wcs/$', views.wcsold, name='wcsold'),
    url(r'^league/(?P<league>[0-9]+)/$', views.league, name='league'),
    url(r'^highmmr/$', views.highmmr, name='highmmr'),
    url(r'^(?P<server>.*)/recent/$', views.recent, name='recent'),
    url(r'^last100/$', views.last100, name='last100'),
    url(r'^(?P<server>.*)/player/(?P<sc2id>[0-9]+)/$', views.player, name='player'),
    url(r'^(?P<server>.*)/profile/(?P<legacy>[0-9]+)/(?P<realm>[0-9])/(?P<name>.*)$', views.player2, name='player'),
  #  url(r'^player/(?P<sc2id>(.*))/$', views.player, name='player'),
    url(r'^update/$', views.update, name='update'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^graph/(?P<playerid>[0-9]+)/$', views.graph, name='graph'),
    url(r'^(?P<server>.*)/comparemmr/$', views.graphmmr, name='graphmmr'),
    url(r'^(?P<server>.*)/statswcs/$', views.statswcs, name='statswcs'),
    url(r'^testrecentlive/$', views.recentlive, name='rlive'),
    url(r'^testrecentlive/lm/$', views.lastmatchsince, name='since'),
    #pro url
    url(r'^pro/$', views.pros, name='pro'),
    url(r'^pro/(?P<proid>[0-9]+)/$', views.proPlayer, name='proPlayer'),
]
