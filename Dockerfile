FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=propylon_document_manager.site.settings.local

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/dev.txt /code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

RUN mv /code/src/propylon_document_manager /code/