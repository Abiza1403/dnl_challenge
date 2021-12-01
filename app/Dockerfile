FROM python:3.10.0

COPY . /scraper

WORKDIR /scraper

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED 1

CMD [ "python3", "-u", "./app/scraper.py"]