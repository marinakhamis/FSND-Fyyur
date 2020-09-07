#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects import postgresql
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from datetime import datetime
from config import *

# TODO (Done): connect to a local postgresql database
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    artist_genre_table = db.Table('artist_genre_table',
                                  db.Column('genre_id', db.Integer, db.ForeignKey(
                                      'Genre.id'), primary_key=True),
                                  db.Column('artist_id', db.Integer, db.ForeignKey(
                                      'Artist.id'), primary_key=True)
                                  )

    venue_genre_table = db.Table('venue_genre_table',
                                 db.Column('genre_id', db.Integer, db.ForeignKey(
                                     'Genre.id'), primary_key=True),
                                 db.Column('venue_id', db.Integer, db.ForeignKey(
                                     'Venue.id'), primary_key=True)
                                 )


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    # Require a venue to have a name and a city
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO (Done): implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    genres = db.Column(db.String())

    shows = db.relationship('Show', backref='venue',
                            cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Venue id={self.id} name={self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), primary_key=True)
    show_time = db.Column(db.DateTime(), primary_key=True)

    def __repr__(self):
        return f'<Show artist_id={self.artist_id} venue_id={self.venue_id} time={self.show_time}>'
