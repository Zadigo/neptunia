FROM ubuntu:latest

RUN apt install python

RUN mkdir app

COPY . ./app

WORKDIR /app

VOLUME [ "/data" ]

ENTRYPOINT [ "-m", "app.py" ]

CMD [ "python" ]
