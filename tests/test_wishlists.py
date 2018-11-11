import unittest
from app.models import Wishlist, Wishlist_entry, DataValidationError

class TestWishlists(unittest.TestCase):

	def setUp(self):
		Wishlist.remove_all()

	def test_create_a_wishlist_entry(self):
		""" Create a wishlist entry and assert that it exists """
		wishlist_entry = Wishlist_entry(0, "bike")
		self.assertTrue(wishlist_entry != None)
		self.assertEqual(wishlist_entry.id, 0)
		self.assertEqual(wishlist_entry.name, "bike")

	def test_create_a_wishlist(self):
		""" Create a wishlist and assert that it exists """
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		self.assertTrue(wishlist != None)
		self.assertEqual(wishlist.id, 0)
		self.assertEqual(wishlist.name, "mike's wishlist")
		self.assertEqual(wishlist.user, "mike")

	def test_add_a_wishlist(self):
		""" Create a wishlist and add it to the database """
		wishlists = Wishlist.all()

		self.assertEqual(wishlists, [])
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		self.assertTrue(wishlist != None)
		self.assertEqual(wishlist.id, 0)
		wishlist.save()
		# Asert that it was assigned an id and shows up in the database
		self.assertEqual(wishlist.id, 1)
		wishlists = Wishlist.all()
		self.assertEqual(len(wishlists), 1)

	def test_update_a_wishlist(self):
		""" Update a Wishlist """
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		wishlist.save()
		self.assertEqual(wishlist.id, 1)
		# Change it an save it
		wishlist.name = "mike's hard wishlist"
		wishlist.save()
		self.assertEqual(wishlist.id, 1)
		# Fetch it back and make sure the id hasn't changed
		# but the data did change
		wishlists = Wishlist.all()
		self.assertEqual(len(wishlists), 1)
		self.assertEqual(wishlists[0].name, "mike's hard wishlist")

	def test_delete_a_wishlist(self):
		""" Delete a Wishlists """
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		wishlist.save()
		self.assertEqual(len(Wishlist.all()), 1)
		# delete the wishlist and make sure it isn't in the database
		wishlist.delete_wishlist()
		self.assertEqual(len(Wishlist.all()), 0)


	""" Currently a redundant test case but may change in the future """
	# def test_add_entry_to_wishlist(self):
	# 	wishlist = Wishlist(0, "mike's wishlist", "mike")
	# 	wishlist_entry = Wishlist_entry(0, "kite")
	# 	wishlist.add_entry(wishlist_entry)
	# 	self.assertEqual(wishlist.entries[0].name, "kite")
	# 	self.assertEqual(len(wishlist.entries), 1)
	# 	wishlist.delete_entry(0)

	""" Currently a redundant test case but may change in the future """
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
		data = {"name": "mikes wishlist", "user": "mike", "entries": [{"id": 0, "name": "bike"}, {"id": 1, "name": "car"}]}
		wishlist = Wishlist()
		wishlist.deserialize(data)
		self.assertNotEqual(wishlist, None)
		self.assertEqual(wishlist.id, 0)
		self.assertEqual(wishlist.name, "mikes wishlist")
		self.assertEqual(wishlist.user, "mike")
		self.assertEqual(wishlist.entries[0].id, 0)
		self.assertEqual(wishlist.entries[1].id, 1)
		self.assertEqual(wishlist.entries[0].name, "bike")
		self.assertEqual(wishlist.entries[1].name, "car")
		wishlist = Wishlist(1)
		wishlist.deserialize(data)
		self.assertNotEqual(wishlist, None)
		self.assertEqual(wishlist.id, 1)
		self.assertEqual(wishlist.name, "mikes wishlist")
		self.assertEqual(wishlist.user, "mike")

	def test_serialize_a_wishlist(self):
		""" Test serialization of a Wishlist """
		wishlist = Wishlist(0, "mike's wishlist", "mike", [Wishlist_entry(0, "car")])
		data = wishlist.serialize()
		self.assertNotEqual(data, None)
		self.assertIn('id', data)
		self.assertEqual(data['id'], 0)
		self.assertIn('name', data)
		self.assertEqual(data['name'], "mike's wishlist")
		self.assertIn('user', data)
		self.assertEqual(data['user'], "mike")

	def test_deserialize_with_no_name(self):
		""" Deserialize a wishlist without a name """
		wishlist = Wishlist()
		data = {"id":0, "user": "Katy"}
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
		Wishlist(0, "mike's wishlist", "mike").save()
		Wishlist(0, "joan's wishlist", "joan").save()
		wishlist = Wishlist.find(2)
		self.assertIsNot(wishlist, None)
		self.assertEqual(wishlist.id, 2)
		self.assertEqual(wishlist.name, "joan's wishlist")

	def test_find_with_no_wishlists(self):
		""" Find a Wishlist with no Wishlists """
		wishlist = Wishlist.find(1)
		self.assertIs(wishlist, None)

	def test_wishlist_not_found(self):
		""" Test for a Wishlist that doesn't exist """
		Wishlist(0, "mike's wishlist", "mike").save()
		wishlist = Wishlist.find(2)
		self.assertIs(wishlist, None)

	def test_find_by_user(self):
		""" Find Wishlist by Category """
		Wishlist(0, "mike's wishlist", "mike").save()
		Wishlist(0, "joan's wishlist", "joan").save()
		wishlists = Wishlist.find_by_user("mike")
		self.assertNotEqual(len(wishlists), 0)
		self.assertEqual(wishlists[0].user, "mike")
		self.assertEqual(wishlists[0].name, "mike's wishlist")

	def test_find_by_name(self):
		""" Find a Wishlist by Name """
		Wishlist(0, "mike's wishlist", "mike").save()
		Wishlist(0, "joan's wishlist", "joan").save()
		wishlists = Wishlist.find_by_name("mike's wishlist")
		self.assertEqual(len(wishlists), 1)
		self.assertEqual(wishlists[0].user, "mike")
		self.assertEqual(wishlists[0].name, "mike's wishlist")

	def test_all(self):
		""" All() should return a list of all wishlists """
		Wishlist(0, "mike's wishlist", "mike").save()
		Wishlist(0, "joan's wishlist", "joan").save()
		wishlists = Wishlist.all()
		self.assertEqual(len(wishlists), 2)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
	unittest.main()