# set base image (host OS)
FROM python:3.8-alpine

# set the working directory in the container
WORKDIR /fpq

# copy the dependencies file to the working directory
COPY docs/requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY config.py .
COPY family-photo-quiz.py .
COPY .env .

WORKDIR /fpq/app
COPY  app .
WORKDIR /fpq

# command to run on container start
CMD [ "python", "./family-photo-quiz.py" ]
