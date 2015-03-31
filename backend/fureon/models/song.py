import os
import datetime
import logging
import imghdr
import errno
import random

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from fureon import config
from fureon.utils.song_metadata_extractor import SongMetadataExtractor
from fureon.models.base import Base


module_logger = logging.getLogger(__name__)

class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    artist = Column('artist', String)
    album = Column('album', String, nullable=True)
    trackno = Column('trackno', String, nullable=True)
    date = Column('date', String, nullable=True)
    genre = Column('genre', String, nullable=True)
    duration = Column('duration', String)
    file_path = Column('file_path', String)
    art_path = Column('art_path', String, nullable=True)
    datetime_added = Column('datetime_added', DateTime)
    tags = Column('tags', String, nullable=True)
    play_count = Column('play_count', Integer, default=0)
    fave_count = Column('fave_count', Integer, default=0)

def add_song_from_path(session, song_path):
    extractor = SongMetadataExtractor()
    metadata = extractor.extract_metadata_from_song(song_path)
    picture_data = metadata.pop('picture_data')
    new_song = Song(**metadata)
    session.add(new_song)
    session.flush()
    art_path = None
    if picture_data:
        picture_extension = get_picture_extension_from_picture_data(picture_data)
        art_path = get_default_art_path(str(new_song.id), picture_extension)
        save_album_art_to_file(picture_data, art_path)
    new_song.datetime_added = datetime.datetime.now()
    new_song.file_path = unicode(song_path)
    new_song.art_path = unicode(art_path)
    return new_song.id

def save_album_art_to_file(picture_data, art_path):
    art_directory = os.path.dirname(art_path)
    try:
        os.makedirs(art_directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(art_path, 'wb') as image_out:
        image_out.write(picture_data)

def get_song_count(session):
    return session.query(Song.id).count()

def get_random_song(session):
    song_count = get_song_count(session)
    random_row_number = random.randint(0, song_count-1)
    return session.query(Song).slice(random_row_number,random_row_number+1).one()

def get_picture_extension_from_picture_data(picture_data):
    picture_format = imghdr.what(None, picture_data)
    extension = None
    if picture_format == 'jpeg':
        extension = 'jpg'
    elif picture_format == 'png':
        extension = 'png'
    return extension

def get_default_art_path(file_name, picture_format):
    static_folder_path = config.paths['static_folder_path']
    if not static_folder_path:
        return ''
    art_file_name = '{0}.{1}'.format(file_name, picture_format)
    art_path = os.path.join(static_folder_path, 'album-art', art_file_name)
    return art_path

def does_song_exist(session, song_path):
    if session.query(Song).filter(file_path=song_path).count():
        return True
    else:
        return False

def check_for_duplicate_song_entry(session, song_path):
    if not does_song_exist():
        error_message = 'The song located at {0} is already in the database'
        raise DuplicateEntryError(
            message=error_message.format(song_path),
            logger=module_logger,
            level='info'
        )


