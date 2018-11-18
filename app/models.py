"""
Models for Wishlist Service

All of the models are stored in this module

Models
------
Wishlist - A wishlist owned by a user
Wishlist Entry - A product entry to a wishlist

"""

import threading, json

class DataValidationError(Exception):
	""" Used for an data validation errors when deserializing """
	pass



class Wishlist_entry(object):
	"""
	Class that represents a Wishlist Entry

	"""
	lock = threading.Lock()
	index = 0
	
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

	def __init__(self, wishlist_id=0, wishlist_name='', wishlist_user='', wishlist_entries=[]):
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

	"""
	It is not yet necessary to be able to add individual wishlist entries
	as this is accomplished by updating the entire wishlist

	# method to add a product entry to a wishlist's product list
	def add_entry(self, wishlist_entry):
		wishlist_entry.id =  len(self.entries)
		self.entries.append(wishlist_entry)

	"""
	def delete_wishlist(self):
		Wishlist.data.remove(self)


	"""
	It is not yet necessary to be able to remove individual wishlist entries
	as this is accomplished by updating the entire wishlist

	# method to delete a product entry from a wishlist's product list		
	def delete_entry(self, ID):
		for i in self.entries:
			if i.id == ID:
				self.entries.remove(i) 

	"""

	def deserialize(self, data):
		"""
		Deserializes a Wishlist from a dictionary
		Args:
		data (dict): A dictionary containing the Wishlist data
		"""
		if not isinstance(data, dict):
			raise DataValidationError('Invalid wishlist: body of request contained bad or no data')
		try:
			self.name = data['name']
			self.user = data['user']
			self.entries = [Wishlist_entry(i['id'], i['name']) for i in data['entries']]

		except KeyError as err:
			raise DataValidationError('Invalid wishlist: missing ' + err.args[0])
		return
    
	def serialize(self):
		""" Serializes a wishlist into a dictionary """
		return {"id": self.id, "name": self.name, "user": self.user, "entries": [entry.serialize() for entry in self.entries]}

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

	@classmethod
	def find(cls, wishlist_id):
		""" Finds a wishlist by its ID """
		if not cls.data:
			return None
		wishlists = [wishlist for wishlist in cls.data if wishlist.id == wishlist_id]
		if wishlists:
			return wishlists[0]
		return None

	@classmethod
	def find_by_user(cls, wishlist_user):
		""" Returns all a user's wishlists

		Args:
			User (string): the owner of the wishlists you want to match
		"""
		return [wishlist for wishlist in cls.data if wishlist.user == wishlist_user]

	@classmethod
	def find_by_name(cls, wishlist_name):
		""" Returns all wishlists with the given name

		Args:
			Name (string): the name of the wishlist you want to match
		"""
		return [wishlist for wishlist in cls.data if wishlist.name == wishlist_name]