import time
import jwt
from jwt import ExpiredSignatureError
from database.models import User, db, Token, Role
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

class AuthService:

    def __init__(self, config):
        self.secret = config.get("JWT_SECRET", "auth")
        self.algorithm = config.get("JWT_ALGORITHM", "HS256")
        self.access_token_max_age = config.get("ACCESS_TOKEN_MAX_AGE", 10 * 60)
        self.refresh_token_max_age = config.get("REFRESH_TOKEN_MAX_AGE",
                                                3 * 60 * 60)

    def authenticate(self, username, password):
        # 查询数据库以获取用户
        try:
            user = User.query.filter_by(username=username).one()
        except NoResultFound as e:
            raise Exception(f"username:{username} not found.{e}")

        # 检查密码是否匹配
        if not user.check_password(password):
            raise Exception("The provided password is incorrect.")

        # 如果认证成功，生成访问令牌和刷新令牌
        access_token = self.generate_token(
            username, expiration=self.access_token_max_age)
        refresh_token = self.generate_token(
            username, expiration=self.refresh_token_max_age)

        # 将刷新令牌存储到数据库中
        self.store_refresh_token(username, refresh_token)
        self.store_token(username, access_token)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'userinfo': user.to_dict()
        }

    def generate_token(self, username, expiration=10 * 60):
        payload = {
            'sub': username,
            'iat': time.time(),
            'exp': time.time() + expiration
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def decode_token(self, token, verify_exp=True):
        try:
            payload = jwt.decode(token,
                                 self.secret,
                                 algorithms=[self.algorithm],
                                 options={'verify_exp': verify_exp})
            return payload
        except ExpiredSignatureError:
            raise Exception("Token has expired.")
        except Exception as e:
            raise Exception(f"Invalid token: {e}")

    def refresh(self, refresh_token):
        payload = self.decode_token(refresh_token)
        username = payload.get('sub')

        try:
            user = User.query.filter_by(username=username).one()
        except NoResultFound:
            raise Exception("Username not found.")

        # 检查刷新令牌是否在数据库中并且是有效的
        if not self.is_valid_refresh_token(username, refresh_token):
            raise Exception("Invalid refresh token.")

        # 如果刷新令牌是有效的，生成新的访问令牌
        access_token = self.generate_token(
            username, expiration=self.access_token_max_age)
        self.store_token(username, access_token)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'userinfo': user.to_dict()
        }

    def logout(self, refresh_token):
        payload = self.decode_token(refresh_token, verify_exp=False)
        username = payload.get('sub')

        # 删除刷新令牌
        self.delete_refresh_token(username)

        return username

    def is_valid_refresh_token(self, username, refresh_token):
        token = self.get_token_from_db(username)
        if token is None or token.refresh_token != refresh_token:
            return False
        return True

    def is_valid_token(self, username, access_token):
        token = self.get_token_from_db(username)
        if token is None or token.token != access_token:
            return False
        return True

    def verify_token_expiration(self, token):
        try:
            leeway = 60
            payload = jwt.decode(token,
                                 self.secret,
                                 algorithms=[self.algorithm],
                                 options={'verify_exp': True},
                                 leeway=leeway)
            username = payload.get('sub')
            if not self.is_valid_token(username, token):
                raise Exception("Token has expired.")
            return True, payload
        except ExpiredSignatureError:
            raise Exception("Token has expired.")

    def store_refresh_token(self, username, refresh_token):
        token = self.get_token_from_db(username)

        if token:
            # 如果已存在具有相同用户名的记录，则更新它
            token.refresh_token = refresh_token
        else:
            # 如果不存在具有相同用户名的记录，则创建一个新的记录
            token = Token(username=username, refresh_token=refresh_token)

        db.session.add(token)
        db.session.commit()

    def store_token(self, username, access_token):
        token = self.get_token_from_db(username)

        if token:
            # 如果已存在具有相同用户名的记录，则更新它
            token.token = access_token
        else:
            # 如果不存在具有相同用户名的记录，则创建一个新的记录
            token = Token(username=username, token=access_token)

        db.session.add(token)
        db.session.commit()

    def delete_refresh_token(self, username):
        token = self.get_token_from_db(username)
        if token:
            db.session.delete(token)
            db.session.commit()

    def get_token_from_db(self, username):
        try:
            token = Token.query.filter_by(username=username).first()
        except Exception:
            raise Exception("Invalid refresh token.")

        return token

    def get_roles_list(self):
        # 使用 SQLAlchemy 查询来获取所有role记录
        roles = Role.query.all()

        # 将role记录转换为字典列表，以便于序列化为 JSON 格式
        role_list = [role.to_dict() for role in roles]

        return role_list

    def get_users(self):
        users = User.query.all()

        # 将user记录转换为字典列表，以便于序列化为 JSON 格式
        user_list = [user.to_dict() for user in users]

        return user_list

    def create_user(self, user_info):
        try:
            if User.query.filter(User.username ==
                                 user_info['username']).first() is not None:
                raise Exception("Username is already in use.")
            if User.query.filter(
                    User.email == user_info['email']).first() is not None:
                raise Exception("Email is already in use.")

            user = User(**user_info)
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except Exception as e:
            raise Exception(e)

    def update_user(self, user_id, user_info):
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise Exception("User not found.")

            if 'username' in user_info:
                if User.query.filter(User.username == user_info['username'],
                                     User.id != user_id).first() is not None:
                    raise Exception("Username is already in use.")

            if 'email' in user_info:
                if User.query.filter(User.email == user_info['email'], User.id
                                     != user_id).first() is not None:
                    raise Exception("Email is already in use.")

            if 'password' in user_info:
                user.set_password(user_info['password'])

            for field in ['username', 'email', 'role_id', 'experiments']:
                if field in user_info:
                    setattr(user, field, user_info[field])

            db.session.commit()
            return user.to_dict()

        except IntegrityError as e:
            db.session.rollback()
            raise Exception(f"Database error: {e}")

    def delete_user(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            raise Exception("User not found.")
        db.session.delete(user)
        db.session.commit()
        return user_id

    def get_user_info(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            raise Exception("User not found.")
        return user.to_dict()
