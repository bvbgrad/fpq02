"""

"""
from sqlalchemy.sql import text

from app import db
import app.utils6L.utils6L as utils
import logging
import os

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

from app.models import Person


def get_all_persons():
    logger.info(__name__ + ".getAllPersons()")
    all_person_list = Person.query.all()
    return all_person_list


def get_all_persons_count():
    logger.info(__name__ + ".getAllPersons()")
    all_person_count = Person.query.count()
    return all_person_count


def get_person_gen_data(generation, count=False, before=False, after=False):
    logger.info(__name__ + ".get_person_gen_data()")
    filter_before = "Person.year_born < {}".format(generation)
    filter_after = "Person.year_born >= {}".format(generation)
    next_gen_filter = "Person.year_born < {}".format(generation + 25)

    if before:
        gen_filter = filter_before
    elif after:
        gen_filter = filter_after
    else:
        gen_filter = "{} and {}".format(filter_after, next_gen_filter)

# todo SAWarning: when Textual SQL expression declared as text -> query returns zero results
    logger.info(__name__ + ".get_person_gen_data(): filter: " + gen_filter)
    gen_filter = text(gen_filter)
    if count:
        generation_data = Person.query.filter(gen_filter).count()
    else:
        generation_data = Person.query.filter(gen_filter).all()

    return generation_data


def get_bad_answers(gender, year_born):
    logger.info(__name__ + ".get_bad_answers()")

    before_year_born = year_born - 10
    after_year_born = year_born + 10

    bad_answer_choices = Person.query. \
        filter(Person.gender == gender,
               Person.year_born >= before_year_born,
               Person.year_born < after_year_born).all()
    # print("bad_answer_choices: ", bad_answer_choices)
    return bad_answer_choices

def add_person(person):
    logger.info(f"Add person: {person}")
    #TODO prevent adding duplicate persons
    db.session.add(person)
    db.session.commit()

    person_filter = text(f"Person.surname='{person.surname}' AND Person.given_names='{person.given_names}'")
    person_list = Person.query.filter(person_filter).all()

    return person_list


def add_persons(person_data_list):
    #TODO prevent adding duplicate persons

    for line in person_data_list:
        item = line.split(',')
        person = Person(surname=item[1], given_names=item[2], gender=item[3], year_born=item[4])
        db.session.add(person)
    db.session.commit()