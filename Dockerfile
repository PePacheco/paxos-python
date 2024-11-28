FROM python:2.7

WORKDIR /app

COPY src/ /app/src
COPY config/ /app/config

EXPOSE 10000

ENV NODE_TYPE=LEADER
ENV NODE_ID=1
ENV HOST_IP=127.0.0.1
ENV PORT=10000

CMD ["python2", "./src/main.py"]
