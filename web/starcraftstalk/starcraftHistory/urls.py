from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^players/$', views.players, name='players'),
    url(r'^recent/$', views.recent, name='recent'),
    url(r'^player/(?P<sc2id>[0-9]+)/$', views.player, name='player'),
    url(r'^profile/(?P<legacy>[0-9]+)/(?P<realm>[0-9])/(?P<name>.*)$', views.player2, name='player'),
  #  url(r'^player/(?P<sc2id>(.*))/$', views.player, name='player'),
    url(r'^update/$', views.update, name='update'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
]
