import unittest
from app.models import Wishlist, Wishlist_entry, DataValidationError

class TestWishlists(unittest.TestCase):

	def setUp(self):
		Wishlist.remove_all()

	def test_create_a_wishlist_entry(self):
		wishlist_entry = Wishlist_entry(0, "bike")
		self.assertTrue(wishlist_entry != None)
		self.assertEqual(wishlist_entry.id, 0)
		self.assertEqual(wishlist_entry.name, "bike")

	def test_create_a_wishlist(self):
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		self.assertTrue(wishlist != None)
		self.assertEqual(wishlist.id, 0)
		self.assertEqual(wishlist.name, "mike's wishlist")
		self.assertEqual(wishlist.user, "mike")

	def test_add_a_wishlist(self):
		wishlist = Wishlist(0, "mike's wishlist", "mike")


	def test_add_entry_to_wishlist(self):
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		wishlist_entry = Wishlist_entry(0, "kite")
		wishlist.add_entry(wishlist_entry)
		self.assertEqual(wishlist.entries[0].name, "kite")
		self.assertEqual(len(wishlist.entries), 1)
		wishlist.delete_entry(0)


	def test_delete_entry_from_wishlist(self):
		wishlist = Wishlist(0, "mike's wishlist", "claire")
		wishlist_entry = Wishlist_entry(0, "car")
		wishlist.add_entry(wishlist_entry)
		self.assertNotEqual(wishlist.entries[0], None)
		self.assertEqual(wishlist.entries[0].id, 0)
		wishlist.delete_entry(0)
		self.assertEqual(len(wishlist.entries), 0)

	def test_deserialize_wishlist(self):
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
	

if __name__ == '__main__':
	unittest.main()