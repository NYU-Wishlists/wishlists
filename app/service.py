
"""
Wishlist services

Paths
-----
GET  /pets - Retrieves a list of pets from the database
GET  /pets{id} - Retrirves a Pet with a specific id
POST /pets - Creates a Pet in the datbase from the posted database
PUT  /pets/{id} - Updates a Pet in the database fom the posted database
DELETE /pets{id} - Removes a Pet from the database that matches the id
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
    """ Handles Pets that cannot be found """
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
				   url=url_for('list_all_wishlists', _external=True)), HTTP_200_OK

				   
######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_all_wishlists():
	""" Retrieves a list of wishlists from the database """
	app.logger.info('Listing wishlists')
	results = []
	results = Wishlist.all()
	return jsonify([wishlist.serialize() for wishlist in results]), HTTP_200_OK

	

######################################################################
# Demo DATA
######################################################################
@app.route('/wishlists/demo', methods=['POST'])
def create_demo_data():
	""" Loads a few wishlists into the database for demos """
	app.logger.info('Loading demo wishlists')
	Wishlist(0, "Wishlist demo 1", "demo user1", [Wishlist_entry(0, "test11"), Wishlist_entry(1, "test12")]).save()
	Wishlist(0, "Wishlist demo 2", "demo user2", [Wishlist_entry(0, "test21"), Wishlist_entry(1, "test22")]).save()
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
