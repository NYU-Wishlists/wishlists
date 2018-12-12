"""
Models for Wishlist Service

All of the models are stored in this module

Models
------
Wishlist - A wishlist owned by a user
Wishlist Entry - A product entry to a wishlist

"""

import threading
import json
import os
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError
from retry import retry

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

class DataValidationError(Exception):
	""" Used for an data validation errors when deserializing """
	pass


class DatabaseConnectionError(ConnectionError):
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
	logger = logging.getLogger(__name__)
	client = None
	database = None

	"""
	Class that represents a Wishlist

	"""
	lock = threading.Lock()
	data = []
	index = 0

	def __init__(self, wishlist_name=None, wishlist_user=None, wishlist_entries=[]):
		""" Initialize a wishlist """
		self.id = None
		self.name = wishlist_name
		self.user = wishlist_user
		self.entries = wishlist_entries

	def equals(self, other): # pragma: no cover
		return self.__dict__ == other.__dict__

	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def create(self):
		"""
		Creates a new Wishlist in the database
		"""
		if self.name is None or self.user is None:   # name is the only required field
			raise DataValidationError('name attribute is not set')

		try:
			document = self.database.create_document(self.serialize())
		except HTTPError as err:
			Wishlist.logger.warning('Create failed: %s', err)
			return

		if document.exists():
			self.id = document['_id']

	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def update(self):
		"""
		Updates a Wishlist in the database
		"""
		try:
			document = self.database[self.id]
		except KeyError:
			document = None
		if document:
			document.update(self.serialize())
			document.save()

	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def save(self):
		"""
		Saves a Wishlist to the data store
		"""
		if self.name is None or self.user is None:   # name is the only required field
			raise DataValidationError('name attribute is not set')
		if self.id:
			self.update()
		else:
			self.create()
		# if self.id == 0:
		#     self.id = self.__next_index()
		#     Wishlist.data.append(self)
		# else:
		#     for i in range(len(Wishlist.data)):
		#         if Wishlist.data[i].id == self.id:
		#             Wishlist.data[i] = self
		#             break

	"""
	It is not yet necessary to be able to add individual wishlist entries
	as this is accomplished by updating the entire wishlist
	# method to add a product entry to a wishlist's product list
	def add_entry(self, wishlist_entry):
		wishlist_entry.id =  len(self.entries)
		self.entries.append(wishlist_entry)

	"""
	@retry(HTTPError, delay=2, backoff=3, tries=5)
	def delete_wishlist(self):
		try:
			document = self.database[self.id]
		except KeyError:
			document = None
		if document:
			document.delete()

	"""
	It is not yet necessary to be able to remove individual wishlist entries
	as this is accomplished by updating the entire wishlist

	# method to delete a product entry from a wishlist's product list
	def delete_entry(self, ID):
		for i in self.entries:
			if i.id == ID:
				self.entries.remove(i)

	"""

	@retry(HTTPError, delay=2, backoff=3, tries=5)
	def deserialize(self, data):
		"""
		Deserializes a Wishlist from a dictionary
		Args:
		data (dict): A dictionary containing the Wishlist data
		"""
		Wishlist.logger.info(data)
		try:
			self.name = data['name']
			self.user = data['user']
			self.entries = [Wishlist_entry(i['id'], i['name']) for i in data['entries']]

		except KeyError as err:
			raise DataValidationError('Invalid wishlist: missing ' + err.args[0])
		except TypeError as err:
			raise DataValidationError('Invalid wishlist: body of request contained bad or no data')

		# if there is no id and the data has one, assign it
		if not self.id and '_id' in data:
			self.id = data['_id']

		return self

	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def serialize(self):
		""" Serializes a wishlist into a dictionary """
		return {"id": self.id, "name": self.name, "user": self.user, "entries": [entry.serialize() for entry in self.entries]}



######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

	@classmethod
	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def connect(cls):
		""" Connect to the server """
		cls.client.connect()

	@classmethod
	@retry(HTTPError, delay=1, backoff=2, tries=5)
	def disconnect(cls):
		""" Disconnect from the server """
		cls.client.disconnect()

	# Not used anymore, commented out to improve code coverage.
	# @classmethod
	# def __next_index(cls):
	#     """ Generates the next index in a continual sequence """
	#     with cls.lock:
	#         cls.index += 1
	#     return cls.index

	@classmethod
	@retry(HTTPError, delay=2, backoff=3, tries=5)
	def remove_all(cls):
		""" Removes all of the Wishlists from the database """
		for document in cls.database:
			document.delete()

	@classmethod
	@retry(HTTPError, delay=2, backoff=3, tries=5)
	def all(cls):
		""" Returns all of the Wishlists in the database """
		results = []
		for doc in cls.database:
			wishlist = Wishlist().deserialize(doc)
			wishlist.id = doc['_id']
			results.append(wishlist)
		return results


######################################################################
#  F I N D E R   M E T H O D S
######################################################################
	@classmethod
	# @retry(HTTPError, delay=1, backoff=5, tries=10)
	def find_by(cls, **kwargs):
		""" Find records using selector """
		query = Query(cls.database, selector=kwargs)
		results = []
		for doc in query.result:
			wishlist = Wishlist()
			wishlist.deserialize(doc)
			results.append(wishlist)
		return results

	@classmethod
	# @retry(HTTPError, delay=1, backoff=5, tries=10)
	def find(cls, wishlist_id):
		""" Query that finds Pets by their id """
		try:
			document = cls.database[wishlist_id]
			return Wishlist().deserialize(document)
		except KeyError:
			return None

	@classmethod
	# @retry(HTTPError, delay=1, backoff=5, tries=10)
	def find_by_user(cls, wishlist_user):
		""" Returns all a user's wishlists

		Args:
			User (string): the owner of the wishlists you want to match
		"""
		return cls.find_by(user=wishlist_user)

	@classmethod
	# @retry(HTTPError, delay=1, backoff=5, tries=10)
	def find_by_name(cls, wishlist_name):
		""" Returns all wishlists with the given name

		Args:
			Name (string): the name of the wishlist you want to match
		"""
		return cls.find_by(name=wishlist_name)



############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

	@staticmethod
	# @retry(HTTPError, delay=1, backoff=30, tries=10)
	def init_db(dbname='wishlists'):
		"""
		Initialized Coundant database connection
		"""
		opts = {}
		vcap_services = {}
		# Try and get VCAP from the environment or a file if developing
		if 'VCAP_SERVICES' in os.environ:
			Wishlist.logger.info('Running in Bluemix mode.')
			vcap_services = json.loads(os.environ['VCAP_SERVICES'])
		# if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
		elif 'BINDING_CLOUDANT' in os.environ:
			Wishlist.logger.info('Found Kubernetes Bindings')
			creds = json.loads(os.environ['BINDING_CLOUDANT'])
			vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
		else:
			Wishlist.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
			creds = {
				"username": CLOUDANT_USERNAME,
				"password": CLOUDANT_PASSWORD,
				"host": CLOUDANT_HOST,
				"port": 5984,
				"url": "http://"+CLOUDANT_HOST+":5984/"
			}
			vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

		# Look for Cloudant in VCAP_SERVICES
		for service in vcap_services:
			if service.startswith('cloudantNoSQLDB'):
				cloudant_service = vcap_services[service][0]
				opts['username'] = cloudant_service['credentials']['username']
				opts['password'] = cloudant_service['credentials']['password']
				opts['host'] = cloudant_service['credentials']['host']
				opts['port'] = cloudant_service['credentials']['port']
				opts['url'] = cloudant_service['credentials']['url']

		if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
			Wishlist.logger.info('Error - Failed to retrieve options. ' \
							 'Check that app is bound to a Cloudant service.')
			exit(-1)

		Wishlist.logger.info('Cloudant Endpoint: %s', opts['url'])
		try:
			if ADMIN_PARTY:
				Wishlist.logger.info('Running in Admin Party Mode...')
			Wishlist.client = Cloudant(opts['username'],
								  opts['password'],
								  url=opts['url'],
								  connect=True,
								  auto_renew=True,
								  admin_party=ADMIN_PARTY
								 )
		except ConnectionError:
			raise AssertionError('Cloudant service could not be reached')

		# Create database if it doesn't exist
		try:
			Wishlist.database = Wishlist.client[dbname]
		except KeyError:
			# Create a database using an initialized client
			Wishlist.database = Wishlist.client.create_database(dbname)
		# check for success
		if not Wishlist.database.exists():
			raise AssertionError('Database [{}] could not be obtained'.format(dbname))