FROM python:3.11.6

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

COPY . .
RUN pip install -r requirements.txt

CMD ["python", "./main.py"] 
