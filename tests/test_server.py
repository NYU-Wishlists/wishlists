"""
Test cases for the Wishlists Service

Test cases can be run with:
  nosetests
  coverage report -m
"""
import os
import logging
import unittest
import json
from flask_api import status    # HTTP Status Codes
import app.service as service
from app.models import Wishlist
from time import sleep  # use for rate limiting Cloudant Lite :(

######################################################################
#  T E S T   C A S E S
######################################################################


class TestWishlistServer(unittest.TestCase):
    """ Wishlists Server Tests """

    def setUp(self):
        """ Runs before each test """
        self.app = service.app.test_client()
        TestWishlistServer.throttle_api()
        Wishlist.init_db()
        TestWishlistServer.throttle_api()
        Wishlist("Wishlist demo 1", "demo user1", [service.Wishlist_entry(
            0, "test11"), service.Wishlist_entry(1, "test12")]).save()
        TestWishlistServer.throttle_api()
        Wishlist("Wishlist demo 2", "demo user2", [service.Wishlist_entry(
            0, "test21"), service.Wishlist_entry(1, "test22")]).save()
        TestWishlistServer.throttle_api()

    def tearDown(self):
        """ Runs after each test """
        TestWishlistServer.throttle_api()
        Wishlist.remove_all()


    @staticmethod
    def throttle_api():
        """ Throttles the API calls by sleeping """
    if 'VCAP_SERVICES' in os.environ:
        sleep(0.5)


# FlaskRESTPlus takes over the index so we can't test it
    # def test_index(self):
    #	resp = self.app.get('/')
    #	self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #	data = json.loads(resp.data)
    #	self.assertEqual(data['name'], 'Wishlists REST API Service')

    def test_healthcheck(self):
        """ Making Server is till alive """
        resp = self.app.get('/healthcheck')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('Healthy', resp.data)

    def test_delete_wishlist(self):
        """ Delete a wishlist by ID """
        wishlist = Wishlist.find_by_name('Wishlist demo 1')[0]
        wishlist_count = self.get_wishlist_count()
        resp = self.app.delete(
            '/wishlists/{}'.format(wishlist.id), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count, wishlist_count - 1)

    def test_get_wishlists_list(self):
        """ Get a list of Wishlists """
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_query_wishlist_by_user(self):
        """ Get a list of Wishlists for a User"""
        resp = self.app.get(
            '/wishlists', query_string='wishlist_user=demo user2')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(data), 1)
        self.assertTrue('Wishlist demo 2' in resp.data)
        self.assertFalse("Wishlist demo 1" in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['user'], 'demo user2')

    def test_query_wishlist_by_user_and_wishlist_name(self):
        """ Get a list of Wishlists for a User that matches a name"""
        resp = self.app.get(
            '/wishlists', query_string='wishlist_user=demo user2&wishlist_name=Wishlist demo 2')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertTrue('Wishlist demo 2' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['user'], 'demo user2')

    """
	def test_get_wishlist_by_id(self):
		"" Get a wishlist by ID ""
		resp = self.app.get('/wishlists/2/items')
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = json.loads(resp.data)
		self.assertEqual(data['name'], "Wishlist demo 2")
	"""

    def test_get_wishlist_not_found(self):
        "" "Get a wishlist thats not found """
        resp = self.app.get('/wishlists/12')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist(self):
        """ Create a Wishlist """
        # save the current number of wishlists for later comparrison
        wishlist_count = self.get_wishlist_count()
        # add a new wishlist
        new_wishlist = {'name': 'Wishlist demo 3', 'user': 'demo user2', 'entries': [
            {'id': 0, 'name': 'test31'}]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'Wishlist demo 3')
        self.assertEqual(new_json['user'], 'demo user2')
        # check that count has gone up and includes Wishlist demo 3
        user = {'user': 'demo user2'}
        data = json.dumps(user)
        resp = self.app.get('/wishlists', data=data,
                            content_type='application/json')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), wishlist_count + 1)
        self.assertIn(new_json, data)

    """id is assigned automatically, no need for this test"""
    """
	def test_spoof_wishlist_id(self):
		"" Create a Wishlist passing in an id ""
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
	"""

    def test_create_wishlist_with_no_name(self):
        """ Create a Wishlist with the name missing """
        new_wishlist = {'user': 'demo user1', 'entries': [
            {'id': 0, 'name': "test31"}, {'id': 1, 'name': "test32"}]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_with_no_user(self):
        """ Create a Wishlist with the user missing """
        new_wishlist = {'name': 'Wishlist demo 3', 'entries': [
            {'id': 0, 'name': "test31"}, {'id': 1, 'name': "test32"}]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_wishlist_wit_no_entries(self):
        """ Create a Wishlist with the entries missing """
        new_wishlist = {'user': 'demo user1', 'name': 'Wishlist demo 3'}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_wishlist_by_user(self):
        """ Delete a wishlist by user name  """
        user_wishlists = self.get_wishlist_count_by_user('demo user1')
        wishlist_count = self.get_wishlist_count()
        resp = self.app.delete(
            '/wishlists/demo user1/delete_all', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count, wishlist_count - user_wishlists)

# Test update wishlost Resource
# TODO: query an exsisting wishlist instead of creating a new one for each test
    def test_update_wishlist(self):
        """ Update a Wishlist """
        # create a new wishlist to update after
        new_wishlist = {'name': 'Wishlist demo 3', 'user': 'demo user3', 'entries': [
            {'id': 0, 'name': 'test31'}]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        wishlist_id = new_json['id']
        # update wish list
        updated_wishlist = {'name': 'Wishlist demo updated 3', 'user': 'demo user2', 'entries': [
            {'id': 0, 'name': 'test31 update'}, {'id': 1, 'name': 'test32'}]}
        data = json.dumps(updated_wishlist)
        resp = self.app.put('/wishlists/' + wishlist_id,
                            data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/wishlists/' + wishlist_id)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json2 = json.loads(resp.data)
        self.assertEqual(new_json2['name'], 'Wishlist demo updated 3')
        self.assertEqual(new_json2['user'], 'demo user2')

    def test_update_wishlist_with_no_name(self):
        """ Update a wishlist with no name """
        # create a new wishlist to update after
        new_wishlist = {'name': 'Wishlist demo 3', 'user': 'demo user3', 'entries': [
            {'id': 0, 'name': 'test31'}]}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        wishlist_id = new_json['id']
        # update wish list  with an empy name
        updated_wishlist = {'name': '', 'user': 'demo user2', 'entries': [
            {'id': 0, 'name': 'test31 update'}, {'id': 1, 'name': 'test32'}]}
        data = json.dumps(updated_wishlist)
        resp = self.app.put('/wishlists/' + wishlist_id,
                            data=data, content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_wishlist_not_found(self):
        """ Update a wishlist that can't be found """
        new_wish = {"name": "timothy's list", "user": "timothy"}
        data = json.dumps(new_wish)
        resp = self.app.put('/wishlists/0', data=data,
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)



######################################################################
# DELETE ALL WISHLIST DATA
######################################################################
    def test_delete_all_wishlist(self):
        """Removes all wishlists from the database"""
        resp = self.app.delete('/wishlists/reset')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count,0)


    def get_wishlist_count(self):
        """ save the current number of wishlists """
        resp = self.app.get('/wishlists', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)

    def get_wishlist_count_by_user(self, user_name):
        """ save the current number of wishlists for a user """
        user = {'user': user_name}
        userdata = json.dumps(user)
        resp = self.app.get(
            '/wishlists', query_string='wishlist_user={}'.format(user_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)

    

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
