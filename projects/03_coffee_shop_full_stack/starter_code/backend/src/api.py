import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS, cross_origin

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={'/': {'origins': '*'}})


## adding cors headers after each response
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin','*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'POST,GET,PUT,DELETE,PATCH,OPTIONS')
    return response

# db_drop_and_create_all()

## ROUTES

## get drinks ( public endpoint)
@app.route('/drinks')
# this endpoint to get all drinks in the DB
def get_drinks():
    drinks = Drink.query.all()
    drinks = [drink.short() for drink in drinks]

    if len(drinks) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'drinks': drinks
            }), 200


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    drinks = [drink.long() for drink in drinks]
    # if no drinks 404 will be returned
    if len(drinks) == 0:
        abort(404)
    else:
        return jsonify({
            'success': True,
            'drinks': drinks
            }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    try:
        # check if title in post data 
        if 'title' in request.get_json():
            title = request.get_json()['title']
        # check if recipe in post data 
        if 'recipe' in request.get_json():
            recipe = json.dumps(request.get_json()['recipe'])
        if 'title' in request.get_json() and 'recipe' in request.get_json():
            drink = Drink(title=title, recipe=recipe)
            drink.insert()
            return jsonify({'success': True, 'drinks': [drink.long()]}, 200)

    except BaseException:
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    try:
        drink = Drink.query.get(id)
        # check if title in post data 
        if 'title' in request.get_json():
            title = request.get_json()['title']
            drink.title = title
        # check if recipe in post data 
        if 'recipe' in request.get_json():
            recipe = json.dumps(request.get_json()['recipe'])
            drink.recipe = recipe

        drink.update()
        return jsonify({'success': True, 'drinks': [drink.long()]}, 200)
    
    except BaseException:
        # if the object is not exist a 404 error will be returned
        abort(404)
    

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        drink = Drink.query.get(id)
        drink.delete()
        return jsonify({'success': True, 'delete': id}, 200)
    except BaseException:
        # if the object is not exist a 404 error will be returned
        abort(404)


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": '401',
        "message": "Unauthorized",
    }), 401