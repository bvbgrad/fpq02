"""

"""

from web import app
from .models import Person


def get_all_persons():
    app.logger.info(__name__ + ".getAllPersons()")
    all_person_list = Person.query.all()
    return all_person_list


def get_all_persons_count():
    app.logger.info(__name__ + ".getAllPersons()")
    all_person_count = Person.query.count()
    return all_person_count


def get_person_gen_data(generation, count=False, before=False, after=False):
    app.logger.info(__name__ + ".get_person_gen_data()")
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
        app.logger.info(__name__ + ".get_person_gen_data(): filter: " + gen_filter)
    if count:
        generation_data = Person.query.filter(gen_filter).count()
    else:
        generation_data = Person.query.filter(gen_filter).all()

    return generation_data


def get_bad_answers(gender, year_born):
    app.logger.info(__name__ + ".get_bad_answers()")

    before_year_born = year_born - 10
    after_year_born = year_born + 10

    bad_answer_choices = Person.query. \
        filter(Person.gender == gender,
               Person.year_born >= before_year_born,
               Person.year_born < after_year_born).all()
    # print("bad_answer_choices: ", bad_answer_choices)
    return bad_answer_choices
