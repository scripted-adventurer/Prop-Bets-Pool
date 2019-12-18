# -*- coding: utf-8 -*-

import ui.models as db_models
import hashlib
from collections import OrderedDict
import classes.member
import classes.prop_bet

class League:
  '''A logical grouping of Users and PropBets. Can have many associated Members,
  one for each User in the league. Can have many associated PropBets, one for 
  each prop bet item created by the league admin. Must have a globally unique
  name.'''
  def __init__(self, name):
    self.name = name
    # stores the corresponding object from the Django ORM
    self.db_object = None
  def __repr__(self):
    return "League(name=%r)" % (self.name)
  def __str__(self):
    return self.name
  def __eq__(self, other):
    if isinstance(other, League):
      return self.name == other.name
    else:
      return NotImplemented  
  def __hash__(self):
    return hash(self.name)  
  def create(self, username, password, prop_bets):
    if not self.unique_name():
      return False
    if not prop_bets:
      return False
    # create league
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    self.db_object = db_models.League(name=self.name, password=password_hash)
    self.db_object.save()
    # add user as admin
    classes.member.Member(user_name=username, league_name=self.name).create(
      admin=True)
    # add prop bets
    for title in prop_bets:
      title = title.strip()
      classes.prop_bet.PropBet(title=title, league_name=self.name).create()
    return True
  def lookup(self):
    self.db_object = db_models.League.objects.filter(name=self.name)
    if len(self.db_object) == 1:
      self.db_object = self.db_object[0]
    else:
      self.db_object = None
    return self 
  def update_answers(self, answer_map):
    if not self.db_object:
      self.lookup()
    if self.db_object:
      for title, answer in answer_map.items():
        classes.prop_bet.PropBet(title=title, league_name=self.name).update(
          answer=answer)
      return True
    else:
      return False
  def unique_name(self):
    if len(db_models.League.objects.filter(name=self.name)) == 0:
      return True
    else:
      return False
  def correct_password(self, password):
    self.lookup()
    if not password:
      return False
    if self.db_object and (hashlib.sha256(password.encode('utf-8')).hexdigest() == 
      self.db_object.password):
      return True
    else:
      return False 
  def get_prop_bets(self):
    if not self.db_object:
      self.lookup()
    if self.db_object:
      prop_bets = db_models.PropBet.objects.filter(league=self.db_object)
      if len(prop_bets):
        return {row.title:row.answer for row in prop_bets}
      else:
        return {}
    else:
      return None
  def get_scoreboard(self):
    # retrieves each league user's picks, scores them based on the prop bet answers,
    # and returns username/total points pairs sorted by total
    if not self.db_object:
      self.lookup()
    scores = []
    for member in db_models.Member.objects.filter(league=self.db_object):
      score = 0
      for pick in db_models.Pick.objects.filter(member=member):
        if pick.response == pick.prop_bet.answer:
          score += 1
      scores.append({'username': member.user.username, 'score': score})
    scores.sort(key=lambda pair: pair['score'], reverse=True)
    return scores
  def get_name(self):
    return self.name
  def get_object(self):
    if not self.db_object:
      self.lookup()
    return self.db_object 