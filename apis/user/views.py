from flask import Blueprint, jsonify, request, current_app
from utils.utils import make_response
from log import logging

user = Blueprint('user', __name__)


@user.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        auth_service = current_app.config['AUTH_SERVICE']
        response = auth_service.authenticate(username, password)

        if 'error' in response:
            return make_response(500, data=None, message=response['message'])

        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        access_token_max_age = auth_service.access_token_max_age
        refresh_token_max_age = auth_service.refresh_token_max_age

        resp = make_response(200, data=response, message="login success")
        resp[0].set_cookie('access_token',
                           access_token,
                           max_age=access_token_max_age,
                           path='/',
                           secure=False,
                           httponly=True)
        resp[0].set_cookie('refresh_token',
                           refresh_token,
                           max_age=refresh_token_max_age,
                           path='/',
                           secure=False,
                           httponly=True)
        resp[0].set_cookie('logged_in',
                           'true',
                           max_age=access_token_max_age,
                           path='/',
                           secure=False,
                           httponly=False)

        logging.info(f'login success: username:{username}')
        return resp
    except Exception as e:
        logging.error(f'login username:{username} error : {e}')
        return make_response(500, data=None, message=str(e))


@user.route('/logout', methods=['POST'])
def logout():
    try:
        refresh_token = request.cookies.get('refresh_token')
        auth_service = current_app.config['AUTH_SERVICE']
        username = auth_service.logout(refresh_token)
        logging.info(f"logout success, username：{username}")

        resp = make_response(200,
                             data=None,
                             message=f"logout success, username：{username}")
        resp[0].set_cookie('access_token',
                           "",
                           max_age=-1,
                           path='/',
                           secure=False,
                           httponly=True)
        resp[0].set_cookie('refresh_token',
                           "",
                           max_age=-1,
                           path='/',
                           secure=False,
                           httponly=True)
        resp[0].set_cookie('logged_in',
                           '',
                           max_age=-1,
                           path='/',
                           secure=False,
                           httponly=False)

        return resp
    except Exception as e:
        logging.error(f'logout error: {e}')
        return make_response(500, data=None, message=f'logout error: {str(e)}')


@user.route('/refresh', methods=['POST'])
def refresh():
    try:
        refresh_token = request.cookies.get('refresh_token')
        auth_service = current_app.config['AUTH_SERVICE']
        response = auth_service.refresh(refresh_token)

        access_token = response.get('access_token')
        access_token_max_age = auth_service.access_token_max_age

        resp = make_response(200,
                             data=response,
                             message="refresh token success")
        resp[0].set_cookie('access_token',
                           access_token,
                           max_age=access_token_max_age,
                           path='/',
                           secure=False,
                           httponly=True)
        resp[0].set_cookie('logged_in',
                           'true',
                           max_age=access_token_max_age,
                           path='/',
                           secure=False,
                           httponly=False)

        return resp
    except Exception as e:
        logging.error(f'refresh error: {e}')
        return make_response(401,
                             data=None,
                             message=f'refresh error: {str(e)}')


@user.route('/groups', methods=['GET'])
def get_groups():
    try:
        auth_service = current_app.config['AUTH_SERVICE']
        groups = auth_service.get_roles_list()

        # 返回包含两个组的列表
        return make_response(200,
                             data=groups,
                             message="Groups fetched successfully")
    except Exception as e:
        logging.error(f'Error fetching groups: {e}')
        return make_response(500,
                             data=None,
                             message=f'Error fetching groups: {str(e)}')


@user.route('/user', methods=['GET'])
def get_user_list():
    try:
        auth_service = current_app.config['AUTH_SERVICE']
        user_list = auth_service.get_users()
        logging.info('get user list success')
        return make_response(200,
                             data=user_list,
                             message="get user list success")
    except Exception as e:
        logging.error(f'logout error: {e}')
        return make_response(500,
                             data=None,
                             message=f'get user list error: {str(e)}')


@user.route('/user', methods=['POST'])
def add_user():
    try:
        user_info = request.json
        auth_service = current_app.config['AUTH_SERVICE']
        created_user = auth_service.create_user(user_info)

        logging.info(
            f'User created successfully,username:{created_user["username"]}')
        return make_response(200,
                             data=created_user,
                             message="User created successfully")
    except Exception as e:
        logging.error(f'User creation error: {e}')
        return make_response(500,
                             data=None,
                             message=f'User creation error: {str(e)}')


@user.route('/user/<string:userid>', methods=['PUT'])
def update_user(userid):
    try:
        user_info = request.json
        auth_service = current_app.config['AUTH_SERVICE']

        update_user_data = auth_service.update_user(userid, user_info)
        logging.info(
            f'User updated successfully,username:{update_user_data["username"]}'
        )
        return make_response(200,
                             data=update_user_data,
                             message="User updated successfully")
    except Exception as e:
        logging.error(f'User update error: {e}')
        return make_response(500,
                             data=None,
                             message=f'User update error: {str(e)}')


@user.route('/user/<string:userid>', methods=['DELETE'])
def delete_user(userid):
    try:
        auth_service = current_app.config['AUTH_SERVICE']
        user_id = auth_service.delete_user(userid)
        logging.info(f'User delete successfully,info:{user_id}')
        return make_response(200,
                             data=user_id,
                             message="User deleted successfully")
    except Exception as e:
        logging.error(f'User delete error: {e}')
        return make_response(500,
                             data=None,
                             message=f'User deletion error: {str(e)}')


@user.route('/user/<string:userid>', methods=['GET'])
def get_user_info(userid):
    try:
        auth_service = current_app.config['AUTH_SERVICE']
        user_info = auth_service.get_user_info(userid)
        logging.info('get user info success')
        return make_response(200,
                             data=user_info,
                             message="get user info success")
    except Exception as e:
        logging.error(f'logout error: {e}')
        return make_response(500,
                             data=None,
                             message=f'get user info error: {str(e)}')
