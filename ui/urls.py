from django.conf.urls import url
from . import views

app_name = 'ui'
urlpatterns = [
    url(r'^signup$', views.signup, name='signup'),
    url(r'^main$', views.landing, name='landing'),
    url(r'^league/join$', views.league_join, name='league_join'),
    url(r'^league/join/submit$', views.league_join_submit, 
      name='league_join_submit'),
    url(r'^league/create$', views.league_create, name='league_create'),
    url(r'^league/create/submit$', views.league_create_submit, 
      name='league_create_submit'),
    url(r'^league/home/(?P<league_name>.+)$', views.league_home, 
      name='league_home'),
    url(r'^league/picks/submit$', views.league_picks_submit, 
      name='league_picks_submit'),
    url(r'^league/answers/submit$', views.league_answers_submit, 
      name='league_answers_submit'),
    url(r'^league/scoreboard/(?P<league_name>.+)$', views.league_scoreboard, 
      name='league_scoreboard'),
    url(r'^league/(?P<answers_or_picks>[a-z]+)/(?P<league_name>.+)$', 
      views.league_answers_or_picks, name='league_answers_or_picks')
]