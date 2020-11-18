import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-gidx7ugc.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'auth'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code



def get_token_auth_header():
    """
    This function validate the Authorization header
    and return the token
    """
    if "Authorization" in request.headers:
        auth_header = request.headers.get("Authorization")
        auth_header = auth_header.split(' ')
        # check first if the header contains two parts: bearer and token
        if len(auth_header) != 2:
             raise AuthError({"message": "authorization header is malformed"}, 401)
        # if the first part is not bearer
        elif auth_header[0].lower() != "bearer":
            raise AuthError({"message": "authorization header has no bearer part"}, 401)
        # if the second part doesn't contain the token
        elif not auth_header[1]:
            raise AuthError({"message": "authorization header has no token part"}, 401)
        # if the token exists it will be returned
        else:
            token = auth_header[1]
            return token
    else:
        raise AuthError({"message": "authorization header is missing"}, 401)
 

def check_permissions(permission, payload):
    """ 
    This function checks if authorization permissions are included in the payload
    """

    if 'permissions' not in payload:
        raise AuthError({'message': 'permissions are not included in the payload'}, 401)
    elif permission not in payload['permissions']:
        raise AuthError({'message': 'permissions are not included in the payload'}, 401)
    else:
        return True


def verify_decode_jwt(token):
    """
    This function verfies the decoded JWT
    and return the decoded  payload
    """
    jsonurl = urlopen(f'http://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())


    # Get the header from the token
    header = jwt.get_unverified_header(token)

    # check if kid in header
    if 'kid' in header:
        if header['kid']:
   
            rsa_key = {}
            for key in jwks['keys']:
                # if the kid in jwks matches the kid in the header
                # the rsa key will be created
                if key['kid'] == header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']}
                    
            if rsa_key:
                try:
                    # create the payload
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=ALGORITHMS,
                        audience=API_AUDIENCE,
                        issuer='https://' + AUTH0_DOMAIN + '/'
                    )
                    return payload
                
                # raise exception the the token is claiming a wrong audience.
                except jwt.JWTClaimsError:
                    raise AuthError({
                        'code': 'the claims are invalid',
                        'description': 'please check the audience and issuer.'
                    }, 401)
        
                # raise exception if the token expired
                except jwt.ExpiredSignatureError:
                    raise AuthError({
                'code': 'token has expired',
                'description': 'token expired'
                }, 401)

                # raise exception in case of any error
                except Exception:
                    raise AuthError({
                        'code': 'invalid_header',
                        'description': 'Unable to parse authentication token.'
                    }, 400)
        else:
            raise AuthError({
        'code': 'invalid_header',
        'description': 'Authorization malformed'}, 401)

    else:
        raise AuthError({'code': 'invalid_header',
                         'description': 'Unable to find the appropriate key.'}, 400)


def requires_auth(permission=''):
    """
    This function return the decorator 
    which passes the decoded payload to the decorated method
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator