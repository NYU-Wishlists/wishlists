"""
Wishlist services

Paths
-----
GET  /wishlists - Retrieves a list of wishlists from the database
GET  /wishlists{id} - Retrirves a Wishlist with a specific id
POST /wishlists - Creates a Wishlist in the datbase from the posted database
PUT  /wishlists/{id} - Updates a Wishlist in the database fom the posted database
DELETE /wishlists{id} - Removes a Wishlist from the database that matches the id
"""

import os
import sys
import logging
from flask import Response, jsonify, request, json, url_for, make_response
from . import app
from models import Wishlist,Wishlist_entry, DataValidationError

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
	""" Handles all data validation issues from the model """
	return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
	""" Handles requests that have bad or malformed data """
	return jsonify(status=400, error='Bad Request', message=error.message), 400

@app.errorhandler(404)
def not_found(error):
	""" Handles wishlists that cannot be found """
	return jsonify(status=404, error='Not Found', message=error.message), 404

@app.errorhandler(405)
def method_not_supported(error):
	""" Handles bad method calls """
	return jsonify(status=405, error='Method not Allowed',
				   message='Your request method is not supported.' \
				   ' Check your HTTP method and try again.'), 405

@app.errorhandler(500)
def internal_server_error(error):
	""" Handles catostrophic errors """
	return jsonify(status=500, error='Internal Server Error', message=error.message), 500


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
	""" Return something useful by default """
	return jsonify(name='Wishlists REST API Service',
					version='1.0',
				   url=url_for('list_wishlists', _external=True)), HTTP_200_OK


######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_wishlists():
	""" Retrieves all the wishlists from the database """
	app.logger.info('Listing wishlists')
	wishlists = []
	wishlist_user = request.args.get('wishlist_user')

	if wishlist_user:
		wishlists = Wishlist.find_by_user(wishlist_user)
	else:
		wishlists = Wishlist.all()

	return jsonify([wishlist.serialize() for wishlist in wishlists]), HTTP_200_OK

######################################################################
# Delete a wishlist
######################################################################
@app.route('/wishlists/<wishlist_id>', methods =['DELETE'])
def delete_wishlist(wishlist_id):
	"""Removes a wishlist from the database that matches the id """
	wishlist = Wishlist.find(wishlist_id)
	if wishlist:
		wishlist.delete_wishlist()
	return make_response('', HTTP_204_NO_CONTENT)


# @app.route('/wishlists/<wishlist_name>', methods=['DELETE'])
# def delete_wishlist_by_name(wishlist_name):
# 	"""Remove wishlists from the database that matches the name"""
# 	wishlist_list = Wishlist.find_by_name(wishlist_name)
# 	for wishlist in wishlist_list:
# 		wishlist.delete_wishlist()
# 	return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# RETRIEVE A WISHLIST
######################################################################
@app.route('/wishlists/<wishlist_id>/items', methods=['GET'])
def get_wishlist(wishlist_id):
	""" Retrieves a Wishlist with a specific id """
	app.logger.info('Finding a Wishlist with id [{}]'.format(wishlist_id))
	wishlist = Wishlist.find(wishlist_id)
	if wishlist:
		message = wishlist.serialize()
		return_code = HTTP_200_OK
	else:
		message = {'error' : 'Wishlist with id: %s was not found' % str(wishlist_id)}
		return_code = HTTP_404_NOT_FOUND
	return jsonify(message), return_code


######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################

@app.route('/wishlists/<wishlist_id>', methods=['PUT'])
def update_wishlist(wishlist_id):
	""" Updates a Wishlist in the database from the posted database """
	app.logger.info('Updating a Wishlist with id [{}]'.format(wishlist_id))
	wishlist = Wishlist.find(wishlist_id)
	if wishlist:
		payload = request.get_json()
		wishlist.deserialize(payload)
		wishlist.id = wishlist_id
		wishlist.save()
		message = wishlist.serialize()
		return_code = HTTP_200_OK
	else:
		message = {'error' : 'Wishlist with id: %s was not found' % str(wishlist_id)}
		return_code = HTTP_404_NOT_FOUND
	return jsonify(message), return_code



######################################################################
# ADD A NEW WISHLIST
######################################################################
@app.route('/wishlists',methods=['POST'])
def create_wishlist():
	""" Creates a Wishlist in the database from the posted database"""
	app.logger.info('Creating a new wishlist')
	payload = request.get_json()
	wishlist = Wishlist()
	wishlist.deserialize(payload)
	wishlist.save()
	Wishlist.logger.info('wishlist with new id [%s] saved!', wishlist.id)

	message = wishlist.serialize()
	response = make_response(jsonify(message), HTTP_201_CREATED)
	response.headers['Location'] = url_for('get_wishlist', wishlist_id=wishlist.id, _external=True)
	return response

######################################################################
# DELETE ALL WISHLISTS OF USER
######################################################################
@app.route('/wishlists/<string:user_name>/delete_all', methods=['DELETE'])
def delete_user_wishlists(user_name):
	""" Removes all wishlists from the database that matches the user name"""
	app.logger.info('Deleting all user id [{}] wishlists'.format(user_name))
	wishlists = Wishlist.find_by_user(user_name)
	for wishlist in wishlists:
		wishlist.delete_wishlist()
	return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# Demo DATA
######################################################################
@app.route('/wishlists/demo', methods=['POST'])
def create_demo_data():
	""" Loads a few wishlists into the database for demos """
	app.logger.info('Loading demo wishlists')
	Wishlist("Wishlist demo 1", "demo user1", [Wishlist_entry(0, "test11"), Wishlist_entry(1, "test12")]).save()
	Wishlist("Wishlist demo 2", "demo user2", [Wishlist_entry(0, "test21"), Wishlist_entry(1, "test22")]).save()
	return make_response(jsonify(message='Created demo wishlists'), HTTP_201_CREATED)

######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################
def initialize_logging(log_level=logging.INFO):
	""" Initialized the default logging to STDOUT """
	if not app.debug:
		print 'Setting up logging...'
		# Set up default logging for submodules to use STDOUT
		# datefmt='%m/%d/%Y %I:%M:%S %p'
		fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
		logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
		# Make a new log handler that uses STDOUT
		handler = logging.StreamHandler(sys.stdout)
		handler.setFormatter(logging.Formatter(fmt))
		handler.setLevel(log_level)
		# Remove the Flask default handlers and use our own
		handler_list = list(app.logger.handlers)
		for log_handler in handler_list:
			app.logger.removeHandler(log_handler)
		app.logger.addHandler(handler)
		app.logger.setLevel(log_level)
		app.logger.info('Logging handler established')
