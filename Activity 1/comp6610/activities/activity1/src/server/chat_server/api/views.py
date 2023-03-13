from .models import User
from crypt import crypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from hmac import compare_digest
from json import dumps, loads
from os import urandom
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from time import time


@api_view(['POST'])
def register_view(request):
    """Register a new user. This method expects a username and password value,
    and saves this information to the database."""

    json_request = loads(request.body)

    if 'username' not in json_request:
        return Response({'error': 'Parameter username not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if 'password' not in json_request:
        return Response({'error': 'Parameter password not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    username = json_request['username']
    password = get_user_password_hash(json_request['password'])
    ip_addr = request.META.get('REMOTE_ADDR')

    if is_user_registered(username):
        return Response({'error': f'Username {username} already registered.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    register_user(username, password, ip_addr)
    return Response()


@api_view(['POST'])
def login_view(request):
    """Verify the username and password of a registered user, and return back
    their login token."""

    json_request = loads(request.body)

    if 'username' not in json_request:
        return Response({'error': 'Parameter username not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if 'password' not in json_request:
        return Response({'error': 'Parameter password not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    username = json_request['username']
    password = json_request['password']

    if not is_user_registered(username) or \
            not is_user_password_valid(username, password):
        return Response({'error': 'Given username or password is incorrect.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    return Response({'token': get_user_token(username)})


@api_view(['POST'])
def user_info_view(request):
    """Verify the username and token of a registered user, and then return
    back the details of the user they want to connect with."""

    json_request = loads(request.body)

    if 'username' not in json_request:
        return Response({'error': 'Parameter username not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if 'token' not in json_request:
        return Response({'error': 'Parameter token not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if 'receiver' not in json_request:
        return Response({'error': 'Parameter receiver not found in request.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    s_username = json_request['username']
    s_token = json_request['token']
    s_ip_addr = request.META.get('REMOTE_ADDR')
    r_username = json_request['receiver']

    if not is_user_registered(s_username) or \
            not is_user_token_valid(s_username, s_token):
        return Response({'error': 'Given username or token is incorrect.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if not is_user_registered(r_username):
        return Response({'error': f'Username {r_username} was not found.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    r_token = get_user_token(r_username)
    r_ip_addr = get_user_ip_addr(r_username)
    secret = generate_secret_key()

    s_info = get_encrypted_sender_info(r_token, s_username, s_ip_addr, secret)

    return Response({'receiver': r_username, 'ip_addr': r_ip_addr,
                     'secret': secret, 'senderinfo': s_info})


def is_user_registered(username):
    return User.objects.filter(pk=username).exists()


def register_user(username, password, ip_addr):
    token = generate_user_token()
    user = User(username, password, token, ip_addr)
    user.save()


def get_user_password_hash(password):
    return crypt(password)


def is_user_password_valid(username, password):
    user = User.objects.get(pk=username)
    return compare_digest(user.password, crypt(password, user.password))


def get_user_token(username):
    return User.objects.get(pk=username).token


def is_user_token_valid(username, token):
    return get_user_token(username) == token


def generate_user_token():
    return urandom(16).hex()


def get_user_ip_addr(username):
    return User.objects.get(pk=username).ip_addr


def generate_secret_key():
    return urandom(16).hex()


def get_encrypted_sender_info(key, username, ip_addr, secret):
    timestamp = round(time() * 1000)
    message = dumps({'username': username,
                     'ip_addr': ip_addr,
                     'timestamp': timestamp,
                     'secret': secret})

    key = str.encode(key)
    message = pad(str.encode(message), 16)

    return AES.new(key, AES.MODE_ECB).encrypt(message).hex()
