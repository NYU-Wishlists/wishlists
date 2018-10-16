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

	@classmethod
	def __next_index(cls):
		""" Generate sthe next index in a continual sequence """
		with cls.lock:
			cls.index += 1
		return cls.index

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

	def add_entry(self, wishlist_entry):
		wishlist_entry.id =  Wishlist_entry.__next_index() #len(self.entries)
		self.entries.append(wishlist_entry)


	def delete_wishlist(self):
		Wishlist.data.remove(self)

	def delete_entry(self, ID):
		for i in self.entries:
			if i.id == ID:
				self.entries.remove(i)

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
			if not isinstance(data['entries'], list):
				raise DataValidationError('Invalid wishlist: body of request contained bad or no data')
			# entries = []
			# for i in data['entries']:
			# 	x = json.loads(i)
			# 	entries.append(x)
			self.entries = [Wishlist_entry(i['id'], i['name']) for i in data['entries']]

		except KeyError as err:
			raise DataValidationError('Invalid wishlist: missing ' + err.args[0])
		return

	@classmethod
	def all(cls):
		""" Returns all of the Wishlists in the database """
		return [wishlist for wishlist in cls.data]

	@classmethod
    def find_by_wishlist_user(cls, wishlist_user):
		""" Returns all Wishlists with the given user id"""
		return [wishlist for wishlist in cls.data if wishlist.user == wishlist_user]

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