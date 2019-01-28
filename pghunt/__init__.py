import os
from flask import Flask
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from elasticsearch import Elasticsearch
# from flask_babel import Babel


app = Flask(__name__) 
app.config['SECRET_KEY'] = '9486120d6df77409e74b72ba6f35d4fb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['CELERY_RESULT_BACKEND'] = 'amqp://localhost//'

app.config['ELASTICSEARCH_URL']='http://localhost:9200'
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# app.config['POSTS_PER_PAGE'] = 10

from pghunt import routes
