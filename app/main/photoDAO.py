"""
Database functions for photo data (including quiz candidates)
"""
from sqlalchemy.sql import text

from app import db
import app.utils6L.utils6L as utils
import logging
import os

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

from app.models import Person, Photo

def get_all_photos():
    logger.info(__name__ + ".get_all_photos()")
    all_photo_list = Photo.query.all()
    return all_photo_list


def get_all_tagged_photos():
    logger.info(__name__ + ".get_all_tagged_photos()")
    all_tagged_photo_list = Photo.query.filter(Photo.PersonIdFK > 0).all()
    return all_tagged_photo_list


def get_all_photos_count():
    logger.info(__name__ + ".getAllPhotos() count")
    all_photo_count = Photo.query.count()
    return all_photo_count
    

def get_all_tagged_photos_count():
    logger.info(__name__ + ".get_all_tagged_photos_count()")
    all_tagged_photo_count = Photo.query.filter(Photo.PersonIdFK > 0).count()
    return all_tagged_photo_count


def get_photo_quiz_data(generation, count=False, before=False, after=False):
    logger.info(__name__ + ".get_photo_quiz_data()")

    gen_filter = create_photo_filter(after, before, generation)

    if count:
        logger.info(__name__ + ".get_photo_gen_data().count: filter: " + gen_filter)
        gen_filter = text(gen_filter)
        generation_data = Photo.query.join(Person).filter(gen_filter).count()
    else:
        logger.info(__name__ + ".get_photo_gen_data(): filter: " + gen_filter)
        gen_filter = text(gen_filter)
        generation_data = Photo.query.join(Person).filter(gen_filter).all()

    return generation_data


def get_photo_data(generation, count=False, before=False, after=False):
    logger.info(__name__ + ".get_photo_quiz_data()")

    gen_filter = create_photo_filter(after, before, generation)

    if count:
        generation_data = Photo.query.filter(gen_filter).count()
    else:
        generation_data = Photo.query.filter(gen_filter).all()

    return generation_data


def create_photo_filter(after, before, generation):
    logger.info(__name__ + ".create_photo_filter()")
    filter_before = "Person.year_born < {}".format(generation)
    filter_after = "Person.year_born >= {}".format(generation)
    next_gen_filter = "Person.year_born < {}".format(int(generation) + 25)
    if before:
        gen_filter = filter_before
    elif after:
        gen_filter = filter_after
    else:
        gen_filter = "{} and {}".format(filter_after, next_gen_filter)
# todo SAWarning: when Textual SQL expression declared as text -> query returns zero results
    return gen_filter


def add_photos(photo_data_list):
    logger.info(__name__ + ".add_photos()")
#TODO prevent adding duplicate photos

    for photo_info in photo_data_list:
        filename, folder = photo_info
        photo = Photo(filename=filename, folder=folder)
        db.session.add(photo)
    db.session.commit()


# To update an object simply set its attribute to a new value, 
# add the object to the session,
# and commit the changes.
def update_photo(photo):
    logger.info(__name__ + f".update_photo({photo})")
    db.session.add(photo)
    db.session.commit()


def delete_photos(photo_data_list):
    logger.info(__name__ + ".delete_photos()")
    photo_list = get_all_photos()
    for delete_photo in photo_data_list:
    # processing the entire list for each photo catches any duplicate entries
        for photo in photo_list:
    # delete a specific photo database entry based on filename and folder location
            if photo.filename == delete_photo.filename and photo.folder == delete_photo.folder:
                    logger.info("Deleting photo = {photo}")
                    db.session.delete(photo)
    db.session.commit()
