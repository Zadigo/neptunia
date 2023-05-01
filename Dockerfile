FROM python:latest

ENV USER=neptunia
# Create group
RUN groupadd --gid 1000 ${USER}
# Create user (based on the current gid
# of the user on the server ex. id ubuntu)
RUN useradd --uid 1000 --gid 1000 --base-dir /neptunia --home-dir /neptunia ${USER}

LABEL "com.example.neptunia"="neptunia"

# RUN apt-get update

# RUN apt-get install -y python3

# RUN apt-get install -y python3-pip

RUN python3 --version

# Install/Update Pip
RUN pip install --upgrade pip
RUN pip3 install pipenv

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

RUN mkdir neptunia

WORKDIR /neptunia

# RUN echo 'export PATH=$PATH:/neptunia/neptunia/app.py' >> ~/.bashrc

# RUN . ~/.bashrc

# RUN echo $PATH

COPY . .

EXPOSE 8011

VOLUME [ "/data" ]

ENTRYPOINT [ "-m", "/neptunia/app.py" ]

CMD [ "python" ]
