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
from .photoDAO import get_all_photos, get_all_photos_count, add_photos, delete_photos, update_photo

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

    num_quiz_photos = len(quiz_photos)

    while 'test' in answers:
    # random_photo_id identifies which photo is being quized
        random_photo_id = random.randint(0, num_quiz_photos - 1)
        if answers[random_photo_id] != 'test':
            logger.info(f"test candidate already tested: {random_photo_id} current answers {answers}")
            continue
        else:
            logger.info(f"untested candidate: {random_photo_id} current answers {answers}")

        logger.info("Photo {} selected".format(quiz_photos[random_photo_id]))
        photo_path = Path(quiz_photos[random_photo_id].filename)
        photo = (photo_path.name, quiz_photos[random_photo_id].comment)

        person_id = quiz_photos[random_photo_id].PersonIdFK
        photo_person = Person.query.filter(Person.id == person_id).first()

        logger.info("photo '{}' photo_person = {}".format(random_photo_id, photo_person))

        answer_list_choices = get_bad_answers(photo_person.gender, photo_person.year_born)
        # print("view().answer_list: ", answer_list_choices)
        correct_found = False
        shuffled_answer_list = []
        while not correct_found:
            shuffled_answer_list = random.sample(answer_list_choices, 5)
            for random_person in shuffled_answer_list:
                if random_person == photo_person:
                    correct_found = True

        answer_list = []
        for person in shuffled_answer_list:
            if person == photo_person:
                answer_list.append(('correct', person))
            else:
                answer_list.append(('wrong', person))

        logger.info(f"Answer list append: {answer_list}")

        return render_template(
            'templates_quiz/quiz.html',
            question_id=random_photo_id, photo=photo, answer_list=answer_list)

    return redirect(url_for('main.display_score'))


@bp.route('/scores', methods=['POST', 'GET'])
def display_score():
    global photo_list
    logger.info(__name__ + ".display_score()")
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
        photo_list.append((i, num_photos, path.name, photo.comment, photo_person, answers[i - 1]))

    print("Scores -- Photo List: ", photo_list)

    # person_id = quiz_photos[random_photo_id].PersonIdFK  # todo display right/wrong answerss
    # photo_person = Person.query.filter(Person.id == person_id).first()
    # for quiz_person in quiz_photos:

    return render_template('templates_quiz/display_score.html',
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


@bp.route('/mx_photos', methods=['post', 'get'])
@login_required
def mx_photo_admin():
    logger.info(__name__ + f".mx_photo_admin()")

    # get a list of all the photos from the database
    all_photos = Photo.query.all()  # todo shadow outer scope photos
    num_photos = len(all_photos)
    logger.info(__name__ + " {} available photos".format(num_photos))

    return render_template('templates_mx/mx_photo_admin.html', photos=all_photos)


@bp.route('/mx/tag_one_photo', methods=['post', 'get'])
@login_required
def tag_one_photo():
    try:
        photo_id = int(request.args.get("photo"))
    except (TypeError, ValueError):
        photo_id = 0
    logger.info(__name__ + f".tag_one_photo() Photo Id = {photo_id}")

    # get a list of all the photos from the database
    all_photos = Photo.query.all()  # todo shadow outer scope photos
    num_photos = len(all_photos)
    logger.info(" {} available photos".format(num_photos))

    selected_photo = None
    # Try to find the correct selected_photo based on the photo Id
    for i, photo in enumerate(all_photos):
        if photo_id == photo.id:
            selected_photo = all_photos[i]
            logger.info(f"Found photo {selected_photo} for photo id {photo_id} in photos")
    
    # if photo id does not exist, default to the first photo on the list
    if selected_photo is None:
        logger.warn(f"Could not find photo id {photo_id} in photos")
        selected_photo = all_photos[0]

    # get a list of all persons from the database ordered by surname, given names
    persons = Person.query.order_by(Person.surname, Person.given_names).all()
    logger.info(__name__ + " {} persons".format(len(persons)))

    return render_template('templates_mx/tag_photo.html',
                           photo=selected_photo, persons=persons)


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
    # TODO remove 'if i > 5: break' line after fixing photo tagging algorithm
        if i > 5: break
        if photo.PersonIdFK != 0:
            # person = persons[photo.PersonIdFK]
            person = Person.query.filter_by(id=photo.PersonIdFK).first()
            print("personIdFK = {}, person: {}".format(photo.PersonIdFK, person)) # todo logging?
            try:
                photo_person = "{}, {} ({}) ({})" \
                    .format(person.surname, person.given_names,
                            person.gender, person.year_born)
            except AttributeError:
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
    try:
        tagged_person_id = int(tagged_person)
    except ValueError as exception:
        logger.exception(f"{__name__}error = '{exception}'")
        tagged_person_id = 0

    tagged_photo = request.form.get('selected_photo')
    try:
        tagged_photo_id = int(tagged_photo)
    except ValueError as exception:
        logger.exception(f"{__name__} error = '{exception}'")
        tagged_photo_id = 0

    tagged_comment = request.form.get('comment')

    if tagged_person and tagged_photo:
        logger.info(
            __name__ + " tagged person = {}, tagged photo = {}, comment = {}"
            .format(tagged_person_id, tagged_photo, tagged_comment))
        photo = Photo.query.filter_by(id=tagged_photo_id).first()
        photo.PersonIdFK = tagged_person_id
        photo.comment = tagged_comment
        update_photo(photo)

        logger.info(
            __name__ + " photo #{} has been updated: {}".format(tagged_photo_id, photo))
        return redirect(url_for('main.mx_photo_admin'))
    return redirect(url_for('main.mx_photo_admin'))


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
    # TODO non-functional, needs to be updated
    
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


@utils.log_wrap
@bp.route('/sync_db_with_images', methods=['get'])
@login_required
def sync_db_with_images():
    logger.info("sync_db_with_images()")

    photo_list = get_all_photos()
    logger.info(f"There are {len(photo_list)} photos before the sync action")

    # TODO make image location an configuration or environment variable
    images_folder = 'app/static/images'
    images_path = Path(images_folder)
    photo_files = os.listdir(images_path)

    # identify the rows in the database that do not have a photo in the images folder
    flagged_for_action = []
    for i, photo in enumerate(photo_list, 1):
        print(f"{i:2d}.  {photo.id}:{photo.filename}")
        if photo.filename in photo_files:
            logger.info(f"photo found: {photo.filename}")
        else:
            flagged_for_action.append(photo)

    # delete the rows in the database that do not have a photo in the images folder
    delete_photos(flagged_for_action)

    # Create new photo list of the photos that were found
    # And whose information is still in the database
    photos_found = set()
    photo_list = get_all_photos()
    for photo in photo_list:
        photos_found.add(photo.filename)
    logger.info(f"There are {len(photos_found)} photos left in the database after the delete photos action")
    print(f"photos found set: {photos_found}")

    flagged_for_action = []
    for i, photo_file in enumerate(photo_files, 1):
        print(f"{i:2d}. {photo_file}")
        if photo_file not in photos_found:
            logger.info(f"add photo to database: {photo_file}")
            flagged_for_action.append((photo_file, images_folder,))

    print(f"add photos: {flagged_for_action}")

    # add the new photos to the database
    add_photos(flagged_for_action)

    photo_list = get_all_photos()
    logger.info(f"There are {len(photo_list)} photos after the sync action")

    return redirect(url_for('main.mx_actions'))
