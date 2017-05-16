from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<server>.*)/players/$', views.players, name='players'),
    url(r'^pro/$', views.pro, name='pro'),
    url(r'^(?P<server>.*)/wcs/$', views.wcs, name='wcs'),
    url(r'^league/(?P<league>[0-9]+)/$', views.league, name='league'),
    url(r'^highmmr/$', views.highmmr, name='highmmr'),
    url(r'^(?P<server>.*)/recent/$', views.recent, name='recent'),
    url(r'^last100/$', views.last100, name='last100'),
    url(r'^player/(?P<sc2id>[0-9]+)/$', views.player, name='player'),
    url(r'^profile/(?P<legacy>[0-9]+)/(?P<realm>[0-9])/(?P<name>.*)$', views.player2, name='player'),
  #  url(r'^player/(?P<sc2id>(.*))/$', views.player, name='player'),
    url(r'^update/$', views.update, name='update'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^graph/(?P<playerid>[0-9]+)/$', views.graph, name='graph'),
    url(r'^(?P<server>.*)/comparemmr/$', views.graphmmr, name='graphmmr'),
    url(r'^(?P<server>.*)/statswcs/$', views.statswcs, name='statswcs'),
]
