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

	def test_add_entry_to_wishlist(self):
		wishlist = Wishlist(0, "mike's wishlist", "mike")
		wishlist_entry = Wishlist_entry(0, "bike")
		wishlist.add_entry(wishlist_entry)
		self.assertEqual(wishlist.entries[0].name, "bike")

	def test_deserialize_wishlist(self):
		data = {"name": "mikes wishlist", "user": "mike", "entries": ["bike", "car", "bar"]}
		wishlist = Wishlist()
		wishlist.deserialize(data)
		self.assertNotEqual(wishlist, None)
		self.assertEqual(wishlist.id, 0)
		self.assertEqual(wishlist.name, "mikes wishlist")
		self.assertEqual(wishlist.user, "mike")
		self.assertEqual(wishlist.entries, ["bike", "car", "bar"])
		wishlist = Wishlist(1)
		wishlist.deserialize(data)
		self.assertNotEqual(wishlist, None)
		self.assertEqual(wishlist.id, 1)
		self.assertEqual(wishlist.name, "mikes wishlist")
		self.assertEqual(wishlist.user, "mike")
		self.assertEqual(wishlist.entries, ["bike", "car", "bar"])		

if __name__ == '__main__':
	unittest.main()