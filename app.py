from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse
from starlette.authentication import (
    AuthenticationBackend, AuthenticationError, SimpleUser, UnauthenticatedUser,
    AuthCredentials
)
from starlette.routing import Route
import base64
import binascii
import os
from config import Cfg, constants
from utils.processor import DatabaseServicer
from utils.exceptions import *

CONF = Cfg(os.environ.get(constants.STAGE))


class BasicAuthBackend(AuthenticationBackend):

    async def authenticate(self, request):
        """
            This method validates the authenticity of the request based on the authorization header.
            Authorization Header: a base64 encoded string of the Admin's username (e.g: token c2hla2hhcg== )
        """

        if "Authorization" not in request.headers:
            return
        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != 'token':
                return
            username = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
            raise AuthenticationError('Invalid basic auth credentials')
        if DatabaseServicer.get_user(CONF.DB(), username):
            return AuthCredentials(["authenticated"]), SimpleUser(username)


def on_auth_error(request, exc: Exception):
    return JSONResponse({"error": str(exc), 'status_code': 401})


def search_movies(request):
    """API method for handling read request.
        Authentication: not required
        Additional filter (oneof: name, director, genre)is expected as query parameter.
    """
    try:
        param = request.query_params.items()
        db = DatabaseServicer(CONF)
        print(db.get(param))
        return JSONResponse(db.get(param))
    except CustomException as e:
        return JSONResponse(create_error_status(e))


async def add_movie(request):
    """API method for handling insert request.
        Authentication: required
        This method expects a request body containing the record to be added.
    """

    if request.user.is_authenticated:
        body = await request.json()
        try:
            DatabaseServicer(CONF).insert(body)
            return JSONResponse({'message': 'Hurray!! Movie successfully added.'}, status_code=200)
        except CustomException as e:
            return JSONResponse(create_error_status(e))
    return JSONResponse({'error': 'This action requires authentication', 'status_code': 401})


async def edit_movie(request):
    """API method for handling update request.
        Authentication: required
        This method expects a request body containing the record to be updated.

    """

    if request.user.is_authenticated:
        body = await request.json()
        try:
            db = DatabaseServicer(CONF)
            if not body.get('id'):
                raise InvalidParameterError('id')
            db.update(body)
            return JSONResponse({'message': 'Movie details successfully edited.', 'status_code': 200})
        except CustomException as e:
            return JSONResponse(create_error_status(e))
    return JSONResponse({'error': 'This action requires authentication', 'status_code':401})


def delete_movie(request):
    """API method for handling delete request.
        Authentication: required
        "id" of the record to be deleted is expected as query parameter.

    """

    if request.user.is_authenticated:
        if request.query_params.get('id'):
            try:
                DatabaseServicer(CONF).delete(request.query_params.get('id'))
                return JSONResponse({'message': 'Movie successfully deleted from the face of the earth.',
                                    'status_code': 200})
            except CustomException as e:
                return JSONResponse(create_error_status(e))
        else:
            return JSONResponse({'error': 'This action requires id as query parameter', 'status_code': 401})
    return JSONResponse({'error': 'This action requires authentication', 'status_code': 401})


routes = [
    Route('/api/movies', endpoint=search_movies, methods=['GET']),
    Route('/api/admin/movie/add', endpoint=add_movie, methods=['PUT']),
    Route('/api/admin/movie/remove', endpoint=delete_movie, methods=['DELETE']),
    Route('/api/admin/movie/edit', endpoint=edit_movie, methods=['POST'])

]

middleware = [
    Middleware(AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_auth_error)
]

app = Starlette(debug=CONF.debug, routes=routes, middleware=middleware)

# if __name__ == '__main__':
#     app.run()
