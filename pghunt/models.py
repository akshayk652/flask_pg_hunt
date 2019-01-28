from datetime import datetime
from pghunt import db, login_manager
from flask_login import UserMixin
from pghunt.services.search import add_to_index, remove_from_index, query_index


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page, cls.__searchable__)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='user.png')
    password = db.Column(db.String(60), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    posts = db.relationship('Post', backref='owner', passive_deletes=True, lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.account_type}')"


class Post(SearchableMixin, db.Model):
    __searchable__ = ['details', 'title', 'address']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    details = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pg_pic = db.Column(db.String(20), nullable=False, default='default-paying-guest-accommodations-0.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.created_at}')"


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    booked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    book_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"User('{self.id}')"

