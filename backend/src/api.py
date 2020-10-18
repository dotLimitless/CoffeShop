import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()


@app.route('/drinks')
def get_drinks():
    result = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in result]
    })


@requires_auth('get:drinks-detail')
@app.route('/drinks-detail')
def get_drinks_detail(payload):
    result = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in result]
    })


@requires_auth('post:drinks')
@app.route('/drinks', method=['POST'])
def store_drinks(payload):
    data = request.get_json()
    drink = None

    try:
        drink = Drink(
            title=data['title'],
            recipe=data['recipe']
        )
        drink.insert()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@requires_auth('patch:drinks')
@app.route('/drinks/<id>', method=['PATCH'])
def update_drink(payload, id):
    drink = Drink.query.get(id)

    if not drink:
        abort(404)

    data = request.get_json()

    try:
        drink.title = data['title']
        drink.recipe = data['recipe']
        drink.update()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@requires_auth('delete:drinks')
@app.route('/drinks/<id>', method=['DELETE'])
def delete_drinks(payload, id):
    drink = Drink.query.get(id)

    if not drink:
        abort(404)

    try:
        drink.delete()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500)
    finally:
        db.session.close()


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'unathorized action'
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'bad request'
    }), 400


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'internal server error'
    }), 500
