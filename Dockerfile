FROM python:3.10-slim-buster

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt update \
    && apt install -y wget \
    && apt install -y unzip

# install chrom browser for selenium use
ARG CHROME_VERSION="101.0.4951.41-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

WORKDIR app/
COPY . .

# download the chrome driver for use with selenium
RUN wget https://chromedriver.storage.googleapis.com/101.0.4951.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && rm chromedriver_linux64.zip \
    && chmod 755 chromedriver \
    && mv chromedriver /usr/local/bin/

# volume for env-specific data
VOLUME ["data" ]

# uncomment for debug to keep container running
#ENTRYPOINT ["tail", "-f", "/dev/null"]
ENTRYPOINT [ "python3", "run_search.py" ]

