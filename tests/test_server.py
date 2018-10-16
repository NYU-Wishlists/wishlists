
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

		

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
