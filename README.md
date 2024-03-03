# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React based client.  This API/client can be used as a bootstrap to implement the specific features requested in the assessment description.

## Getting Started

<details>
  <summary>API Development and Client</summary>

### API Development
The API project is a [Django/DRF](https://www.django-rest-framework.org/) project that utilizes a [Makefile](https://www.gnu.org/software/make/manual/make.html) for a convenient interface to access development utilities. This application uses [SQLite](https://www.sqlite.org/index.html) as the default persistence database you are more than welcome to change this. This project requires Python 3.11 in order to create the virtual environment.  You will need to ensure that this version of Python is installed on your OS before building the virtual environment.  Running the below commmands should get the development environment running using the Django development server.
1. `$ make build` to create the virtual environment.
2. `$ make fixture` to create a small number of fixture file versions.
3. `$ make serve` to start the development server on port 8001.
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

To build the project
```bash
make build
```

To start server
```bash
make serve
```

### Using API

This project runs only the backend, and it is usable thanks to django rest framework gui.

#### Authentication
Go to <http://localhost:8001>
Click on "[login](http://localhost:8001/accounts/signup)"
Signup.
I deactivated email verification for testing purpose.
You will be redirected to your files.

#### Document manager

##### Uploading a file
Choose Django GUI or postman, as you prefer. This guide will follow Django GUI.
[Here](http://localhost:8001/home/) you can upload a file.
The version number will be setted automatically if there are already existing files with the same name and path.
Chose a file, an url, the owner, and the collaborators. The version file will be retrieved.

##### Retrieving files
[Here will be all your files](http://localhost:8001/home/all/)
[Here you'll add parameters to filter by "url" and "version_number"](http://localhost:8001/home/)
Both routes support get, post and delete.
I chose to split those routes to avoid getting all documents when you only want one, to not get heavy on the database

##### Download files
You can download files only if you're one collaborator or the owner.
The download will start automatically at <http://localhost:8001/home/download/file_id>