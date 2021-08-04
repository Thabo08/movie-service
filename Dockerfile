FROM python:3.9-alpine

RUN apk -U upgrade
RUN apk add busybox-extras
RUN adduser -D movies_adduser

WORKDIR /app

RUN echo 'System permissions ...'
RUN chown -R movies_adduser:movies_adduser ./
USER movies_adduser

RUN echo 'Copying application files ...'
COPY movies/ ./movies/
COPY requirements.txt requirements.txt

RUN echo 'Installing application dependencies ...'
RUN pip install -r requirements.txt

RUN echo 'Performing migrations ...'
RUN python ./movies/manage.py migrate

RUN echo 'Running tests ...'
RUN python ./movies/manage.py test movies_api

EXPOSE 8000

CMD ["python", "./movies/manage.py", "runserver", "0.0.0.0:8000"]