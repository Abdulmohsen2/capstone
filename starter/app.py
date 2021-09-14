import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor
from auth import AuthError, requires_auth
import datetime


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    return app


app = create_app()


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


# ------------------------ Actor api ------------------------


@app.route('/actors', methods=['GET'])
@requires_auth('get:actors')
def get_actors(jwt):
    try:
        actors = Actor.query.all()
        return jsonify({
            'success': True,
            'actors': [actor.format() for actor in actors]
        }), 200
    except:
        abort(455)


@app.route('/actors', methods=['POST'])
@requires_auth('add:actor')
def add_actor(playload):
    data = request.get_json()

    try:
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')

        actor = Actor(name=name, age=age, gender=gender)
        actor.insert()

        return jsonify({
            'success': True,
            'actors': actor.format()
        })
    except:
        abort(500)


@app.route('/actors/<id>', methods=['PATCH'])
@requires_auth('patch:actor')
def update_actor(playload, id):
    data = request.get_json()
    try:

        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')

        if(name is None and age is None and gender is None):
            abort(422)

        actor = Actor.query.filter(Actor.id == id).one_or_none()
        if actor is None:
            abort(404)

        if 'name' in data:
            actor.name = data['name']
        if 'age' in data:
            actor.age = data['age']
        if 'gender' in data:
            actor.gender = data['gender']

        actor.update()

        return jsonify({
            'success': True,
            'actors': actor.format()
        })
    except:
        abort(500)


@app.route('/actors/<id>', methods=['DELETE'])
@requires_auth('delete:actor')
def delete_actor(playload, id):
    actor = Actor.query.filter(Actor.id == id).one_or_none()
    if actor is None:
        abort(404)
    actor.delete()

    return jsonify({
        'success': True,
        'actors': id
    })

# ------------------------ Movie api ------------------------


@app.route('/movies')
@requires_auth('get:movies')
def get_movies(payload):
    try:

        getMovie = Movie.query.all()
        if not getMovie:
            abort(404)

        return jsonify({
            'success': True,
            'movies': [movie.format() for movie in getMovie]
        })
    except:
        abort(455)


@app.route('/movies', methods=['POST'])
@requires_auth('add:movie')
def add_movie(payload):
    data = request.get_json()

    try:
        title = data.get('title')
        release_date = data.get('release_date')

        # if not title:
        #     abort(422)

        movie = Movie(title=title, release_date=release_date)
        movie.insert()

        return jsonify({
            'success': True,
            'movies': movie.format()
        })
    except:
        abort(422)


@app.route('/movies/<id>', methods=['PATCH'])
@requires_auth('patch:movie')
def update_movie(payload, id):
    data = request.get_json()
    try:

        title = data.get('title')
        release_date = data.get('release_date')
        if title is None and release_date is None:
            abort(422)

        movie = Movie.query.filter(Movie.id == id).one_or_none()
        if movie is None:
            abort(404)
        if 'title' in data:
            movie.title = data['title']
        if 'release_date' in data:
            movie.release_date = data['release_date']
        movie.update()

        return jsonify({
            'success': True,
            'movies': movie.format()
        })
    except:
        abort(500)


@app.route('/movies/<id>', methods=['DELETE'])
@requires_auth('delete:movie')
def delete_movie(payload, id):

    movie = Movie.query.filter(Movie.id == id).one_or_none()
    if not movie:
        abort(404)
    movie.delete()

    return jsonify({
        'success': True,
        'movies': id
    })


@app.errorhandler(400)
def badRequest(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def notFound(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
