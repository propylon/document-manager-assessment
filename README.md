# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React based client.  This API/client can be used as a bootstrap to implement the specific features requested in the assessment description. 

## Getting Started
### API Development
The API project is a [Django/DRF](https://www.django-rest-framework.org/) project that utilizes a [Makefile](https://www.gnu.org/software/make/manual/make.html) for a convenient interface to access development utilities. This application uses [SQLite](https://www.sqlite.org/index.html) as the default persistence database you are more than welcome to change this. This project requires Python 3.11 in order to create the virtual environment.  You will need to ensure that this version of Python is installed on your OS before building the virtual environment.  Running the below commmands should get the development environment running using the Django development server.
1. `$ make build` to create the virtual environment.
2. `$ make fixtures` to create a small number of fixture file versions.
3. `$ make serve` to start the development server on port 8001.
4. `$ make test` to run the limited test suite via PyTest.
### Client Development 
The client project is a [Create React App](https://create-react-app.dev/) that has been tested against [Node v18.19.0 Hydrogen LTS](https://nodejs.org/download/release/v18.19.0/).  An [.nvmrc](https://github.com/nvm-sh/nvm#calling-nvm-use-automatically-in-a-directory-with-a-nvmrc-file) file has been included so that the command `$ nvm use` should select the correct NodeJS version through NVM.
1. Navigate to the client/doc-manager directory.
2. `$ npm install` to install the dependencies.
3. `$ npm start` to start the React development server.


## Setup with HTTPS (IMPORTANT):
Use mkcert 

https://github.com/FiloSottile/mkcert

follow instruction and generate local certificates
and place them in the root of the project as `localhost.pem` and `localhost-key.pem`.
use django_extension to run the server with ssl

`runserver_plus --cert-file 127.0.0.1+1.pem localhost:9092`

**Note**: As react app uses http cookie for authentication it is require to have sercure backend server

# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React-based client. This document outlines the available APIs, their authentication methods, and the frontend URL.

## Application Overview
Current Application stores files at local followed by storage/user_{user_id}/{file_name} and uses a simple versioning system.
This functionality can be extended to support cloud storage solutions such as Amazon S3 or Google Cloud Storage (GCP Bucket).
The application allows users to upload, download, and manage documents with version control.

## Frontend URL
The React frontend is accessible at:
- **URL**: [http://localhost:3000](http://localhost:3000)
- Frontend is built using React and Material-UI.
- Backeend API url is configurable in the frontend codebase. it can be find in `client/doc-manager/src/config.js` file.

## API Overview
The backend API is built using Django and Django REST Framework (DRF). Below is a list of available APIs and their authentication methods.

## Authentication Method
The API uses **JWT (JSON Web Token)** for authentication. To access protected endpoints:

### Authentication APIs
1. **Obtain Token**
   - **Endpoint**: `/api/token/`
   - **Method**: `POST`
   - **Description**: Obtain an access and refresh token using email and password.
   - **Authentication**: None (public endpoint).
   - **Request Body**:
     ```json
     {
       "email": "user@example.com",
       "password": "your_password"
     }
     ```
   - **Response**:
     ```json
        {
        "user": "admin@example.com",
        "responseCode": 200,
        "responseMessage": "Success"
        }
     ```
     
        ```commandline
         Refresh and Access token are stored in http cookie for secuirty purpose
        ```

2. **Refresh Token**
   - **Endpoint**: `/api/refresh-token/`
   - **Method**: `POST`
   - **Description**: Refresh the access token using a valid refresh token.
   - **Authentication**: None (public endpoint).
   - **Request Body**:
     ```json
      {}
     ```
   - **Response**:
     ```json
     {
      "responseCode": 200,
      "responseMessage": "Success"
     }
     ```


### Document Management APIs
1. **List Documents**
   - **Endpoint**: `/api/document/`
   - **Method**: `GET`
   - **Description**: Retrieve a list of all documents.
   - **Authentication**: Access Token (cookie based access token required).

2. **Upload Document**
   - **Endpoint**: `/api/documents/`
   - **Method**: `POST`
   - **Description**: Upload a new document with form-data.
   - **Authentication**: Access Token (cookie based access token required).
   - **Request Body**: Multipart form data with the file.

3. **Retrieve Document**
   - **Endpoint**: `/api/document?id=<id>`
   - **Method**: `GET`
   - **Description**: Retrieve details of a specific document by ID.
   - **Authentication**: Access Token (cookie based access token required).
   - **Response**:
   - ```json
      [
        {
            "id": 35,
            "content": "https://127.0.0.1:9092/media/storage/user_1/review_v0_MEjooWb.pdf",
            "file_name": "review.pdf",
            "full_path": "storage/storage/user_1/review_v0_MEjooWb.pdf",
            "version_number": 0,
            "hash": "3df79d34abbca99308e79cb94461c1893582604d68329a41fd4bec1885e6adb4",
            "created_at": "2025-04-26T14:55:21.937813Z",
            "document": 20,
            "owner": 1
        }
      ]
     ```

4. **Download Document**
   - **Endpoint**: `/api/document/<file_name>?revision=<revision_id>`
   - **Method**: `GET`
   - **Description**: Download a specific document by file_name and revision id. if revision id is not provided latest version will be downloaded.
   - **Authentication**: Access Token (cookie based access token required).

5. **Unique Document**
   - **Endpoint**: `/api/file`
   - **Method**: `GET`
   - **Description**: Get list of unique document.
   - **Authentication**: Access Token (cookie based access token required).
   - **Response**:
   - ```json
      {
        "responseCode": 200,
        "responseMessage": "Success",
        "data": [
        {
            "id": 23,
            "fileName": "readme.txt",
            "latestVersionNumber": 0,
            "fileVersionCount": 1
        },
        {
            "id": 20,
            "fileName": "review.pdf",
            "latestVersionNumber": 2,
            "fileVersionCount": 3
        }
      ]
     }
     ```


## Notes
- Ensure the backend is running on `http://localhost:8001` and the frontend on `http://localhost:3000`.
- Use HTTPS for secure communication in production environments.
```

##
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
