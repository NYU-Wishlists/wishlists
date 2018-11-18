"""
Wishlist services

Paths:
-----
GET /healthcheck -- Check heart beat
GET  /wishlists/ - Retrieves a list of wishlists from the database
GET  /wishlists/{id}/items - Retrieves a Wishlist with a specific id
GET /wishlists?wishlist_user="username" - Retrieves the list of wishlists for a user
POST /wishlists - Creates a Wishlist in the datbase from the posted database
PUT  /wishlists/{id} - Updates a Wishlist in the database fom the posted database
DELETE /wishlists/{id} - Removes a Wishlist from the database that matches the id
DELETE /wishlists/{wishlist_name} - Removes all wishlists that match a name
DELETE /wishlists/{user_name}/delete_all - Removes all wishlists of a user
"""

import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import NotFound
from app.models import Pet, DataValidationError, DatabaseConnectionError
from . import app

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Wishlist REST API Service',
          description='This is a Wishlist store server.',
          doc='/apidocs/'
          # prefix='/api'
         )


# This namespace is the start of the path i.e., /pets
ns = api.namespace('wishlists', description='Wishlist operations')

# Define the model so that the docs reflect what can be sent
wishlist_model = api.model('Wishlist', {
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Wishlist'),
    'user': fields.String(required=True,
                              description='The owner of the Wishlist'),
    'entries': fields.Boolean(required=True,
                                description='The items of the Wishlist')
})


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = error.message or str(error)
    app.logger.info(message)
    return {'status':400, 'error': 'Bad Request', 'message': message}, 400

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status':500, 'error': 'Server Error', 'message': message}, 500


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)



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
# Delete a wishlist
######################################################################
@app.route('/wishlists/<int:id>', methods =['DELETE'])
def delete_wishlist(id):
    """Removes a wishlist from the database that matches the id """
    wishlist = Wishlist.find(id)
    if wishlist:
        wishlist.delete_wishlist()
    return make_response('', HTTP_204_NO_CONTENT)


@app.route('/wishlists/<wishlist_name>', methods=['DELETE'])
def delete_wishlist_by_name(wishlist_name):
    """Remove wishlists from the database that matches the name"""
    wishlist_list = Wishlist.find_by_name(wishlist_name)
    for wishlist in wishlist_list:
        wishlist.delete_wishlist()
    return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# RETRIEVE A WISHLIST
######################################################################
@app.route('/wishlists/<int:wishlist_id>/items', methods=['GET'])
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

@app.route('/wishlists/<int:wishlist_id>', methods=['PUT'])
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
#  PATH: /wishlists
######################################################################
@ns.route('/', strict_slashes=False)
class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """
    #------------------------------------------------------------------
    # LIST ALL WISHLISTS
    #------------------------------------------------------------------    
    @ns.doc('list_wishlists')
    @ns.param('wishlist_user','List Wishlists of a user')
    @ns.marshal_with(wishlist_model)
    def get(self):
        """ Retrieves all the wishlists """
        app.logger.info('Request to list wishlists')
        wishlists = []
        wishlist_user = request.args.get('wishlist_user')

        if wishlist_user:
            wishlists = Wishlist.find_by_user(wishlist_user)
        else:
            wishlists = Wishlist.all()

        app.logger.info('[%s] Wishlists returned', len(wishlists))
        results = [wishlist.serialize() for wishlist in wishlists]
        return results, HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW WISHLIST
    #------------------------------------------------------------------
    @ns.doc('create_wishlists')
    @ns.expect(wishlist_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Wishlist created successfully')
    @ns.marshal_with(pet_model, code = 201)
    def post(self):
        """
        Creates a Wishlist
        This endpoint will create a Wishlist based the data in the body that is posted
        """
        app.logger.info('Request to Create a wishlist')
        check_content_type('application/json')
        wishlist = Wishlist()
        app.logger.info('Payload = %s', api.payload)
        wishlist.deserialize(api.payload)
        wishlist.save()
        app.logger.info('Wishlist with new id [%s] saved', wishlist.id)
        location_url = api.url_for(WishlistResource, wishlist_id=wishlist.id, _external=True)
        return wishlist.serialize(), status.HTTP_201_CREATED, {'Location':location_url}



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
def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))


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
