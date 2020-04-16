FROM python:3.7-alpine
ADD . /opt/croyale
WORKDIR /opt/croyale
RUN pip install -r requirements.txt
CMD python app.py