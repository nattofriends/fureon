import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from fureon import config
from fureon.utils.song_metadata_extractor import SongMetadataExtractor
from fureon.models.base import Base


class SongModel(Base):
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
    art_path = Column('art_path', String)
    datetime_added = Column('datetime_added', DateTime)
    tags = Column('tags', String, nullable=True)
    play_count = Column('play_count', Integer, default=0)
    fave_count = Column('fave_count', Integer, default=0)

def add_new_song(session, song_path, art_path=''):
    extractor = SongMetadataExtractor()
    metadata = extractor.extract_metadata_from_song(song_path)
    picture_data = metadata.pop('picture_data')
    new_song = SongModel(**metadata)
    session.add(new_song)
    session.flush()
    if picture_data:
        if not art_path:
            art_path = get_default_art_path(str(new_song.id), picture_format)
        save_album_art_to_file(picture_data, art_path)
        new_song.artpath = art_path
    new_song.datetime_added = datetime.datetime.now()
    new_song.file_path = unicode(song_path)
    new_song.art_path = unicode(art_path)
    return new_song.id

def save_album_art_to_file(picture_data, art_path):
    if not art_path:
        return ''
    with open(art_path, 'wb') as image_out:
        image_out.write(picture_data)

def get_default_art_path(file_name, picture_format):
    static_folder_path = config.paths['static_folder_path']
    if not static_folder_path:
        return ''
    art_file_name = '{0}.{1}'.format(file_name, picture_format)
    art_path = os.path.join(static_files_path, 'album-art', art_file_name)
    return art_path
