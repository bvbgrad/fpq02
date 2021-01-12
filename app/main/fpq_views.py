import random
from pathlib import Path
import json

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from app.main import bp

from app.models import Photo, Person
from .personDAO import get_all_persons_count, get_person_gen_data, get_bad_answers
from .personDAO import add_persons
from .photoDAO import get_all_tagged_photos, get_all_tagged_photos_count, get_photo_quiz_data
from .photoDAO import get_all_photos_count, add_photos

import app.utils6L.utils6L as utils
import logging
import os

logger_name = os.getenv("LOGGER_NAME")
logger = logging.getLogger(logger_name)

# from .photoDAO import get_photo_quiz_data


# from .forms import ContactForm, LoginForm
# from .utils import send_mail

photo_list = []
quiz_photos = []
num_questions = 5
answers = []


# todo change all print statements to log entries


# @bp.route('/', methods=['POST', 'GET'])
@bp.route('/prep', methods=['POST', 'GET'])
def quiz_prep():
    logger.info(__name__ + ".quiz_prep()")
    global num_questions

    if request.form:
        num_questions = int(request.form.get('num_questions'))
        chosen_generation = str(request.form.get('optradio'))
        logger.info(
            __name__ + ".quiz_prep() number of questions: '{}', chosen generation: '{}'"
            .format(num_questions, chosen_generation))

        # that have been tagged to a person # todo adjust for data from form

        if chosen_generation == 'None':
            chosen_generation = 'All'
        if chosen_generation == 'All':
            tagged_photo_list = get_all_tagged_photos()
        elif get_photo_quiz_data(chosen_generation, count=True) > 0:
            tagged_photo_list = get_photo_quiz_data(chosen_generation)
        else:
            flash("Error: No available quiz photos for generation '{}'".format(chosen_generation))
            return redirect(url_for('quiz_prep'))

        number_tagged_photos = len(tagged_photo_list)
        logger.info(__name__ + " {} tagged photos".format(number_tagged_photos))
        if number_tagged_photos > num_questions:
            number_tagged_photos = num_questions

        quiz_photos.clear()
        answers.clear()
        for photo in random.sample(tagged_photo_list, number_tagged_photos):
            quiz_photos.append(photo)
            answers.append('test')
        logger.info(__name__ + " {} quiz photos".format(len(quiz_photos)))
        # todo print(quiz_photos)
        return redirect(url_for('main.quiz'))

    persons = Person.query.all()
    logger.info(__name__ + " {} persons".format(len(persons)))
    # for i in range(5):
    #     logger.info(__name__ + " Person #{}: {}".format(i, persons[i]))

    # get list of all photos from the database
    photos = Photo.query.all()
    logger.info(__name__ + " {} photos".format(len(photos)))

    generations = ["All", 1800, 1825, 1850, 1875, 1900, 1925, 1950, 1975, 2000]
    number_per_generation = []
    number_tagged_photos = []

    for generation in generations:
        if generation == "All":
            all_count = get_all_persons_count()
            all_tagged_photos_count = get_all_tagged_photos_count()
            number_per_generation.append(all_count)
            number_tagged_photos.append(all_tagged_photos_count)
        else:
            data_count = get_person_gen_data(generation, count=True)
            quiz_count = get_photo_quiz_data(generation, count=True)
            number_per_generation.append(data_count)
            number_tagged_photos.append(quiz_count)
            if data_count < 15:
                logger.debug("generation: {} has {} names, data = {}"
                                 .format(generation, data_count, get_person_gen_data(generation)))

    logger.info(__name__ + " {} number per generation ".format(number_per_generation))
    logger.info(__name__ + " {} number tagged photos ".format(number_tagged_photos))

    mapped = zip(generations, number_per_generation, number_tagged_photos)
    zipped_gen = list(mapped)
    logger.info("zipped tuples: {}".format(zipped_gen))

    return render_template('templates_quiz/quiz_prep.html', num_questions=num_questions,
                           zipped_gen=zipped_gen)


@bp.route('/quiz', methods=['POST', 'GET'])
def quiz():
    logger.info(__name__ + ".quiz()")
    global num_questions

    if request.form:
        question_id = int(request.form.get('question_id'))
        answer = request.form.get('optradio')
        logger.info(
            __name__ + ".quiz() Question {} answer is '{}'"
            .format(question_id, answer))
        answers[question_id] = answer

        print("Quiz photo: {} answer was '{}'".format(quiz_photos[question_id], answer))
        print("Answers so far: {}".format(answers))

        person_id = quiz_photos[question_id].PersonIdFK
        photo_person = Person.query.filter(Person.id == person_id).first()
        photo_name = "'{}, {}'".format(photo_person.surname, photo_person.given_names)

        if answer == "correct":
            flash("Success: {} was the correct answer".format(photo_name))
        else:
            flash("Error: Your answer should have been {}".format(photo_name))

        return render_template(
            'templates_quiz/response.html',
            question_id=person_id, photo=photo_person, photo_name=photo_name, answer=answer)

    num_quiz_photos = len(quiz_photos)

    while 'test' in answers:
        random_photo_id = random.randint(0, num_quiz_photos - 1)
        if answers[random_photo_id] != 'test':
            print("test candidate already tested: ", random_photo_id, answers)
            continue
        else:
            print("untested candidate: ", random_photo_id, answers)

        print("Photo {} selected".format(quiz_photos[random_photo_id]))
        photo_path = Path(quiz_photos[random_photo_id].filename)
        photo = (photo_path.name, quiz_photos[random_photo_id].comment)

        person_id = quiz_photos[random_photo_id].PersonIdFK
        photo_person = Person.query.filter(Person.id == person_id).first()

        print("photo '{}' photo_person = {}".format(random_photo_id, photo_person))

        answer_list_choices = get_bad_answers(photo_person.gender, photo_person.year_born)
        # print("view().answer_list: ", answer_list_choices)
        correct_found = False
        shuffled_answer_list = []
        while not correct_found:
            print("view().shuffle answers")
            shuffled_answer_list = random.sample(answer_list_choices, 5)
            for random_person in shuffled_answer_list:
                if random_person == photo_person:
                    correct_found = True
        print("view().shuffled_answer_list: ", shuffled_answer_list)

        answer_list = []
        for person in shuffled_answer_list:
            if person == photo_person:
                answer_list.append(('correct', person))
            else:
                answer_list.append(('wrong', person))

        print("Answer list append: {}".format(answer_list))

        return render_template(
            'templates_quiz/quiz.html',
            question_id=random_photo_id, photo=photo, answer_list=answer_list)

    # return render_template('templates_quiz/scores.html')
    return redirect(url_for('main.display_scores'))


@bp.route('/scores', methods=['POST', 'GET'])
def display_scores():
    global photo_list
    logger.info(__name__ + ".display_scores()")
    correct_answers = 0
    wrong_answers = 0
    for answer in answers:
        if answer == 'correct':
            correct_answers += 1
        else:
            wrong_answers += 1
    total_answers = correct_answers + wrong_answers
    percent_correct = 0.0
    if total_answers > 0:
        percent_correct = correct_answers / total_answers * 100
        percent_correct = "%.1f" % percent_correct
    print("percent correct: ", percent_correct, correct_answers, wrong_answers, total_answers)
    print("Scores -- Quiz Photos: ", quiz_photos)

    num_photos = len(quiz_photos)
    logger.info(__name__ + " {} photos".format(num_photos))
    # for i in range(5):
    #     logger.info(__name__ + " Photo #{}: {}".format(i, photos[i]))
    #
    photo_list = []
    i = 0
    for photo in quiz_photos:
        if photo.PersonIdFK != 0:
            # person = persons[photo.PersonIdFK]
            person = Person.query.filter_by(id=photo.PersonIdFK).first()
            # todo print("personIdFK = {}, person: {}".format(photo.PersonIdFK, person))
            photo_person = "{}, {} ({}) ({})" \
                .format(person.surname, person.given_names,
                        person.gender, person.year_born)
        else:
            photo_person = None
        path = Path(photo.filename)
        i += 1
        photo_list.append((i, num_photos, path.name, photo.comment, photo_person))

    print("Scores -- Photo List: ", photo_list)

    # person_id = quiz_photos[random_photo_id].PersonIdFK  # todo display right/wrong answerss
    # photo_person = Person.query.filter(Person.id == person_id).first()
    # for quiz_person in quiz_photos:

    return render_template('templates_quiz/scores.html',
                           percent_correct=percent_correct,
                           wrong_answers=wrong_answers,
                           correct_answers=correct_answers,
                           photo_list=photo_list)


@bp.route('/gallery', methods=['GET'])
@bp.route('/gallery/<gallery_type>', methods=['GET'])
def gallery(gallery_type='all'):
    global photo_list

    logger.info(__name__ + ".gallery() {} photos".format(type))

    if gallery_type == 'tagged':
        photos = get_all_tagged_photos()
    else:
        photos = Photo.query.all()

    num_photos = len(photos)
    logger.info(__name__ + " {} photos".format(num_photos))
    # for i in range(5):
    #     logger.info(__name__ + " Photo #{}: {}".format(i, photos[i]))
    #
    photo_list = []
    i = 0
    for photo in photos:
        if photo.PersonIdFK != 0:
            # person = persons[photo.PersonIdFK]
            person = Person.query.filter_by(id=photo.PersonIdFK).first()
            # todo print("personIdFK = {}, person: {}".format(photo.PersonIdFK, person))
            photo_person = "{}, {} ({}) ({})" \
                .format(person.surname, person.given_names,
                        person.gender, person.year_born)
        else:
            photo_person = None
        path = Path(photo.filename)
        i += 1
        photo_list.append((i, num_photos, path.name, photo.comment, photo_person))

    return render_template('templates_quiz/gallery.html', photo_list=photo_list)


@bp.route('/about')
@bp.route('/about/<name>')
def about(name=None):
    logger.info(__name__ + ".about()")
    # users = User.query.all()  # todo No user table available
    # logger.info(".about(): {} users: {}".format(len(users), users.__str__()))
    # return render_template('templates_quiz/about.html', name=name, users=users)
    return render_template('templates_quiz/about.html', name=name)


@bp.route('/mx', methods=['post', 'get'])
@login_required
def mx_actions():
    return render_template('templates_mx/mx_actions.html')


@bp.route('/mx/<photo_number>', methods=['post', 'get'])
@login_required
def tag_photos(photo_number=0):
    global photo_list

    logger.info(__name__ + ".tag_photos() Photo number = {}".format(photo_number))

    # get a list of all persons from the database ordered by surname, given names
    persons = Person.query.order_by(Person.surname, Person.given_names).all()
    logger.info(__name__ + " {} persons".format(len(persons)))
    for i in range(5):
        logger.debug(__name__ + " Person #{}: {}".format(i, persons[i]))

    # get a list of all the photos from the database
    photos = Photo.query.all()  # todo shadow outer scope photos
    num_photos = len(photos)
    logger.info(__name__ + " {} available photos".format(num_photos))
    for i in range(5):
        logger.debug(__name__ + " Photo #{}: {}".format(i, photos[i]))

    photo_list = []
    i = 0
    for i, photo in enumerate(photos):
        if i > 5: break
        if photo.PersonIdFK != 0:
            # person = persons[photo.PersonIdFK]
            person = Person.query.filter_by(id=photo.PersonIdFK).first()
            print("personIdFK = {}, person: {}".format(photo.PersonIdFK, person)) # todo logging?
            try:
                photo_person = "{}, {} ({}) ({})" \
                    .format(person.surname, person.given_names,
                            person.gender, person.year_born)
            except AttributeError as e:
                logger.exception(f"problem with person object for photo id = {photo.id}")
        else:
            photo_person = None
        path = Path(photo.filename)
        i += 1
        photo_list.append(
            (i, num_photos, path.name, photo.comment, photo_person, photo.PersonIdFK))

    logger.info(__name__ + " {} tagged photos".format(len(photo_list)))
    return render_template('templates_mx/tag_photos.html',
                           photo_list=photo_list, persons=persons,
                           photo_number=photo_number)


@bp.route('/mx/update', methods=['post', 'get'])
@login_required
def update_photo_tag():
    logger.info(__name__ + ".update_photo_tag()")

    tagged_person = request.form.get('selected_person')
    tagged_person_id = int(tagged_person)
    tagged_photo = request.form.get('selected_photo')
    tagged_photo_id = int(tagged_photo)
    tagged_comment = request.form.get('comment')

    if tagged_person and tagged_photo:
        logger.info(
            __name__ + " tagged person = {}, tagged photo = {}, comment = {}"
            .format(tagged_person_id, tagged_photo, tagged_comment))
        photos = Photo.query.all()  # todo shadow outer scope photos
        photo = Photo.query.filter_by(id=photos[tagged_photo_id - 1].id).first()  # todo index offset fudge?
        photo.PersonIdFK = tagged_person_id
        photo.comment = tagged_comment

        logger.info(
            __name__ + " photo #{} has been updated: {}".format(tagged_photo_id, photo))
        return redirect("/mx")
        # return redirect("/mx/" + str(tagged_photo_id))
    return redirect("/mx")


def check_logger():
    logger.info(__name__ + ".check_logger()")
    logger.debug("this is a DEBUG message")
    logger.info("this is an INFO message")
    logger.warning("this is a WARNING message")
    logger.error("this is an ERROR message")
    logger.critical("this is a CRITICAL message")
    return "See console or log file for log messages"


@utils.log_wrap
@bp.route('/load_persons_json', methods=['get'])
@login_required
def load_persons_json():
    logger.info("load load_persons_json data")

    person_data = {}
    person_file_path = Path("data/rpi 20180615t0630 person.json")
    logger.info(f"Loading person data from '{person_file_path.name}'")
    try:
        with open(person_file_path, "r") as json_file:
            person_data = json.load(json_file)
            person_list = list(person_data[0]["rows"])
    except Exception as e:
        logger.exception(f"error: {e}")

    logger.info(f"Found {len(person_list)} persons in '{person_file_path.name}'")
    logger.info(f"There are {get_all_persons_count()} persons before the add action")

    for id, surname, given_names, gender, year_born in person_list:
        person = Person(surname=surname, given_names=given_names, gender=gender, year_born=year_born)
        add_person(person)

    logger.info(f"There are {get_all_persons_count()} persons before the add action")
    return redirect(url_for('main.mx_actions'))


@utils.log_wrap
@bp.route('/load_persons_csv', methods=['get'])
@login_required
def load_persons_csv():
    logger.info("load persons_csv data")

    person_file_path = Path("data/rpi 20180615t0630 person.csv")
    logger.info(f"Loading person data from '{person_file_path.name}'")

    person_list = []
    try:
        with open(person_file_path, "r") as csv_file:
            person_line = csv_file.readlines()
            for line in person_line:
                person_list.append(line.strip())
    except Exception as e:
        logger.exception(f"error: {e}")

    logger.info(f"There are {get_all_persons_count()} persons before the add action")
    logger.info(f"Found {len(person_list)} persons in '{person_file_path.name}'")
    if person_list[0] == "id,surname,given_names,gender,year_born":
        person_list.pop(0)
        add_persons(person_list)
    logger.info(f"There are {get_all_persons_count()} persons after the add action")

    return redirect(url_for('main.mx_actions'))

@utils.log_wrap
@bp.route('/load_photos_csv', methods=['get'])
@login_required
def load_photos_csv():
    logger.info("load photos_csv data")

    photo_file_path = Path("data/photo20210112x0345.csv")
    logger.info(f"Loading photo data from '{photo_file_path.name}'")

    photo_list = []
    try:
        with open(photo_file_path, "r") as csv_file:
            person_line = csv_file.readlines()
            for line in person_line:
                photo_list.append(line.strip())
    except Exception as e:
        logger.exception(f"error: {e}")

    logger.info(f"There are {get_all_photos_count()} photos before the add action")
    logger.info(f"Found {len(photo_list) - 1} photos in '{photo_file_path.name}'")
    if photo_list[0] == "id,filename,comment,PersonIdFK,folder":
        photo_list.pop(0)
        add_photos(photo_list)
    logger.info(f"There are {get_all_photos_count()} photos after the add action")

    return redirect(url_for('main.mx_actions'))
