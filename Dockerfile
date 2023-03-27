FROM ubuntu:latest

ENV USER=neptunia
# Create group
RUN groupadd --gid 1000 ${USER}
# Create user (based on the current gid
# of the user on the server ex. id ubuntu)
RUN useradd --uid 1000 --gid 1000 --base-dir /code --home-dir /code ${USER}

LABEL "com.example.neptunia"="neptunia"

# Install/Update Pip
RUN pip install --upgrade pip
RUN pip3 install pipenv

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

RUN mkdir app

COPY . ./app

WORKDIR /app

EXPOSE 8011

VOLUME [ "/data" ]

ENTRYPOINT [ "-m", "app.py" ]

CMD [ "python" ]
