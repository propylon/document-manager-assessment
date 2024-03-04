# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React based client.  This API/client can be used as a bootstrap to implement the specific features requested in the assessment description.

## Getting Started

<details>
  <summary>API Development and Client</summary>

### API Development
The API project is a [Django/DRF](https://www.django-rest-framework.org/) project that utilizes a [Makefile](https://www.gnu.org/software/make/manual/make.html) for a convenient interface to access development utilities. This application uses [SQLite](https://www.sqlite.org/index.html) as the default persistence database you are more than welcome to change this. This project requires Python 3.11 in order to create the virtual environment.  You will need to ensure that this version of Python is installed on your OS before building the virtual environment.  Running the below commmands should get the development environment running using the Django development server.
1. `$ make build` to create the virtual environment.
2. `$ make fixture` to create a small number of fixture file versions.
3. `$ make serve` to start the development server on port 8000.
4. `$ make test` to run the limited test suite via PyTest.
### Client Development
The client project is a [Create React App](https://create-react-app.dev/) that has been tested against [Node v18.19.0 Hydrogen LTS](https://nodejs.org/download/release/v18.19.0/).  An [.nvmrc](https://github.com/nvm-sh/nvm#calling-nvm-use-automatically-in-a-directory-with-a-nvmrc-file) file has been included so that the command `$ nvm use` should select the correct NodeJS version through NVM.
1. Navigate to the client/doc-manager directory.
2. `$ npm install` to install the dependencies.
3. `$ npm start` to start the React development server.

##
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
</details>

## How to test Eduardo's work


### Run API server

#### Building the Project
I containerized the project, to run it you need to install docker and docker-compose, you can find how on the [official website](https://docs.docker.com/compose/install/).

Then to start the project simply run
```bash
docker-compose up --build
```

There are two containers: one for django and one for postgres.
Env file:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=propylon
DB_USER=eduardo
DB_PASSWORD=A_great_one
DB_HOST=db
DB_PORT=5432
WEB_PORT=8000
```
## Using API

This project only serves the backend, accessible via Django Rest Framework GUI.

### Document Manager

##### Authentication
1. Go to [localhost:8000](http://localhost:8000)
2. Click on "[login](http://localhost:8000/accounts/signup)"
3. Sign up. Email verification is deactivated for testing.
4. You will be redirected to your files.

##### Uploading a File
You can upload a file via Django GUI or Postman. This guide follows the Django GUI:
1. [Click here](http://localhost:8000/home/) to upload a file.
2. The version number is automatically set if there are existing files with the same name and path.
3. Choose a file, a URL, the owner, and collaborators. The version file will be retrieved.

##### Retrieving Files
- [View all files](http://localhost:8000/home/all/)
- [Filter by "url" and "version_number"](http://localhost:8000/home/)

Both routes support GET, POST, and DELETE requests. They are split to avoid fetching all documents unnecessarily.

##### Download Files
You can download files if you're a collaborator or the owner. The download starts automatically at [localhost:8000/home/download/file_id](http://localhost:8000/home/download/file_id)

### Requirements
- [x] Stores files of any type and name
- [x] Stores files at any URL
- [x] Does not allow interaction by non-authenticated users
- [x] Does not allow a user to access files submitted by another user
- [x] Allows users to store multiple revisions of the same file at the same URL
- [x] Allows users to fetch any revision of any file
