# -*- coding: utf-8 -*-
import hashlib
from django.test import TestCase
from django.contrib.auth.models import User as Auth_User
import ui.models as db_models
import classes.user
import classes.league
import classes.member
import classes.pick
import classes.prop_bet

class DataSetup:
  '''Creates a batch of test data for use in the test case, avoiding conflicts 
  with unique names based on the test_case_name. Saves references to the created 
  data within an array.'''
  def __init__(self, test_case_name):
    self.test_case_name = test_case_name
    self.user = []
    self.league = []
    self.member = []
    self.prop_bet = []
    self.pick = []
  def create_users(self, count):  
    # creates in batches (no dependencies)
    for x in range(0, count):
      name = self.test_case_name + '_user_' + str(x)
      user = classes.user.User(name).create('password')
      self.user.append(user)
  def create_leagues(self, count):
    # creates in batches (no dependencies)
    for x in range(0, count):
      password = hashlib.sha256('password'.encode('utf-8')).hexdigest()
      name = self.test_case_name + '_league_' + str(x)
      league = db_models.League(name=name, password=password)
      league.save()
      self.league.append(league)
  def create_member(self, user, league, admin):
    # creates one at a time (dependent on user and league objects and admin bool)
    member = db_models.Member(user=user, league=league, admin=admin)
    member.save()
    self.member.append(member)
  def create_prop_bet(self, league, answer):
    # creates one at a time (dependent on league object and answer bool)  
    this_id = len(self.prop_bet)
    title = self.test_case_name + '_prop_bet_' + str(this_id)
    prop_bet = db_models.PropBet(league=league, title=title, answer=answer)
    prop_bet.save()
    self.prop_bet.append(prop_bet)
  def create_pick(self, member, prop_bet, response):
    # creates one at a time (dependent on member and prop_bet objects, and a 
    # response bool)
    this_id = len(self.pick)
    title = self.test_case_name + '_pick_' + str(this_id)
    pick = db_models.Pick(member=member, prop_bet=prop_bet, response=response)
    pick.save()
    self.pick.append(pick)


class UserTest(TestCase):
  
  def test_basic(self):
    main = classes.user.User('test_user')
    same = classes.user.User('test_user')
    different = classes.user.User('test_user_2')
    self.assertEqual(repr(main), "User(name='test_user')")
    self.assertEqual(str(main), "test_user")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)
    
  def test_create(self):
    user = classes.user.User('test_user_create')
    user.create('password')
    self.assertEqual(len(Auth_User.objects.filter(username='test_user_create')),
     1)
  
  def test_lookup(self):
    data = DataSetup('user_lookup')
    data.create_users(1)
    user = classes.user.User(data.user[0].name).lookup()
    self.assertEqual(user.name, data.user[0].name)
  
  def test_delete(self):
    data = DataSetup('user_delete')
    data.create_users(1)
    # invalid = User('fake_username').delete()
    # self.assertEqual(invalid, False)
    valid = classes.user.User(data.user[0].name).delete()
    self.assertEqual(valid, True)
    self.assertEqual(len(Auth_User.objects.filter(username=data.user[0].name)),
     0)
  
  def test_get_leagues(self):
    data = DataSetup('user_get_leagues')
    data.create_users(3)
    data.create_leagues(3)
    data.create_member(data.user[1].db_object, data.league[0], False)
    data.create_member(data.user[2].db_object, data.league[1], False)
    data.create_member(data.user[2].db_object, data.league[2], False)

    invalid = classes.user.User('fake_username').get_leagues()
    self.assertEqual(invalid, [])
    no_leagues = classes.user.User(data.user[0].name).get_leagues()
    self.assertEqual(len(no_leagues), 0)
    one_league = classes.user.User(data.user[1].name).get_leagues()
    self.assertEqual(len(one_league), 1)
    multi_leagues = classes.user.User(data.user[2].name).get_leagues()
    self.assertEqual(len(multi_leagues), 2)

  def test_get_methods(self):
    data = DataSetup('user_get_methods')
    data.create_users(1)

    invalid = classes.user.User('invalid_user')
    self.assertEqual(invalid.get_name(), 'invalid_user')
    self.assertEqual(invalid.get_object(), None)
    valid = classes.user.User(data.user[0].name)
    self.assertEqual(valid.get_name(), data.user[0].name)
    self.assertEqual(valid.get_object().username, data.user[0].name)    

class LeagueTest(TestCase):

  def test_basic(self):
    main = classes.league.League('test_league')
    same = classes.league.League('test_league')
    different = classes.league.League('test_league_2')
    self.assertEqual(repr(main), "League(name='test_league')")
    self.assertEqual(str(main), "test_league")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_create(self):
    data = DataSetup('league_create')
    data.create_users(1)     
    data.create_leagues(1)
    
    prop_bets = []
    empty_prop_bet = classes.league.League('new_league_name').create(data.user[0], 
      'password', prop_bets)
    self.assertEqual(empty_prop_bet, False)
    prop_bets = ['test1', 'test2', 'test3']
    non_unique_name = classes.league.League(data.league[0].name).create(data.user[0], 
      'password', prop_bets)
    self.assertEqual(non_unique_name, False)
    valid = classes.league.League('league_create_new').create(data.user[0], 
      'password', prop_bets)
    self.assertEqual(valid, True)
    
    # check objects created
    new_league = db_models.League.objects.get(name='league_create_new')
    new_member = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=new_league, admin=True)
    new_prop_bets = db_models.PropBet.objects.filter(league=new_league)
    new_prop_bets = [row.title for row in new_prop_bets]
    self.assertEqual(new_prop_bets, ['test1', 'test2', 'test3'])

  def test_lookup(self):
    data = DataSetup('league_get_object') 
    data.create_leagues(1)

    invalid_league = classes.league.League('invalid_league').lookup()
    self.assertEqual(invalid_league.db_object, None)
    valid_league = classes.league.League(data.league[0].name).lookup()
    self.assertEqual(valid_league.db_object.name, data.league[0].name)

  def test_update_answers(self):
    data = DataSetup('league_update_answers') 
    data.create_leagues(1)
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')

    answer_map = {data.prop_bet[0].title: True, data.prop_bet[1].title: False,
      data.prop_bet[2].title: True}
    invalid_league = classes.league.League('invalid_league').update_answers(answer_map)
    self.assertEqual(invalid_league, False)
    valid_league = classes.league.League(data.league[0].name).update_answers(answer_map)
    self.assertEqual(valid_league, True)
    self.assertEqual(db_models.PropBet.objects.filter(league=data.league[0], 
      title=data.prop_bet[0].title)[0].answer, True)
    self.assertEqual(db_models.PropBet.objects.filter(league=data.league[0], 
      title=data.prop_bet[1].title)[0].answer, False)
    self.assertEqual(db_models.PropBet.objects.filter(league=data.league[0], 
      title=data.prop_bet[2].title)[0].answer, True)  

  def test_unique_name(self):
    data = DataSetup('league_unique_name')
    data.create_leagues(1)

    not_unique = classes.league.League(data.league[0].name).unique_name()
    self.assertEqual(not_unique, False)
    unique = classes.league.League('invalid_league_name').unique_name()
    self.assertEqual(unique, True)

  def test_correct_password(self):
    data = DataSetup('league_correct_password')
    data.create_leagues(1)

    invalid_league = classes.league.League('invalid_league_name').correct_password(
      'password')
    self.assertEqual(invalid_league, False)
    invalid_password = classes.league.League(data.league[0].name).correct_password( 
      'invalid_password')
    self.assertEqual(invalid_password, False)
    valid = classes.league.League(data.league[0].name).correct_password('password')
    self.assertEqual(valid, True) 

  def test_get_prop_bets(self):
    data = DataSetup('league_get_prop_bets') 
    data.create_leagues(2)
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[1], True)
    data.create_prop_bet(data.league[1], False)
    data.create_prop_bet(data.league[1], True)

    invalid_league = classes.league.League('invalid_league').get_prop_bets()
    self.assertEqual(invalid_league, None)
    valid_blank = classes.league.League(data.league[0].name).get_prop_bets()
    self.assertEqual(valid_blank, {data.prop_bet[0].title: None, 
      data.prop_bet[1].title: None, data.prop_bet[2].title: None})
    valid = classes.league.League(data.league[1].name).get_prop_bets()
    self.assertEqual(valid, {data.prop_bet[3].title: True, 
      data.prop_bet[4].title: False, data.prop_bet[5].title: True})

  def test_get_scoreboard(self):
    data = DataSetup('league_get_scoreboard')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[2].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], True)
    data.create_pick(data.member[0], data.prop_bet[1], False)
    data.create_pick(data.member[0], data.prop_bet[2], True)
    data.create_pick(data.member[1], data.prop_bet[0], False)
    data.create_pick(data.member[1], data.prop_bet[1], False)
    data.create_pick(data.member[1], data.prop_bet[2], False)
    data.create_pick(data.member[2], data.prop_bet[0], False)
    data.create_pick(data.member[2], data.prop_bet[1], True)
    data.create_pick(data.member[2], data.prop_bet[2], False)

    invalid_league = classes.league.League('invalid_league').get_scoreboard()
    self.assertEqual(len(invalid_league), 0)
    valid_league = classes.league.League(data.league[0].name).get_scoreboard()
    self.assertEqual(valid_league, [{'username': data.user[0].name, 'score': 3}, 
      {'username': data.user[1].name, 'score': 1}, 
      {'username': data.user[2].name, 'score': 0}])

  def test_get_methods(self):
    data = DataSetup('league_get_methods')
    data.create_leagues(1)

    invalid = classes.league.League('invalid_league')
    self.assertEqual(invalid.get_name(), 'invalid_league')
    self.assertEqual(invalid.get_object(), None)
    valid = classes.league.League(data.league[0].name)
    self.assertEqual(valid.get_name(), data.league[0].name)
    self.assertEqual(valid.get_object().name, data.league[0].name)

class MemberTest(TestCase):

  def test_basic(self):
    main = classes.member.Member(user_name='test_user', league_name='test_league')
    same = classes.member.Member(user_name='test_user', league_name='test_league')
    different = classes.member.Member(user_name='test_user_2', 
      league_name='test_league_2')
    self.assertEqual(repr(main), "Member(user_name='test_user', league_name='test_league')")
    self.assertEqual(str(main), "{'user': 'test_user', 'league': 'test_league'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_create(self):
    data = DataSetup('member_create')
    data.create_users(2)    
    data.create_leagues(1)

    invalid_league = classes.member.Member(data.user[0], 'invalid_league').create()
    self.assertEqual(invalid_league, False)
    invalid_user = classes.member.Member('invalid_user', 
      data.league[0].name).create(admin=True)
    self.assertEqual(invalid_user, False)
    valid_league_admin_true = classes.member.Member(data.user[0], 
      data.league[0].name).create(admin=True)
    self.assertEqual(valid_league_admin_true, True)
    valid_league_admin_false = classes.member.Member(data.user[1], 
      data.league[0].name).create(admin=False)
    self.assertEqual(valid_league_admin_false, True)

    # check objects created
    member1 = db_models.Member.objects.get(user=data.user[0].get_object(), 
      league=data.league[0], admin=True)
    member2 = db_models.Member.objects.get(user=data.user[1].get_object(), 
      league=data.league[0], admin=False)

  def test_lookup(self):
    data = DataSetup('member_lookup')
    data.create_users(2)    
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)

    invalid_league = classes.member.Member(data.user[0].name, 'invalid_league'
      ).lookup()
    self.assertEqual(invalid_league.db_object, None)
    not_in_league = classes.member.Member(data.user[1].name, data.league[0].name
      ).lookup()
    self.assertEqual(not_in_league.db_object, None)
    valid = classes.member.Member(data.user[0].name, data.league[0].name
      ).lookup()
    self.assertEqual(valid.db_object.league.name, data.league[0].name)

  def test_delete(self):
    data = DataSetup('member_delete')
    data.create_users(2)    
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)

    invalid_league = classes.member.Member(data.user[1].name, 'invalid_league'
      ).delete()
    self.assertEqual(invalid_league, False)
    not_in_league = classes.member.Member(data.user[1].name, data.league[0].name
      ).delete()
    self.assertEqual(not_in_league, False)
    valid = classes.member.Member(data.user[0].name, data.league[0].name).delete()
    self.assertEqual(valid, True)

    # check object deleted
    deleted = db_models.Member.objects.filter(user=data.user[0].get_object(), 
      league=data.league[0], admin=True)
    self.assertEqual(len(deleted), 0)

  def test_is_member(self):
    data = DataSetup('member_is_member')
    data.create_users(2)
    data.create_leagues(1)
    data.create_member(data.user[1].get_object(), data.league[0], False)

    invalid_league = classes.member.Member(data.user[0], 'invalid_league'
      ).is_member()
    self.assertEqual(invalid_league, False)
    not_in_league = classes.member.Member(data.user[0], data.league[0].name
      ).is_member()
    self.assertEqual(not_in_league, False)
    valid = classes.member.Member(data.user[1], data.league[0].name).is_member()
    self.assertEqual(valid, True)

  def test_is_admin(self):
    data = DataSetup('member_is_admin')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[2].get_object(), data.league[0], True)

    invalid_league = classes.member.Member(data.user[0], 'invalid_league'
      ).is_admin()
    self.assertEqual(invalid_league, False)
    not_in_league = classes.member.Member(data.user[0], data.league[0].name
      ).is_admin()
    self.assertEqual(not_in_league, False)
    not_admin = classes.member.Member(data.user[1], data.league[0].name
      ).is_admin()
    self.assertEqual(not_admin, False)
    valid = classes.member.Member(data.user[2], data.league[0].name).is_admin()
    self.assertEqual(valid, True)  

  def test_get_picks(self):
    data = DataSetup('member_get_picks')
    data.create_users(3)
    data.create_leagues(1)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[2].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_pick(data.member[1], data.prop_bet[0], True)
    data.create_pick(data.member[1], data.prop_bet[1], False)
    data.create_pick(data.member[1], data.prop_bet[2], True)

    invalid_league = classes.member.Member(data.user[0].name, 'invalid_league'
      ).get_picks()
    self.assertEqual(invalid_league, {})
    not_in_league = classes.member.Member(data.user[0].name, data.league[0].name
      ).get_picks()
    self.assertEqual(not_in_league, {})
    in_league_no_picks = classes.member.Member(data.user[1].name, data.league[0].name
      ).get_picks()
    self.assertEqual(in_league_no_picks, {})
    in_league_picks = classes.member.Member(data.user[2].name, data.league[0].name
      ).get_picks()
    response = {data.prop_bet[0].title: True, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: True}
    self.assertEqual(in_league_picks, response)

  def test_update_picks(self):
    data = DataSetup('member_update_picks')
    data.create_users(3)    
    data.create_leagues(1)
    data.create_member(data.user[1].get_object(), data.league[0], False)
    data.create_member(data.user[2].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')
    data.create_prop_bet(data.league[0], '')

    pick_map = {}
    invalid_league = classes.member.Member(data.user[0].name, 'invalid_league'
      ).update_picks(pick_map)
    self.assertEqual(invalid_league, False)
    not_in_league = classes.member.Member(data.user[0].name, data.league[0].name
      ).update_picks(pick_map)
    self.assertEqual(not_in_league, False)
    no_picks = classes.member.Member(data.user[1].name, data.league[0].name
      ).update_picks(pick_map)
    self.assertEqual(no_picks, False)
    pick_map = {'invalid_pick_1': True, 'invalid_pick_2': False, 
      'invalid_pick_3': True}
    invalid_picks = classes.member.Member(data.user[2].name, data.league[0].name
      ).update_picks(pick_map)
    self.assertEqual(invalid_picks, False)
    pick_map = {data.prop_bet[0].title: True, data.prop_bet[1].title: False, 
      data.prop_bet[2].title: True}
    valid_picks = classes.member.Member(data.user[2].name, data.league[0].name
      ).update_picks(pick_map)
    self.assertEqual(valid_picks, True)

  def test_get_methods(self):
    data = DataSetup('member_get_methods')   
    data.create_users(1)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)

    invalid = classes.member.Member('invalid_user', 'invalid_league')
    self.assertEqual(invalid.get_user_name(), 'invalid_user')
    self.assertEqual(invalid.get_user_object(), None)
    self.assertEqual(invalid.get_league_name(), 'invalid_league')
    self.assertEqual(invalid.get_league_object(), None)
    self.assertEqual(invalid.get_object(), None)
    valid = classes.member.Member(data.user[0].name, data.league[0].name)
    self.assertEqual(valid.get_user_name(), data.user[0].name)
    self.assertEqual(valid.get_user_object().username, data.user[0].name)
    self.assertEqual(valid.get_league_name(), data.league[0].name)
    self.assertEqual(valid.get_league_object().name, data.league[0].name)
    self.assertEqual(valid.get_object().admin, False)

class PropBetTest(TestCase):

  def test_basic(self):
    main = classes.prop_bet.PropBet(title='test_title', league_name='test_league')
    same = classes.prop_bet.PropBet(title='test_title', league_name='test_league')
    different = classes.prop_bet.PropBet(title='test2', league_name='test_league')
    self.assertEqual(repr(main), "PropBet(title='test_title', league_name='test_league')")
    self.assertEqual(str(main), "{'title': 'test_title', 'league_name': 'test_league'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_create(self):
    data = DataSetup('prop_bet_create')   
    data.create_leagues(1)
    data.create_prop_bet(data.league[0], True)

    invalid_league = classes.prop_bet.PropBet('test1', 'fake_league').create()
    self.assertEqual(invalid_league, False)
    invalid_title = classes.prop_bet.PropBet('', data.league[0].name).create()
    self.assertEqual(invalid_title, False)
    not_unique = classes.prop_bet.PropBet(data.prop_bet[0].title, 
      data.league[0].name).create()
    self.assertEqual(not_unique, False)
    valid = classes.prop_bet.PropBet('test2', data.league[0].name).create()
    self.assertEqual(valid, True)

    # check objects created
    prop_bet = db_models.PropBet.objects.get(title='test2', league=data.league[0])

  def test_lookup(self):
    data = DataSetup('prop_bet_lookup')   
    data.create_leagues(1)
    data.create_prop_bet(data.league[0], True)

    invalid_league = classes.prop_bet.PropBet(data.prop_bet[0].title, 
      'fake_league').lookup()
    self.assertEqual(invalid_league.db_object, None)
    invalid_title = classes.prop_bet.PropBet('fake_title', data.league[0].name
      ).lookup()
    self.assertEqual(invalid_title.db_object, None)
    valid = classes.prop_bet.PropBet(data.prop_bet[0].title, 
      data.league[0].name).lookup()
    self.assertEqual(valid.db_object.title, data.prop_bet[0].title)

  def test_update(self):
    data = DataSetup('prop_bet_update')   
    data.create_leagues(1)
    data.create_prop_bet(data.league[0], True)

    invalid_league = classes.prop_bet.PropBet(data.prop_bet[0].title, 
      'fake_league').update(answer=False)
    self.assertEqual(invalid_league, False)
    invalid_title = classes.prop_bet.PropBet('fake_title', data.league[0].name
      ).update(answer=False)
    self.assertEqual(invalid_title, False)
    valid = classes.prop_bet.PropBet(data.prop_bet[0].title, 
      data.league[0].name).update(answer=True)
    self.assertEqual(valid, True)

    # check object updated
    prop_bet = db_models.PropBet.objects.get(title=data.prop_bet[0].title, 
      league=data.league[0], answer=True)

  def test_get_methods(self):
    data = DataSetup('prop_bet_get_methods')   
    data.create_leagues(1)
    data.create_prop_bet(data.league[0], True)

    invalid = classes.prop_bet.PropBet('invalid_title', 'invalid_league')
    self.assertEqual(invalid.get_title(), 'invalid_title')
    self.assertEqual(invalid.get_league_name(), 'invalid_league')
    self.assertEqual(invalid.get_league_object(), None)
    self.assertEqual(invalid.get_object(), None)
    valid = classes.prop_bet.PropBet(data.prop_bet[0].title, data.league[0].name)
    self.assertEqual(valid.get_title(), data.prop_bet[0].title)
    self.assertEqual(valid.get_league_name(), data.league[0].name)
    self.assertEqual(valid.get_league_object(), data.league[0])
    self.assertEqual(valid.get_object(), data.prop_bet[0])

class PickTest(TestCase):

  def test_basic(self):
    main = classes.pick.Pick(user_name='test_user', league_name='test_league', 
      prop_bet_title='test_title')
    same = classes.pick.Pick(user_name='test_user', league_name='test_league', 
      prop_bet_title='test_title')
    different = classes.pick.Pick(user_name='test_user', league_name='test_league', 
      prop_bet_title='test_title_2')
    self.assertEqual(repr(main), 
      "Pick(user_name='test_user', league_name='test_league', prop_bet_title='test_title')")
    self.assertEqual(str(main), 
      "{'user_name': 'test_user', 'league_name': 'test_league', 'prop_bet_title': 'test_title'}")
    self.assertEqual((main == same), True)
    self.assertEqual(hash(main) == hash(same), True)
    self.assertEqual((main == different), False)
    self.assertEqual(hash(main) == hash(different), False)

  def test_lookup(self):
    data = DataSetup('pick_lookup')
    data.create_users(1)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], True)

    invalid_user = classes.pick.Pick(user_name='invalid_user', 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[0].title)
    invalid_user.lookup()
    self.assertEqual(invalid_user.db_object, None)
    invalid_league = classes.pick.Pick(user_name=data.user[0].name, 
      league_name='invalid_league', prop_bet_title=data.prop_bet[0].title)
    invalid_league.lookup()
    self.assertEqual(invalid_league.db_object, None)
    invalid_prop_bet = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title='invalid_prop_bet')
    invalid_prop_bet.lookup()
    self.assertEqual(invalid_prop_bet.db_object, None)
    valid = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[0].title)
    valid.lookup()
    self.assertEqual(valid.db_object.prop_bet.title, data.prop_bet[0].title)

  def test_create_or_update(self):
    data = DataSetup('pick_create_update')   
    data.create_users(1)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], False)

    invalid_user = classes.pick.Pick(user_name='invalid_user', 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[0].title
      ).create_or_update(response=False)
    self.assertEqual(invalid_user, False)
    invalid_league = classes.pick.Pick(user_name=data.user[0].name, 
      league_name='invalid_league', prop_bet_title=data.prop_bet[0].title
      ).create_or_update(response=False)
    self.assertEqual(invalid_league, False)
    invalid_prop_bet = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title='invalid_prop_bet'
      ).create_or_update(response=False)
    self.assertEqual(invalid_prop_bet, False)
    valid_existing = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[0].title
      ).create_or_update(response=True)
    self.assertEqual(valid_existing, True)
    valid_new = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[1].title
      ).create_or_update(response=True)
    self.assertEqual(valid_new, True)

    # check objects created
    pick1 = db_models.Pick.objects.get(member=data.member[0], 
      prop_bet=data.prop_bet[0], response=True)
    pick2 = db_models.Pick.objects.get(member=data.member[0], 
      prop_bet=data.prop_bet[1], response=True)

  def test_get_methods(self):
    data = DataSetup('pick_get_methods')   
    data.create_users(1)
    data.create_leagues(1)
    data.create_member(data.user[0].get_object(), data.league[0], False)
    data.create_prop_bet(data.league[0], True)
    data.create_pick(data.member[0], data.prop_bet[0], True)

    invalid = classes.pick.Pick(user_name='invalid_user', 
      league_name='invalid_league', prop_bet_title='invalid_title')
    self.assertEqual(invalid.get_user_name(), 'invalid_user')
    self.assertEqual(invalid.get_user_object(), None)
    self.assertEqual(invalid.get_league_name(), 'invalid_league')
    self.assertEqual(invalid.get_league_object(), None)
    self.assertEqual(invalid.get_member_object(), None)
    self.assertEqual(invalid.get_prop_bet_title(), 'invalid_title')
    self.assertEqual(invalid.get_prop_bet_object(), None)
    self.assertEqual(invalid.get_object(), None)
    valid = classes.pick.Pick(user_name=data.user[0].name, 
      league_name=data.league[0].name, prop_bet_title=data.prop_bet[0].title)
    self.assertEqual(valid.get_user_name(), data.user[0].name)
    self.assertEqual(valid.get_user_object().username, data.user[0].name)
    self.assertEqual(valid.get_league_name(), data.league[0].name)
    self.assertEqual(valid.get_league_object().name, data.league[0].name)
    self.assertEqual(valid.get_member_object().admin, False)
    self.assertEqual(valid.get_prop_bet_title(), data.prop_bet[0].title)
    self.assertEqual(valid.get_prop_bet_object().title, data.prop_bet[0].title)
    self.assertEqual(valid.get_object().response, True) 