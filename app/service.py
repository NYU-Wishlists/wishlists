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
from app.models import Wishlist, Wishlist_entry, DataValidationError # DatabaseConnectionError
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
    'id': fields.String(readOnly=True,
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
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # ADD A NEW WISHLIST
    #------------------------------------------------------------------
    @ns.doc('create_wishlists')
    @ns.expect(wishlist_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Wishlist created successfully')
    @ns.marshal_with(wishlist_model, code = 201)
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
#  PATH: /wishlists/{user_name}/delete_all
######################################################################
@ns.route('/<string:user_name>/delete_all')
@ns.param('user_name','The Wishlist owner')
class DeleteAllResource(Resource):
    """ DeleteAll actions on Wishlists"""
    @ns.doc('delete_all_wishlists_of_a_user')
    @ns.response(204, 'All wishlists of the user deleted')
    def delete(self,user_name):
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
def wishlists_reset():
    """ Removes all wishlists from the database """
    Wishlist.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)



######################################################################
#   U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

