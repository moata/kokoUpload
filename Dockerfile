FROM ubuntu:latest
MAINTAINER MoatasemAbdalmahdi
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
#ENV APPLICATION_SETTINGS ./config.cfgm$
ENTRYPOINT ["python"]
CMD ["main.py","runserver"]