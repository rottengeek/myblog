# 使用Werkzeug实现密码散列
from werkzeug.security import generate_password_hash, check_password_hash
# 生成具有过期时间的JSON Web签名
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
# Login提供了一个UserMixin类 默认包含 is_authenticated() 如果用户已经登录，必须返回True，否则返回False
from flask_login import UserMixin
from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    # 使用property装饰器，让对象能够通过点方法访问和修改私有属性 u = User()  u.password = 'cat'
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 用于生成令牌
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 用于检验令牌
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def __repr__(self):
        return '<User %r>' % self.username



# Flask-Login 要求程序实现一个回调函数，使用指定的标识符加载用户
# 加载用户的回调函数接收以Unicode
# 字符串形式表示的用户标识符。如果能找到用户，这
# 个函数必须返回用户对象；否则应该返回None。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))