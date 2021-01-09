# Welcome to the Family Photo Quiz (FPQ) app code base!

Developer notes:
The database structure is based on the models.py module.
THe database upgrade and downgrade is managed by invoking flask-aLembic.
    flask db init  # establish or reset the database migration mechnism
    flask db migrate "comment"  # scan the models.py module for any changes
    flask db upgrade  # apply the changes to the database model
