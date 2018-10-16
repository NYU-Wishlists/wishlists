"""
Models for Wishlist Service

All of the models are stored in this module

Models
------
Wishlist - A wishlist owned by a user
Wishlist Entry - A product entry to a wishlist

"""

import threading

class DataValidationError(Exception):
	""" Used for an data validation errors when deserializing """
	pass

class Wishlist_entry(object):
	"""
	Class that represents a Wishlist Entry

	"""
	lock = threading.Lock()
	
	def __init__(self, entry_id=0, item_name=''):
		""" Initialize a wishlist entry """
		self.id = entry_id
		self.name = item_name

	def serialize(self):
		""" Serializes a Wishlist_entry into a dictionary """
		return {"id": self.id, "name": self.name}
		
		

class Wishlist(object):
	"""
	Class that represents a Wishlist

	"""

	lock = threading.Lock()
	data = []
	index = 0

	def __init__(self, wishlist_id=0, wishlist_name=0, wishlist_user='', wishlist_entries=[]):
		""" Initialize a wishlist """
		self.id = wishlist_id
		self.name = wishlist_name
		self.user = wishlist_user
		self.entries = wishlist_entries

	def save(self):
		"""
		Saves a Wishlist to the data store
		"""

		if self.id == 0:
			self.id = self.__next_index()
			Wishlist.data.append(self)
		else:
			for i in range(len(Wishlist.data)):
				if Wishlist.data[i].id == self.id:
					Wishlist.data[i] = self
					break

	def add_entry(self, wishlist_entry):
		wishlist_entry.id = len(self.entries)
		self.entries.append(wishlist_entry)
		
	def delete_entry(self, ID):
		del self.entries[ID]
    
	def serialize(self):
		""" Serializes a wishlist into a dictionary """
		return {"id": self.id, "wishlist_name": self.name, "user_name": self.user, "entries": [entry.serialize() for entry in self.entries]}
	
	@classmethod
	def __next_index(cls):
		""" Generates the next index in a continual sequence """
		with cls.lock:
			cls.index += 1
		return cls.index

	@classmethod
	def remove_all(cls):
		""" Removes all of the Wishlists from the database """
		del cls.data[:]
		cls.index = 0
		return cls.data
		
	@classmethod
	def all(cls):
		""" Returns all of the Pets in the database """
		return [wishlist for wishlist in cls.data]
