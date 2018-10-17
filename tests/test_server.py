"""
Test cases for the Wishlists Service

Test cases can be run with:
  nosetests
  coverage report -m
"""

import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
import app.service as service
from app.models import Wishlist

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(unittest.TestCase):
	""" Wishlists Server Tests """

	@classmethod
	def setUpClass(cls):
		""" Run once before all tests """
		service.app.debug = False
		service.initialize_logging(logging.ERROR)

	def setUp(self):
		""" Runs before each test """
		service.Wishlist.remove_all()
		service.Wishlist(0, "Wishlist demo 1", "demo user1", [service.Wishlist_entry(0, "test11"), service.Wishlist_entry(1, "test12")]).save()
		service.Wishlist(0, "Wishlist demo 2", "demo user2", [service.Wishlist_entry(0, "test21"), service.Wishlist_entry(1, "test22")]).save()
		self.app = service.app.test_client()

	def tearDown(self):
		""" Runs after each test """
		service.Wishlist.remove_all()

	def test_index(self):
		""" Test the Home Page """
		resp = self.app.get('/')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['name'], 'Wishlists REST API Service')

   def test_delete_wishlist(self):
        """ Delete a wishlist by ID """
        wishlist = Wishlist.find_by_name('Wishlist demo 1')[0]
        wishlist_count = self.get_wishlist_count()
        resp = self.app.delete('/wishlists/{}'.format(wishlist.id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data),0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count, wishlist_count - 1)

	def test_delete_wishlist_by_name(self):
		""" Delete a wishilist by name """
        wishlist_count = self.get_wishlist_count()
        resp = self.app.delete('/wishlists/{}'.format('Wishlist demo 1'), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data),0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count, wishlist_count - 1)
		
	def test_get_wishlists_list(self):
		""" Get a list of Wishlists """
		resp = self.app.get('/wishlists')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(len(data), 2)	

	def test_get_wishlist(self):
		""" Get one Wishlist"""
		resp = self.app.get('/wishlists/2')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['name'], 'Wishlist demo 2')
		self.assertEqual(data['user'], 'demo user2')
		"""content"""
		
	def test_query_wishlist_by_user(self):
		""" Get a list of Wishlists for a User"""
		resp = self.app.get('/wishlists', query_string='wishlist_user=demo user2')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertTrue(len(resp.data) > 0)
		print(resp.data)
		self.assertTrue('Wishlist demo 2' in resp.data)
		self.assertFalse("Wishlist demo 1" in resp.data)
		data = json.loads(resp.data)
		query_item = data[0]
		self.assertEqual(query_item['user'], 'demo user2')

	def test_get_wishlist_by_id(self):
		""" Get a wishlist by ID """
		resp = self.app.get('/wishlists/2')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['name'], "Wishlist demo 2")

	def test_get_wishlist_not_found(self):
		""" Get a wishlist thats not found """
		resp = self.app.get('/wishlists/0')
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_create_wishlist(self):
		""" Create a Wishlist """
		# save the current number of wishlists for later comparrison
		wishlist_count = self.get_wishlist_count()
		# add a new wishlist
		new_wishlist = {'name': 'Wishlist demo 3', 'user':'demo user2', 'entries':[{'id':0,'name':'test31'}]}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		# Make sure location header is set
		location = resp.headers.get('Location', None)
		self.assertIsNotNone(location)
		# Check the data is correct
		new_json = json.loads(resp.data)
		self.assertEqual(new_json['name'], 'Wishlist demo 3')
		self.assertEqual(new_json['user'], 'demo user2')
		self.assertEqual(new_json['entries'][0]['name'], 'test31')
		# check that count has gone up and includes Wishlist demo 3
		user = {'user': 'demo user2'}
		data = json.dumps(user)
		resp = self.app.get('/wishlists', data=data, content_type='application/json')
		data = json.loads(resp.data)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		self.assertEqual(len(data), wishlist_count + 1)
		self.assertIn(new_json, data)

	def test_spoof_wishlist_id(self):
		""" Create a Wishlist passing in an id """
		# add a new wishlist
		new_wishlist = {'id': 999,  'name': 'Wishlist demo 3', 'user': 'demo user2', 'entries': [{'id':0,'name':'test31'}]}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		# Make sure location header is set
		location = resp.headers.get('Location', None)
		self.assertIsNotNone(location)
		# Check the data is correct
		new_json = json.loads(resp.data)
		self.assertNotEqual(new_json['id'], 999)
		self.assertEqual(new_json['name'], 'Wishlist demo 3')
		self.assertEqual(new_json['user'], 'demo user2')
		self.assertEqual(new_json['entries'][0]['name'], 'test31')

	def test_create_wishlist_with_no_name(self):
		""" Create a Wishlist with the name missing """
		new_wishlist = {'user': 'demo user1', 'entries':[{'id': 0, 'name': "test31"}, {'id': 1, 'name': "test32"}]}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_create_wishlist_with_no_user(self):
		""" Create a Wishlist with the user missing """
		new_wishlist = {'name': 'Wishlist demo 3', 'entries':[{'id': 0, 'name': "test31"}, {'id': 1, 'name': "test32"}]}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_create_wishlist_wit_no_entries(self):
		""" Create a Wishlist with the entries missing """
		new_wishlist = {'user': 'demo user1','name': 'Wishlist demo 3'}
		data = json.dumps(new_wishlist)
		resp = self.app.post('/wishlists', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

	def test_update_wishlist(self):
		""" Update a Wishlist """
		new_wishlist = {'name': 'Wishlist demo 3', 'user': 'demo user1', 'entries':[{'id': 0, 'name': "test31"}, {'id': 1, 'name': "test32"}]}
		data = json.dumps(new_wishlist)
		resp = self.app.put('/wishlists/2', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		resp = self.app.get('/wishlists/2')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		new_json = json.loads(resp.data)
		self.assertEqual(new_json['name'],'Wishlist demo 3')
		self.assertEqual(new_json['user'],'demo user1')
		self.assertEqual(new_json['entries'][0]['name'],'test31')
	def test_update_wishlist_with_no_name(self):
		""" Update a wishlist with no name """
		new_wishlist = {'user': 'patty'}
		data = json.dumps(new_wishlist)
		resp = self.app.put('/wishlists/2', data=data, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
	def test_update_wishlist_not_found(self):
		""" Update a wishlist that can't be found """
		new_wish = {"name": "timothy's list", "user": "timothy"}
		data = json.dumps(new_wish)
		resp = self.app.put('/wishlists/0', data=data, content_type='application/json')
		self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

	""" DEPENDS ON DELETE CALL """
	# def test_delete_wishlist(self):
	# 	""" Delete a Wishlist that exists """
	# 	# delete a wishlist
	# 	resp = self.app.delete('/wishlists/2', content_type='application/json')
	# 	self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
	# 	self.assertEqual(len(resp.data), 0)
	# 	resp = self.app.get('/wishlists/2')
	# 	self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

######################################################################
# Utility functions
######################################################################

	def get_wishlist_count(self):
		""" save the current number of wishlists for a user """
		user = {'user': 'demo user2'}
		userdata = json.dumps(user)
		resp = self.app.get('/wishlists', data=userdata, content_type='application/json')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
	unittest.main()