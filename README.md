# Propylon Document Manager Assessment

The Propylon Document Management Technical Assessment is a simple (and incomplete) web application consisting of a basic API backend and a React based client.  This API/client can be used as a bootstrap to implement the specific features requested in the assessment description. 

## Getting Started
### API Development
The API project is a [Django/DRF](https://www.django-rest-framework.org/) project that utilizes a [Makefile](https://www.gnu.org/software/make/manual/make.html) for a convenient interface to access development utilities. This application uses [SQLite](https://www.sqlite.org/index.html) as the default persistence database you are more than welcome to change this. 

This project requires Python 3.13 in order to create the virtual environment.  You will need to ensure that this version of Python is installed on your OS before building the virtual environment.  
- [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
```sh
    curl -LsSf https://astral.sh/uv/install.sh | sh

```
Running the below commands should get the development environment running using the Django development server.
1. `$ make build` to create the virtual environment.
2. `$ make fixtures` to create a small number of fixture file versions.
3. `$ make serve` to start the development server on port 8001.
4. `$ make test` to run the limited test suite via PyTest.

### Backend API Testing (Copy/Paste Guide)
Use the steps below exactly as written.

#### 1) Open a terminal and go to the project root
```sh
cd /home/zainab/Desktop/document-manager-assessment/document-manager-assessment
```

#### 2) Install/sync dependencies
```sh
make build
```

#### 3) Apply migrations
```sh
uv run django-admin migrate
```

#### 4) Create two users and API tokens
Run this command and copy the two printed tokens:
```sh
uv run django-admin shell -c "from django.contrib.auth import get_user_model; from rest_framework.authtoken.models import Token; U=get_user_model(); u1,_=U.objects.get_or_create(email='owner@example.com', defaults={'name':'Owner'}); u1.set_password('ownerpass123'); u1.save(); t1,_=Token.objects.get_or_create(user=u1); u2,_=U.objects.get_or_create(email='other@example.com', defaults={'name':'Other'}); u2.set_password('otherpass123'); u2.save(); t2,_=Token.objects.get_or_create(user=u2); print('OWNER_TOKEN=' + t1.key); print('OTHER_TOKEN=' + t2.key)"
```

Export the tokens in your shell (replace values):
```sh
export OWNER_TOKEN="paste_owner_token_here"
export OTHER_TOKEN="paste_other_token_here"
```

#### 5) Start the server
Keep this terminal running:
```sh
make serve
```

#### 6) Open a second terminal and go to the project root
```sh
cd /home/zainab/Desktop/document-manager-assessment/document-manager-assessment
```

#### 7) Confirm unauthenticated requests are blocked
```sh
curl -i http://127.0.0.1:8001/api/file_versions/
curl -i http://127.0.0.1:8001/api/documents/reviews/review.pdf
```
Expected: `401` or `403`.

#### 8) Upload any file type to any URL as owner
```sh
curl -i -X POST http://127.0.0.1:8001/api/documents/reviews/review.pdf \
    -H "Authorization: Token $OWNER_TOKEN" \
    -F "file=@/home/zainab/Downloads/kittys.jpg"
```
Expected: `201` and JSON with fields including `url_path`, `version_number`, `content_hash`.

#### 9) Upload second version to the same URL
```sh
curl -i -X POST http://127.0.0.1:8001/api/documents/reviews/review.pdf \
    -H "Authorization: Token $OWNER_TOKEN" \
    -F "file=@/home/zainab/Downloads/kittys.jpg"
```
Expected: `201` and `version_number` should be `2`.

#### 10) List owner files
```sh
curl -s http://127.0.0.1:8001/api/file_versions/ \
    -H "Authorization: Token $OWNER_TOKEN"
```
Expected: JSON list with your records only.

#### 11) Fetch latest file bytes by URL
```sh
curl -i http://127.0.0.1:8001/api/documents/reviews/review.pdf \
    -H "Authorization: Token $OWNER_TOKEN" \
    -o /tmp/latest_review.bin
```

#### 12) Fetch specific revisions by URL
```sh
curl -i "http://127.0.0.1:8001/api/documents/reviews/review.pdf?revision=0" \
    -H "Authorization: Token $OWNER_TOKEN" \
    -o /tmp/review_rev0.bin

curl -i "http://127.0.0.1:8001/api/documents/reviews/review.pdf?revision=1" \
    -H "Authorization: Token $OWNER_TOKEN" \
    -o /tmp/review_rev1.bin
```

#### 13) Fetch metadata JSON
```sh
curl -s http://127.0.0.1:8001/api/documents/reviews/review.pdf/metadata \
    -H "Authorization: Token $OWNER_TOKEN"

curl -s "http://127.0.0.1:8001/api/documents/reviews/review.pdf/metadata?revision=0" \
    -H "Authorization: Token $OWNER_TOKEN"
```

#### 14) Fetch by CAS hash
First copy `content_hash` from metadata response above, then:
```sh
export CONTENT_HASH="paste_content_hash_here"

curl -i http://127.0.0.1:8001/api/cas/$CONTENT_HASH \
    -H "Authorization: Token $OWNER_TOKEN" \
    -o /tmp/cas_file.bin
```

#### 15) Verify other users cannot access owner files
```sh
curl -i http://127.0.0.1:8001/api/documents/reviews/review.pdf \
    -H "Authorization: Token $OTHER_TOKEN"

curl -i http://127.0.0.1:8001/api/documents/reviews/review.pdf/metadata \
    -H "Authorization: Token $OTHER_TOKEN"

curl -i http://127.0.0.1:8001/api/cas/$CONTENT_HASH \
    -H "Authorization: Token $OTHER_TOKEN"
```
Expected: `404` for these owner-only resources.

#### 16) Run unit tests
```sh
PYTHONPATH=src python3 -m pytest tests/test_file_versions.py -q
```
Expected: all tests pass.

### Client Development 
See the Readme [here](https://github.com/propylon/document-manager-assessment/blob/main/client/doc-manager/README.md)

##
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
