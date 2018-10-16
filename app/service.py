# Adapted from Professor Rofrano's service.py
# Updated: Oct 15, 2018
"""
Wishlists Service Demo
This is an example of a wishlists service written with Python Flask

Paths:
-----
GET  /wishlists - Retrieves a list of wishlists from the database
GET  /wishlists{id} - Retrirves a Wishlist with a specific id
POST /wishlists - Creates a Wishlist in the datbase from the posted database
PUT  /wishlists/{id} - Updates a Wishlist in the database fom the posted database
DELETe /wishlists{id} - Removes a Wishlist from the database that matches the id
"""

import os
import sys
import logging
from flask import Response, jsonify, request, json, url_for, make_response
from flask_api import status
from . import app
from models import Wishlist, DataValidationError


######################################################################
# GET INDEX                                                          #
######################################################################
@app.route('/')
def index():
    """ Return root url response """
    return jsonify(name='Wishlist Demo REST API Service',
                   version='1.0',
                   url=url_for('list_wishlists', _external=True)), HTTP_200_OK


######################################################################
# LIST ALL WISHLISTS                                                 #
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_wishlists():
    """ Retrieves all the wishlists from the database """
    app.logger.info('Listing wishlists')

    wishlists = []
    wishlist_user = request.args.get('wishlist_user')

    if wishlist_user:
        wishlists = Wishlist.find_by_wishlist_user(wishlist_user)
    else:
        wishlists = Wishlist.all()

    return jsonify([wishlist.serialize() for wishlist in wishlists]), HTTP_200_OK


######################################################################
# ADD A NEW WISHLIST                                                 #
######################################################################
@app.route('/wishlists', methods=['POST'])
def create_wishlists():
    """ Creates a Wishlist in the datbase from the posted database """
    app.logger.info('Creating a new wishlist')

    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.save()
    message = wishlist.serialize()

    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_wishlists', wishlist_id=wishlist.id, _external=True)
    return response


######################################################################
# UPDATE AN EXISTING WISHLIST                                        #
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['PUT'])
def update_wishlists(wishlist_id):
    """ Updates a Wishlist in the database fom the posted database """
    app.logger.info('Updating a Wishlist with id [{}]'.format(wishlist_id))

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    wishlist.save()
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
#   U T I L I T Y   F U N C T I O N S                                #
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
