# -*- coding: utf-8 -*-

import ui.models as db_models
import classes.league

class PropBet:
  '''A single prop bet item in a given League. Each prop bet can have many 
  associated Picks, each from a different Member in the League.'''
  def __init__(self, title, league_name):
    self.title = title
    self.league_name = league_name
    self.league_object = None
    # stores the corresponding object from the Django ORM
    self.db_object = None
  def __repr__(self):
    return "PropBet(title=%r, league_name=%r)" % (self.title, self.league_name)
  def __str__(self):
    return "{'title': %r, 'league_name': %r}" % (self.title, self.league_name)
  def __eq__(self, other):
    if isinstance(other, PropBet):
      return (self.title == other.title and self.league_name == other.league_name)
    else:
      return NotImplemented  
  def __hash__(self):
    return hash((self.title, self.league_name))  
  def _lookup_league(self):
    self.league_object = classes.league.League(self.league_name).lookup().get_object()
  def create(self):
    self.lookup()
    # must have a valid league, valid title, and be unique
    if self.league_object and self.title and not self.db_object:
      self.db_object = db_models.PropBet(title=self.title, league=self.league_object)
      self.db_object.save()
      return True
    else:
      return False
  def lookup(self):
    self._lookup_league()
    self.db_object = db_models.PropBet.objects.filter(title=self.title, 
      league=self.league_object)
    if len(self.db_object) != 1:
      self.db_object = None
    else:
      self.db_object = self.db_object[0]
    return self
  def update(self, answer):
    self.lookup()
    if self.db_object:
      self.db_object.answer = answer
      self.db_object.save()
      return True
    return False
  def get_title(self):
    return self.title
  def get_league_name(self):
    return self.league_name
  def get_league_object(self):
    if not self.league_object:
      self._lookup_league()
    return self.league_object
  def get_object(self):
    if not self.db_object:
      self.lookup()
    return self.db_object 