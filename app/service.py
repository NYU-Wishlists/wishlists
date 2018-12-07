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
import os
import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort, Response
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import NotFound
# DatabaseConnectionError
from app.models import Wishlist, Wishlist_entry, DataValidationError
from . import app
from requests import HTTPError, ConnectionError
from retry import retry

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Wishlist REST API Service',
          description='This is a Wishlist store server.',
          doc='/'
          # prefix='/api'
          )


# This namespace is the start of the path i.e., /wishlists
ns = api.namespace('wishlists', description='Wishlist operations')

# Define the model so that the docs reflect what can be sent
list_item = api.model('Item', {
   'id': fields.Integer,
   'name': fields.String
})

wishlist_model = api.model('Wishlist', {

    'id': fields.String(readOnly=True,
                        description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Wishlist'),
    'user': fields.String(required=True,
                          description='The owner of the Wishlist'),
    'entries': fields.List(fields.Nested(list_item), required=True,
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
    return {'status': 400, 'error': 'Bad Request', 'message': message}, 400


"""
@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
     ""Handles Database Errors from connection attempts""
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status':500, 'error': 'Server Error', 'message': message}, 500
"""

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
@app.route('/index')
def index():
    return app.send_static_file('index.html')
	
######################################################################
#  PATH: /wishlists
######################################################################
@ns.route('/', strict_slashes=False)
class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """
    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @ns.doc('list_wishlists')
    @ns.param('wishlist_user', 'List Wishlists of a user')
    @ns.param('wishlist_name', 'Show wishlist with this name')
    @ns.marshal_with(wishlist_model)
    @retry(HTTPError, delay=1, backoff=5, tries=10)
    def get(self):
        """ Retrieves all the wishlists """
        app.logger.info('Request to list wishlists')
        wishlists = []
        wishlist_user = request.args.get('wishlist_user')
        wishlist_name = request.args.get('wishlist_name')
        app.logger.info('Request to list wishlists of user %s with name: %s', wishlist_user, wishlist_name)
		
        if wishlist_user:
            a = Wishlist.find_by_user(wishlist_user)
            ay = [w.serialize() for w in a]

            if wishlist_name:
                b = Wishlist.find_by_name(wishlist_name)
                bee = [w.serialize() for w in b]

                wishlists = [x for x in ay if x in bee]
            else:
                wishlists = ay
        else:
            wishlists = [w.serialize() for w in Wishlist.all()]

        app.logger.info('[%s] Wishlists returned', len(wishlists))
        return wishlists, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW WISHLIST
    # ------------------------------------------------------------------

    @ns.doc('create_wishlists')
    @ns.expect(wishlist_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Wishlist created successfully')
    @ns.marshal_with(wishlist_model, code=201)
    @retry(HTTPError, delay=1, backoff=5, tries=10)
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
        location_url = api.url_for(
            WishlistResource, wishlist_id=wishlist.id, _external=True)
        return wishlist.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

######################################################################
#  PATH: /wishlists/{id}
######################################################################


@ns.route('/<wishlist_id>')
@ns.param('wishlist_id', 'The Wishlist identifier')
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single wishlists
    GET /wishlist/{id} - Returns a wishlist with the id
    PUT /wishlist/{id} - Update a wishlist with the id
    DELETE /wishlist/{id} - Return a wishlist with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @ns.doc('get_wishlist')
    @ns.response(404, 'Wishlist not found')
    @ns.marshal_with(wishlist_model)
    @retry(HTTPError, delay=1, backoff=5, tries=10)
    def get(self, wishlist_id):
        """
        Retrieve a single wishlist

        This endpoint will return a wishlist based on it's id
        """
        app.logger.info(
            "Request to retrieve a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            api.abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found" .format(wishlist_id))
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------

    @ns.doc('delete_wishlist')
    @ns.response(204, 'Wishlist deleted')
    @retry(HTTPError, delay=1, backoff=5, tries=10)
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based on it's id
        """
        app.logger.info(
            'Request to Delete a wishlist with id [%s]', wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete_wishlist()
        return '', status.HTTP_204_NO_CONTENT

        # ------------------------------------------------------------------
    # UPDATE A WISHLIST
    # ------------------------------------------------------------------
    @ns.doc('update_wishlist')
    @ns.expect(wishlist_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(200, 'Wishlist updated successfully')
    @ns.response(404, 'Whislist not found')
    @retry(HTTPError, delay=1, backoff=5, tries=10)
    def put(self, wishlist_id):
        """
        update a Wishlist

        This endpoint will update a Wishlist based on it's id
        """
        app.logger.info(
            'Request to Update a wishlist with id [%s]', wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            app.logger.info('Payload to update = %s', api.payload)
            wishlist.deserialize(api.payload)
            if wishlist.name == None or wishlist.name == "":
                app.logger.info('Payload to update missing name')
                api.abort(status.HTTP_400_BAD_REQUEST, "Missing wishlist name")
            wishlist.save()
        else:
            app.logger.info('Wishlist with id [%s] not found', wishlist_id)
            api.abort(status.HTTP_404_NOT_FOUND, "Wishlist with id {} not found".format(wishlist_id))
        app.logger.info('Wishlist with  id [%s] updated', wishlist.id)
        return '', status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{user_name}/delete_all
######################################################################
@ns.route('/<string:user_name>/delete_all')
@ns.param('user_name', 'The Wishlist owner')
class DeleteAllResource(Resource):
    """ DeleteAll actions on Wishlists"""
    @ns.doc('delete_all_wishlists_of_a_user')
    @ns.response(204, 'All wishlists of the user deleted')
    @retry(HTTPError, delay=1, backoff=5, tries=10)
    def delete(self, user_name):
        """ Removes all wishlists of a user"""
        app.logger.info('Request to delete all wishlists of a user')
        wishlists = Wishlist.find_by_user(user_name)
        for wishlist in wishlists:
            wishlist.delete_wishlist()
        return '', status.HTTP_204_NO_CONTENT


######################################################################
# DELETE ALL WISHLIST DATA (for testing only)
######################################################################
@app.route('/wishlists/reset', methods=['DELETE'])
@retry(HTTPError, delay=1, backoff=5, tries=10)
def wishlists_reset():
    """ Removes all wishlists from the database """
    Wishlist.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type): # pragma: no cover
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          'Content-Type must be {}'.format(content_type))


def initialize_logging(log_level=logging.INFO): # pragma: no cover
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
