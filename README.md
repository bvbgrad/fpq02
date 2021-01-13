# Welcome to the Family Photo Quiz (FPQ) app code base!

Developer notes:
The database structure is based on the models.py module.
The database upgrade and downgrade is managed by invoking flask-aLembic.

Warning: Init will clear all the data.
    flask db init  # establish or reset the database migration mechnism
Use these commands for normal data structure evolution
    flask db migrate -m "comment"  # scan the models.py module for any logical database model changes
    flask db upgrade            # apply the logical database model changes to the pyhsical database
    flask db downgrade          # undo the last changes to the physical database model
