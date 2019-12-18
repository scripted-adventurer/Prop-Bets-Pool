# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ui.forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

import classes.user
import classes.league
import classes.member
import classes.pick
import classes.prop_bet

def home(request):
  return render(request, 'ui/home.html')

def signup(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      form.save()
      # log the user in, redirect to homepage
      username = form.cleaned_data.get('username')
      raw_password = form.cleaned_data.get('password1')
      user = authenticate(username=username, password=raw_password)
      login(request, user)
      return landing(request)
  else:
    form = SignUpForm()
  
  return render(request, 'ui/signup.html', {'form': form})

@login_required
def landing(request, message=''):
  user = request.user
  leagues = classes.user.User(user.username).get_leagues()
  context = {
    'message': message,
    'user': user,
    'leagues': leagues
  }
  return render(request, 'ui/landing.html', context)

@login_required
def league_join(request, message=''):
  context = {'message': message}
  return render(request, 'ui/league_join.html', context)

@login_required
def league_join_submit(request):
  user = request.user
  league_name = request.POST.get('leagueName')
  league = classes.league.League(league_name)
  member = classes.member.Member(user.username, league_name)
  password = request.POST.get('leaguePassword')
  data_present = True if league_name and password else False
  if (data_present and league.correct_password(password)):
    success = member.create()
    if success:
      message = 'Successfully joined league.'
    else:
      message = 'Unable to join league.'
    return league_home(request, league_name, message)
  else:
    message = 'Error: League name and/or password is invalid or missing.'
  return landing(request, message)          

@login_required
def league_create(request, message=''):
  context = {'message': message}
  return render(request, 'ui/league_create.html', context)

@login_required
def league_create_submit(request):
  user = request.user
  league_name = request.POST.get('leagueName')
  league = classes.league.League(league_name)
  password = request.POST.get('leaguePassword')
  prop_bets = request.POST.get('propBetList')
  if prop_bets:
    prop_bets = prop_bets.split('\n')
  data_present = True if (league_name and password and prop_bets) else False
  if (data_present and league.unique_name()):
    success = league.create(user.username, password, prop_bets)
    if success:
      message = 'Successfully created league.'
    else:
      message = 'Unable to create league.'
    return league_home(request, league_name, message)
  elif data_present:
    message = 'Error: League name must be unique.'
  else:
    message = 'Error: League name, password, and/or prop bet list is invalid or missing.'
  return league_create(request, message)   

@login_required
def league_home(request, league_name, message=''):
  user = request.user
  league = classes.league.League(league_name)
  member = classes.member.Member(user.username, league_name)
  if member.is_member():
    admin = member.is_admin()
    context = {
      'message': message,
      'admin': admin,
      'user': user,
      'league': league.get_object()
    }
    return render(request, 'ui/league_home.html', context)
  else:
    message = 'Error: League is invalid or you are not a member.'
    return landing(request, message)       

@login_required
def league_answers_or_picks(request, league_name, answers_or_picks):
  if answers_or_picks == 'answers':
    answers = True
  elif answers_or_picks == 'picks':
    answers = False
  else:
    return page_not_found(request)
  user = request.user
  league = classes.league.League(league_name)
  member = classes.member.Member(user.username, league_name)
  if not league.get_object() or not member.is_member():
    message = 'Error: League is invalid or you are not a member.'
    return landing(request, message)
  if answers and not member.is_admin():
    message = 'Error: You must be an admin to update league answers.'
    return league_home(request, league_name, message)
  prop_bets = league.get_prop_bets()
  if not answers:
    picks = member.get_picks()
    prop_bet_picks = {}
    for bet in prop_bets.keys():
      if bet in picks:
        prop_bet_picks[bet] = picks[bet]
      else:
        prop_bet_picks[bet] = None
    prop_bets = prop_bet_picks
  context = {
    'user': user,
    'league_name': league_name,
    'prop_bets': prop_bets,
    'answers': answers
  }
  return render(request, 'ui/league_entry.html', context)

@login_required
def league_picks_submit(request):
  user = request.user
  league_name = request.POST.get('league_name')
  picks = {}
  for title, response in request.POST.items():
    if title != 'league_name' and title != 'csrfmiddlewaretoken':
      picks[title] = True if response == 'true' else False
  member = classes.member.Member(user, league_name)
  is_member = member.is_member()
  if (picks and is_member):
    success = member.update_picks(picks)
    if success:
      message = 'Successfully updated picks.'
    else:
      message = 'Unable to update picks.'
  elif picks:
    message = 'Error: League is invalid or you are not a member.'
    return landing(request, message)
  else:
    message = 'Error: Picks block is invalid or missing.'
  return league_home(request, league_name, message)        

@login_required
def league_answers_submit(request):
  user = request.user
  league_name = request.POST.get('league_name')
  answers = {}
  for title, response in request.POST.items():
    if title != 'league_name' and title != 'csrfmiddlewaretoken':
      answers[title] = True if response == 'true' else False
  league = classes.league.League(league_name)
  member = classes.member.Member(user, league_name)
  is_member = member.is_member()
  is_admin = member.is_admin()
  if (answers and is_admin):
    success = league.update_answers(answers)
    if success:
      message = 'Successfully updated league answers.'
    else:
      message = 'Unable to update league answers.'
  elif answers and is_member:
    message = 'Error: You must be an admin to update league answers.'
  elif answers:
    message = 'Error: League is invalid or you are not a member.'
    return landing(request, message)
  else:
    message = 'Error: Answers block is invalid or missing.'
  return league_home(request, league_name, message) 

@login_required
def league_scoreboard(request, league_name):
  user = request.user 
  member = classes.member.Member(user, league_name)
  league = classes.league.League(league_name)
  if member.is_member():
    scores = league.get_scoreboard()
  else:
    message = 'Error: League is invalid or you are not a member.'
    return landing(request, message)
  context = {
    'scores': scores
  }
  return render(request, 'ui/league_scoreboard.html', context)

def page_not_found(request, exception=''):
  return render(request, '404.html', status=404)

def server_error(request):
  return render(request, '500.html', status=500)  