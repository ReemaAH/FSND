#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database (done)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://reema@localhost:5432/fyyur'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  ## this if condition was added to remove the error in datetime 
  # i found in this link: https://stackoverflow.com/questions/63269150/typeerror-parser-must-be-a-string-or-character-stream-not-datetime
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data (done)
  # num_shows should be aggregated based on number of upcoming shows per venue.
  # here u returned a a query with two columns 
  states_and_cities = db.session.query(Venue.city, Venue.state)
  ## here i used a trick which is using set() in python to have distinct values and convert it back to list 
  ## i used this link as ref: https://stackoverflow.com/questions/12897374/get-unique-values-from-a-list-in-python
  states_and_cities = list(set(states_and_cities))
  data = []

  for element in states_and_cities:
    # here i went throgh each element in states_and_cities list to have 
    # to use it as fliter for Venue.id, Venue.name columns 
      venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == element[0],Venue.state == element[1])
      data.append({
        "state": element[1],
        "city": element[0],
        "venues": venues
      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (done)
  search_term = request.form.get('search_term', '')
  # here i used this link: https://stackoverflow.com/questions/16573095/case-insensitive-flask-sqlalchemy-query
  # to find how to search for similar words 
  results = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response={
    "count": results.count(),
    "data": results
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id (done)
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  # past shows
  past_shows = Show.query.filter(Show.venue_id==venue_id, (Show.start_at < datetime.now()))
  # upcomping shows
  upcomping_shows = Show.query.filter(Show.venue_id==venue_id, (Show.start_at > datetime.now()))
  # to avoind null values i checked here if there is a venue.seeking_talent_text value or not
  if venue.seeking_talent_text:
    data ={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_a_talent,
      "seeking_description": venue.seeking_talent_text,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcomping_shows,
      "past_shows_count": past_shows.count(),
      "upcoming_shows_count": upcomping_shows.count(),
    }
  else:
    data ={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": False,
      "seeking_description": '',
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcomping_shows,
      "past_shows_count": past_shows.count(),
      "upcoming_shows_count": upcomping_shows.count(),
    }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead (done)
  # TODO: modify data to be the data object returned from db insertion (done)
  try:
    # here i checked first if  seeking_a_talent checked or not and i assign to it boolean values
    if request.form.get('seeking_a_talent'):
      seeking_a_talent = True
    else:
      seeking_a_talent = False
    # here i created the new object
    new_venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'],
                      address=request.form['address'], phone=request.form['phone'], genres=request.form['genres'], 
                      facebook_link=request.form['facebook_link'], website_link=request.form['website_link'],
                      image_link=request.form['image_link'], seeking_a_talent=seeking_a_talent,
                      seeking_talent_text=request.form.get('seeking_talent_text', ''))
    ## add and commit to DB
    db.session.add(new_venue)
    db.session.commit()
    flash('Artist ' + new_venue.name + ' was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead. (done)
    # rollback in case of any error
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be added.')
  finally:
   db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using (done)
  try:
    ## sime end point which takes the venue id and deleted it 
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()
  return redirect(url_for('venues'))
  return None



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database(done)
  # return all artists in the DB
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.(done)
  #here i used this link: https://stackoverflow.com/questions/16573095/case-insensitive-flask-sqlalchemy-query
  # to find how to search for similar words 
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={
    "count": results.count(),
    "data": results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # TODO: replace with real venue data from the venues table, using venue_id(done)
  # here i retrived the artists data with the given id
  artist =  Artist.query.get(artist_id)

  # past shows with filter by artist_id and show time <= datetime.now()
  past_shows = Show.query.filter(Show.artist_id==artist_id, (Show.start_at <= datetime.now()))

  # upcomping shows with filter by artist_id and show time > datetime.now()
  upcomping_shows = Show.query.filter(Show.artist_id==artist_id, (Show.start_at > datetime.now()))

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_a_venue,
    "seeking_description": artist.seeking_venue_text,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcomping_shows,
    "past_shows_count": past_shows.count(),
    "upcoming_shows_count":  upcomping_shows.count(),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # here i filled the form fields with the data form the given artist ID 
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link,
  form.seeking_a_venue.data = artist.seeking_a_venue,
  form.seeking_venue_text.data = artist.seeking_venue_text,
  form.image_link.data = artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id> (done)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing (done)
  try:
    # here i retrived the request data to update the artist object
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    # here i checked if seeking_a_venue checkbock checked to fill it with boolean values
    if request.form.get('seeking_a_venue'):
      artist.seeking_a_venue = True
    else:
      artist.seeking_a_venue = False
    artist.seeking_venue_text = request.form.get('seeking_venue_text', '')
    flash('Artist ' + artist.name + ' was successfully updated!')
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # here i filled the form fields with the data form the given venue ID 
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link,
  form.seeking_a_talent.data = venue.seeking_a_talent,
  form.seeking_a_talent_text.data = venue.seeking_talent_text,
  form.image_link.data = venue.image_link
  # TODO: populate form with values from venue with ID <venue_id> (done)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing (done)
  try:
    # here i retrived the request data to update the venue object
    venue = Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.address = request.form['address']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    if request.form.get('seeking_a_talent'):
      venue.seeking_a_talent = True
    else:
      venue.seeking_a_talent = False
    venue.seeking_talent_text = request.form.get('seeking_a_talent_text', '')
    flash('Venue ' + venue.name + ' was successfully updated!')
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. venue ' + request.form['name'] + ' could not be updated!')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Venue record in the db, instead(done)
  # TODO: modify data to be the data object returned from db insertion(done)
  try:
    # checking seeking_a_venue value
    if request.form.get('seeking_a_venue'):
      seeking_a_venue = True
    else:
      seeking_a_venue = False
    # create a new object fot artist 
    new_artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'],
                        phone=request.form['phone'], genres=request.form['genres'], image_link=request.form['image_link'],
                        facebook_link=request.form['facebook_link'], website_link=request.form['website_link'],
                        seeking_a_venue=seeking_a_venue,
                        seeking_venue_text=request.form.get('seeking_venue_text', ''))
    # add object to session and commit
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + new_artist.name + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead. (done)
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be added.')
  finally:
   db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # TODO: replace with real venues data. (done)
  data = Show.query.order_by(Show.start_at).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # TODO: insert form data as a new Show record in the db, instead (done)
  try:
    # create a new show object
    new_show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], start_at=request.form['start_time'])
    # add and commit to db session
    db.session.add(new_show)
    db.session.commit()
    flash('Show of artist_id' + request.form['artist_id']  + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.(done)
  except:
    db.session.rollback()
    flash('An error occurred. Show of artist_id' + request.form['artist_id'] + ' could not be added.')
  finally:
   db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
