FROM python:3.10
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
RUN python manage.py collectstatic
EXPOSE 8000
#VOLUME /code
STOPSIGNAL SIGTERM
CMD ["/code/run.sh"]
