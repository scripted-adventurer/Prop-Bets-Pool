# -*- coding: utf-8 -*-

import ui.models as db_models
import classes.user
import classes.league

class Member:
  '''Represents one user's participation in a given League. Each Member can have
  many associated Picks, one for each PropBet in the League.'''
  def __init__(self, user_name, league_name):
    self.user_name = user_name
    self.league_name = league_name
    self.user_object = None
    self.league_object = None
    self.db_object = None
  def __repr__(self):
    return "Member(user_name=%r, league_name=%r)" % (self.user_name, 
      self.league_name)
  def __str__(self):
    return "{'user': %r, 'league': %r}" % (self.user_name, self.league_name)
  def __eq__(self, other):
    if isinstance(other, Member):
      return (self.user_name == other.user_name and 
        self.league_name == other.league_name)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash((self.user_name, self.league_name))
  def _lookup_user(self):
    self.user_object = classes.user.User(self.user_name).lookup().get_object()
  def _lookup_league(self):
    self.league_object = classes.league.League(self.league_name).lookup().get_object()
  def create(self, admin=False):
    self._lookup_user()
    self._lookup_league()
    if self.user_object and self.league_object:
      self.db_object = db_models.Member(user=self.user_object, 
        league=self.league_object, admin=admin)
      self.db_object.save()
      return True
    else:
      return False
  def lookup(self):
    self._lookup_user()
    self._lookup_league()
    self.db_object = db_models.Member.objects.filter(user=self.user_object, 
      league=self.league_object)
    if len(self.db_object) != 1:
      self.db_object = None
    else:
      self.db_object = self.db_object[0]
    return self   
  def delete(self):
    if not self.db_object:
      self.lookup()
    if self.db_object:  
      self.db_object.delete()
      return True
    else:
      return False
  def is_member(self):
    if not self.db_object:
      self.lookup()
    if self.db_object:
      return True
    else:
      return False  
  def is_admin(self):
    if not self.db_object:
      self.lookup()
    if self.db_object and self.db_object.admin:
      return True
    else:
      return False
  def get_picks(self):
    if not self.db_object:
      self.lookup()
    self.picks = {row.prop_bet.title: row.response for row in 
      db_models.Pick.objects.filter(member=self.db_object)}
    return self.picks
  def update_picks(self, picks_map):
    if not self.db_object:
      self.lookup()
    if not self.db_object:
      return False
    if not picks_map:
      return False
    for title, response in picks_map.items():
      pick = classes.pick.Pick(self.user_name, self.league_name, 
        title).create_or_update(response)
      if not pick:
        return False
    return True
  def get_user_name(self):
    return self.user_name
  def get_league_name(self):
    return self.league_name
  def get_user_object(self):
    if not self.user_object:
      self._lookup_user()
    return self.user_object
  def get_league_object(self):
    if not self.league_object:
      self._lookup_league()
    return self.league_object
  def get_object(self):
    if not self.db_object:
      self.lookup()
    return self.db_object