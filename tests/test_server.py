
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
from app.models import Wishlist, Wishlist_entry, DataValidationError

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
		
	def test_get_wishlists_list(self):
		""" Get a list of Wishlists """
		resp = self.app.get('/wishlists')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(len(data), 2)	

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

		

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
	unittest.main()
