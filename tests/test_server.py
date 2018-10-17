
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

    def test_get_wishlists_list(self):
	    """ Get a list of Wishlists """
	    resp = self.app.get('/wishlists')
	    self.assertEqual(resp.status_code, status.HTTP_200_OK)
	    data = json.loads(resp.data)
	    self.assertEqual(len(data), 2)

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

######################################################################
# Utility functions
######################################################################


    def get_wishlist_count(self):
        """ save the current number of wishlists """
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
