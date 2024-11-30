FROM python:2.7

WORKDIR /app/src

COPY src/ /app/src
COPY config/ /app/config
COPY logs/ /app/logs

EXPOSE 10000

CMD ["python2", "./env.py"]
