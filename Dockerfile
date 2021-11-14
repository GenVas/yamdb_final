FROM python:3.7

LABEL maintainer="Gennady V. <_____@yandex.ru>"

WORKDIR /code

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install gunicorn gunicorn==20.0.4
RUN pip3 install -r /code/requirements.txt

COPY . .

CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000 
