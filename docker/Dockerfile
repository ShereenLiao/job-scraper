FROM python:3.6.12-slim-buster

ARG CHROME_VERSION=111.0.5563.64-1
ARG CHROME_DRIVER_VERSION=111.0.5563.64

RUN apt-get update && apt-get install -y \
	wget \
    unzip \
    sudo\
    python3-pip\
    libmysqlclient-dev\
    mariadb-server

    
#install chrome and chrome driver
RUN mkdir -p /usr/local/tmp \
	&& cd /usr/local/tmp \
	&& wget http://dl.google.com/linux/deb/pool/main/g/google-chrome-stable/google-chrome-stable_"$CHROME_VERSION"_amd64.deb \
    && apt-get install -y ./google-chrome-stable_"$CHROME_VERSION"_amd64.deb \
	&& wget https://chromedriver.storage.googleapis.com/"$CHROME_DRIVER_VERSION"/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver

COPY requirements.txt /usr/local/tmp/

COPY scraper /user/local/

RUN pip install -r /usr/local/tmp/requirements.txt

CMD python /user/local/main.py \
    mysql_host=${mysql_host} \
    mysql_user=${mysql_user} \
    mysql_password=${mysql_password} \
    LI_AT_COOKIE=${li_at} > logs.txt


ENTRYPOINT [ "/bin/bash" ]




