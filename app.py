#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
from datetime import *
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, inspect
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from flask_migrate import Migrate
from config import *
from models import *
from forms import *
# to solve this error : sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) table "Show" does not exist
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
import re
import sys
#----------------------------------------------------------------------------#
# Models. Have been moved to a file called " models.py "
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#----------------------------------------------------------------------------#
# Venues
#----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
    # TODO (Done): replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    # Getting all venues and sorting them by city name
    venues = Venue.query.order_by('city').all()

    # To make sure that venues are unique
    places = set()

    for venue in venues:
        # Adding cities and states
        places.add((venue.city, venue.state))

    # for each unique city/state, add venues
    for place in places:
        data.append({
            "city": place[0],
            "state": place[1],
            "venues": []
        })

    for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # get current date to filter num_upcoming_shows
        current_date = datetime.now()

        for show in shows:
            if show.start_time > current_date:
                num_upcoming_shows += 1

        for venue_place in data:
            if venue.state == venue_place['state'] and venue.city == venue_place['city']:
                venue_place['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": num_upcoming_shows
                })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO(Done): implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop"
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    # To know more about "ilike" operator Check this article " https://www.geeksforgeeks.org/postgresql-ilike-operator/ " ♥
    results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(results),
        "data": [{
            "id": result.id,
            "name": result.name,
            "num_upcoming_shows": len([show for show in result.shows if show.show_time > datetime.now()]),
        } for result in results]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO (Done): replace with real venue data from the venues table, using venue_id     venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    current_time = datetime.now()

    for show in shows:
        data = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        # To determine if the show is in the future or in the past
        if show.start_time > current_time:
            upcoming_shows.append(data)

        else:
            past_shows.append(data)

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows)
        }

    return render_template('pages/show_venue.html', venue=data)


#  ----------------------------------------------------------------
# Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO (Done): insert form data as a new Venue record in the db, instead
    # TODO (Done): modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    flashType = 'danger'
    if form.validate():
        try:
            newVenue = Venue(
                name=request.form['name'],
                city=request.form['city'],
                state=request.form['state'],
                address=request.form['address'],
                phone=request.form['phone'],
                genres=request.form.getlist('genres'),
                facebook_link=request.form['facebook_link']
            )
            db.session.add(newVenue)
            db.session.commit()
            # on successful db insert, flash success
            flashType = 'success'
            flash('Venue {} was successfully listed!'.format(newVenue.name))
        except:
            # TODO DONE: on unsuccessful db insert, flash an error instead.
            flash('An error occurred due to database insertion error. Venue {} could not be listed.'.format(
                request.form['name']))
        finally:
            # Close session
            db.session.close()
    else:
        flash(form.errors)
        flash('An error occurred due to form validation. Venue {} could not be listed.'.format(
            request.form['name']))

    return render_template('pages/home.html', flashType=flashType)


""" #Old method :
    try:
        # get form data and create
        form = VenueForm()
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                      phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                      facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,
                      website=form.website.data, seeking_talent=form.seeking_talent.data)

        # commit session to database
        db.session.add(venue)
        db.session.commit()

        # flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # catches errors
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        # closes session
        db.session.close()
    return render_template('pages/home.html') """


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO(Done): Complete this endpoint for taking a venue_id, and using
    venue = Venue.query.get(venue_id)
    if not venue:
        # User somehow faked this call, redirect home
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        venue_name = venue.name
        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting venue {venue_name}.')
            print("Error in delete_venue()")
            abort(500)
        else:
            return jsonify({
                'deleted': True,
                'url': url_for('venues')
            })

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO (Done): replace with real data returned from querying the database
    data = []

    artists = Artist.query.all()

    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO(Done): implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '').strip()
    artists = Artist.query.filter(
        Artist.name.ilike('%' + search_term + '%')).all()

    artist_list = []
    now = datetime.now()
    for artist in artists:
        artist_shows = Show.query.filter_by(artist_id=artist.id).all()
        num_upcoming = 0
        for show in artist_shows:
            if show.start_time > now:
                num_upcoming += 1

        artist_list.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming  # FYI, template does nothing with this
        })

    response = {
        "count": len(artists),
        "data": artist_list
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO(Done): replace with real venue data from the venues table, using venue_id
    artist = Artist.query.get(artist_id)
    shows = Show.query.filter_by(artist_id=artist_id).all()
    upcoming_shows = []
    past_shows = []
    current_time = datetime.now()

    for show in shows:
        data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": format_datetime(str(show.start_time))
        }
        if show.start_time > current_time:
            upcoming_shows.append(data)

        else:
            past_shows.append(data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "seeking_venue": artist.seeking_venue,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO(Done): populate form with fields from artist with ID <artist_id>
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    artist_data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "facebook_link": artist.facebook_link,
        "image_link": artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist_data)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    if venue:
        venue_info = Venue.details(venue)
        form.name.data = venue_info["name"]
        form.genres.data = venue_info["genres"]
        form.address.data = venue_info["address"]
        form.city.data = venue_info["city"]
        form.state.data = venue_info["state"]
        form.phone.data = venue_info["phone"]
        form.website.data = venue_info["website"]
        form.facebook_link.data = venue_info["facebook_link"]
        form.seeking_talent.data = venue_info["seeking_talent"]
        form.seeking_description.data = venue_info["seeking_description"]
        form.image_link.data = venue_info["image_link"]

        # TODO (Done): populate form with values from venue with ID <venue_id>
        return render_template('forms/edit_venue.html', form=form, venue=venue_info)
    return render_template('errors/404.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    # TODO (Done): take values from the form submitted, and update existing
    try:
        form = VenueForm()
        venue = Venue.query.get(venue_id)
        name = form.name.data
        venue.name = name
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()
        flash('Venue ' + name + ' has been updated')
    except:
        db.session.rollback()
        flash('Sorry, an error occured while trying to update Venue')

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO(Done): insert form data as a new Venue record in the db, instead
    # TODO(Done): modify data to be the data object returned from db insertion
    try:
        form = ArtistForm()

        artist = Artist(name=form.name.data, city=form.city.data, state=form.city.data,
                        phone=form.phone.data, genres=form.genres.data,
                        image_link=form.image_link.data, facebook_link=form.facebook_link.data)

        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO(Done): on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm()
    name = form.name.data.strip()
    city = form.city.data.strip()
    state = form.state.data
    phone = form.phone.data
    phone = re.sub('\D', '', phone)
    genres = form.genres.data
    seeking_venue = True if form.seeking_venue.data == 'Yes' else False
    seeking_description = form.seeking_description.data.strip()
    image_link = form.image_link.data.strip()
    website = form.website.data.strip()
    facebook_link = form.facebook_link.data.strip()

    if not form.validate():
        flash(form.errors)
        return redirect(url_for('edit_artist_submission', artist_id=artist_id))

    else:
        error_in_update = False

        try:

            artist = Artist.query.get(artist_id)
            artist.name = name
            artist.city = city
            artist.state = state
            artist.phone = phone
            artist.seeking_venue = seeking_venue
            artist.seeking_description = seeking_description
            artist.image_link = image_link
            artist.website = website
            artist.facebook_link = facebook_link
            artist.genres = []

            for genre in genres:
                fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
                if fetch_genre:
                    artist.genres.append(fetch_genre)

                else:
                    new_genre = Genre(name=genre)
                    db.session.add(new_genre)
                    artist.genres.append(new_genre)

            db.session.commit()
        except Exception as e:
            error_in_update = True
            print(f'Exception "{e}" in edit_artist_submission()')
            db.session.rollback()
        finally:
            db.session.close()

        if not error_in_update:
            flash('Artist ' + request.form['name'] +
                  ' was successfully updated!')
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            flash('An error occurred. Artist ' +
                  name + ' could not be updated.')
            print("Error with edit_artist_submission()")
            abort(500)

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # TODO (Done): replace with real venues data.
    data = [{
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.show_time)
    } for show in Show.query.all()]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # TODO(Done): insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    flashType = 'danger'
    if form.validate():
        try:
            newShow = Show.insert().values(
                Venue_id=request.form['venue_id'],
                Artist_id=request.form['artist_id'],
                start_time=request.form['start_time']
            )
            db.session.execute(newShow)
            db.session.commit()
            # on successful db insert, flash success
            flashType = 'success'
            flash('Show was successfully listed!')
        except:
            # TODO (Done): on unsuccessful db insert, flash an error instead.
            flash(
                'An error occurred. Show could not be listed.')
        finally:
            # Close session
            db.session.close()
    else:
        flash(form.errors)
        flash('An error occurred. Show could not be listed.')

    return render_template('pages/home.html', flashType=flashType)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
