from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^players/$', views.players, name='players'),
    url(r'^player/(?P<sc2id>[0-9]+)/$', views.player, name='players'),
    url(r'^update/$', views.update, name='update'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
]
