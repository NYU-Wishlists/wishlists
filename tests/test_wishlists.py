import unittest
import os
import json
import mock
from mock import patch
from requests import HTTPError, ConnectionError
from app.models import Wishlist, Wishlist_entry, DataValidationError

VCAP_SERVICES = {
    'cloudantNoSQLDB': [
                {'credentials': {
                    'username': 'admin',
                    'password': 'pass',
                    'host': 'localhost',
                    'port': 5984,
                    'url': 'http://admin:pass@localhost:5984'
                }
                }
    ]
}
######################################################################
#  T E S T   C A S E S
######################################################################


class TestWishlists(unittest.TestCase):

    def setUp(self):
        Wishlist.init_db("test")
        Wishlist.remove_all()

    def test_create_a_wishlist_entry(self):
        """ Create a wishlist entry and assert that it exists """
        wishlist_entry = Wishlist_entry(0, "bike")
        self.assertTrue(wishlist_entry != None)
        self.assertEqual(wishlist_entry.id, 0)
        self.assertEqual(wishlist_entry.name, "bike")

    def test_create_a_wishlist(self):
        """ Create a wishlist and assert that it exists """
        wishlist = Wishlist("mike's wishlist", "mike")
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "mike's wishlist")
        self.assertEqual(wishlist.user, "mike")

    def test_create_a_wishlist_without_name(self):
        """Create a wishlist with no name, assert Error"""
        wishlist_empty = Wishlist()
        self.assertRaises(DataValidationError, wishlist_empty.create)
        wishlist_no_name = Wishlist(wishlist_name=None)
        self.assertRaises(DataValidationError, wishlist_no_name.create)
        wishlist_no_user = Wishlist(wishlist_user=None)
        self.assertRaises(DataValidationError, wishlist_no_user.create)

    def test_add_a_wishlist(self):
        """ Create a wishlist and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = Wishlist("mike's wishlist", "mike")
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        wishlist.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(wishlist.id, None)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].name, "mike's wishlist")
        self.assertEqual(wishlists[0].user, "mike")

    def test_update_a_wishlist(self):
        """ Update a Wishlist """
        wishlist = Wishlist("mike's wishlist", "mike")
        wishlist.save()
        self.assertNotEqual(wishlist.id, None)
        # Change it an save it
        wishlist.name = "mike's hard wishlist"
        wishlist.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].name, "mike's hard wishlist")

    def test_delete_a_wishlist(self):
        """ Delete a Wishlists """
        wishlist = Wishlist("mike's wishlist", "mike")
        wishlist.save()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete_wishlist()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_save_without_attribute(self):
        wishlist_empty = Wishlist()
        self.assertRaises(DataValidationError, wishlist_empty.save)
        wishlist_no_name = Wishlist(wishlist_name=None)
        self.assertRaises(DataValidationError, wishlist_no_name.save)
        wishlist_no_user = Wishlist(wishlist_user=None)
        self.assertRaises(DataValidationError, wishlist_no_user.save)

    @mock.patch('app.models.Wishlist.database.create_document')
    def test_create_error(self, create_mock):
        """Test create wishlist that returns error """
        create_mock.side_effect = HTTPError
        wishlist = Wishlist("mike's wishlist", "mike")
        wishlist.save()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_test(self):
        """ TEST TEST """
        wishlist = Wishlist("mike's wishlist", "mike")
        wishlist.save()
        self.assertNotEqual(wishlist.id, None)
        og_id = wishlist.id

        #change its ID before updating it to trigger try-catch block
        wishlist.id = "asdf123"
        wishlist.name = "mike's hard wishlist"
        wishlist.save()
        # Fetch it back and make sure the id and data hasn't changed
        
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].name, "mike's wishlist")
        self.assertEqual(wishlists[0].id, og_id)


    # """ Currently a redundant test case but may change in the future """
    # def test_add_entry_to_wishlist(self):
    # 	wishlist = Wishlist(0, "mike's wishlist", "mike")
    # 	wishlist_entry = Wishlist_entry(0, "kite")
    # 	wishlist.add_entry(wishlist_entry)
    # 	self.assertEqual(wishlist.entries[0].name, "kite")
    # 	self.assertEqual(len(wishlist.entries), 1)
    # 	wishlist.delete_entry(0)

    # """ Currently a redundant test case but may change in the future """
    # def test_delete_entry_from_wishlist(self):
    # 	wishlist = Wishlist(0, "mike's wishlist", "mike")
    # 	wishlist_entry = Wishlist_entry(0, "car")
    # 	wishlist.add_entry(wishlist_entry)
    # 	self.assertNotEqual(wishlist.entries[0], None)
    # 	self.assertEqual(wishlist.entries[0].id, 0)
    # 	wishlist.delete_entry(0)
    # 	self.assertEqual(len(wishlist.entries), 0)

    def test_deserialize_wishlist(self):
        """ Test deserialization of a Wishlist """
        data = {"name": "mikes wishlist", "user": "mike", "entries": [
            {"id": 0, "name": "bike"}, {"id": 1, "name": "car"}]}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "mikes wishlist")
        self.assertEqual(wishlist.user, "mike")
        self.assertEqual(wishlist.entries[0].id, 0)
        self.assertEqual(wishlist.entries[1].id, 1)
        self.assertEqual(wishlist.entries[0].name, "bike")
        self.assertEqual(wishlist.entries[1].name, "car")
        wishlist = Wishlist(1)
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "mikes wishlist")
        self.assertEqual(wishlist.user, "mike")

    def test_serialize_a_wishlist(self):
        """ Test serialization of a Wishlist """
        wishlist = Wishlist("mike's wishlist", "mike",
                            [Wishlist_entry(0, "car")])
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "mike's wishlist")
        self.assertIn('user', data)
        self.assertEqual(data['user'], "mike")

    def test_deserialize_with_no_name(self):
        """ Deserialize a wishlist without a name """
        wishlist = Wishlist()
        data = {"id": 0, "user": "Katy"}
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a wishlist with no data """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a wishlist with bad data """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, "data")

    def test_find_wishlist(self):
        """ Find a wishlist by ID """
        Wishlist("mike's wishlist", "mike").save()
        saved_wishlist = Wishlist("joan's wishlist", "joan")
        saved_wishlist.save()
        wishlist = Wishlist.find(saved_wishlist.id)
        self.assertIsNot(wishlist, None)
        self.assertEqual(wishlist.id, saved_wishlist.id)
        self.assertEqual(wishlist.name, "joan's wishlist")

    def test_find_with_no_wishlists(self):
        """ Find a Wishlist with no Wishlists """
        wishlist = Wishlist.find("1")
        self.assertIs(wishlist, None)

    def test_wishlist_not_found(self):
        """ Test for a Wishlist that doesn't exist """
        Wishlist("mike's wishlist", "mike").save()
        wishlist = Wishlist.find("2")
        self.assertIs(wishlist, None)

    def test_find_by_user(self):
        """ Find Wishlist by Name """
        Wishlist("mike's wishlist", "mike").save()
        Wishlist("joan's wishlist", "joan").save()
        wishlists = Wishlist.find_by_user("mike")
        self.assertNotEqual(len(wishlists), 0)
        self.assertEqual(wishlists[0].user, "mike")
        self.assertEqual(wishlists[0].name, "mike's wishlist")

    def test_find_by_name(self):
        """ Find a Wishlist by Name """
        Wishlist("mike's wishlist", "mike").save()
        Wishlist("joan's wishlist", "joan").save()
        wishlists = Wishlist.find_by_name("mike's wishlist")
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].user, "mike")
        self.assertEqual(wishlists[0].name, "mike's wishlist")

    def test_all(self):
        """ All() should return a list of all wishlists """
        Wishlist("mike's wishlist", "mike").save()
        Wishlist("joan's wishlist", "joan").save()
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 2)

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Wishlist.init_db()
        self.assertIsNotNone(Wishlist.client)


    def test_connect(self):
        '''Test if client connect works'''
        Wishlist.connect()
        self.assertTrue(Wishlist.client)

    def test_disconnect(self):
        '''Test if client disconnect works'''
        Wishlist.disconnect()
        self.assertFalse(Wishlist.client)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWishlists)
    unittest.TextTestRunner(verbosity=2).run(suite)
