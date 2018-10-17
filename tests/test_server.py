
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

    def test_get_wishlist(self):
        """ Get one Wishlist"""
        resp = self.app.get('/wishlists/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Wishlist demo 2')
        self.assertEqual(data['user'], 'demo user2')
        """content"""
        

    def test_create_wishlist(self):
        """ Create a Wishlist """
        # save the current number of wishlists for later comparrison
        wishlist_count = self.get_wishlist_count()
        # add a new pet
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
