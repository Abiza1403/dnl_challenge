FROM python:3.10.0

COPY . /restapi

WORKDIR /restapi

RUN pip3 install -r requirements.txt

CMD [ "python3", "-u", "./api/main.py"]