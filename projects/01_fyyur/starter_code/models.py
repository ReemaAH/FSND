
#----------------------------------------------------------------------------#
# Models section
#----------------------------------------------------------------------------#
from app import db
from sqlalchemy.orm import backref

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_a_talent = db.Column(db.Boolean, default=False)
    seeking_talent_text = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref=backref('venue', uselist=False))

    def __repr__(self):
        return f'<Venue ID: {self.id}, Venue name: {self.name}>'
# TODO: implement any missing fields, as a database migration using Flask-Migrate (done)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres  = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_a_venue =  db.Column(db.Boolean, default=False)
    seeking_venue_text = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='artist')

    def __repr__(self):
        return f'<Artist ID: {self.id}, Artist name: {self.name}>'

# TODO: implement any missing fields, as a database migration using Flask-Migrate (done)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration(done)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete='CASCADE'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'<Show ID: {self.id}>'


