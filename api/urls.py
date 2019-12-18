from django.conf.urls import url
from . import views

app_name = 'api'
urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^login$', views.login_user, name='login_user'),
    url(r'^logout$', views.logout_user, name='logout_user'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^user/leagues$', views.user_leagues, name='user_leagues'),
    url(r'^league/join$', views.league_join, name='league_join'),
    url(r'^league/create$', views.league_create, name='league_create'),
    url(r'^league/prop-bets$', views.league_prop_bets, name='league_prop_bets'),
    url(r'^league/answers$', views.league_answers, name='league_answers'),
    url(r'^league/scoreboard$', views.league_scoreboard, name='league_scoreboard'),
    url(r'^member/admin$', views.member_admin, name='member_admin'),
    url(r'^member/picks/get$', views.member_get_picks, name='member_get_picks'),
    url(r'^member/picks/update$', views.member_update_picks, name='member_update_picks'),
]