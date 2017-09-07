FROM scrapinghub/scrapinghub-stack-scrapy:1.3-py3

RUN apt-get -yqq update && \
    apt-get -yqq install curl unzip && \
    apt-get -yqq install xvfb tinywm && \
    apt-get -yqq install fonts-ipafont-gothic xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic && \
    apt-get -yqq install python && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
&& mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION \
&& curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
&& unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION \
&& rm /tmp/chromedriver_linux64.zip \
&& chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver \
&& ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver


# Install Google Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
&& sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'  \
&& apt-get -yqq update \
&& apt-get -yqq install google-chrome-stable \
&& rm -rf /var/lib/apt/lists/*
RUN wget -q https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar -xjf phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin && \
    rm -rf phantomjs-2.1.1-linux-x86_64.tar.bz2 phantomjs-2.1.1-linux-x86_64
ENV TERM xterm
ENV SCRAPY_SETTINGS_MODULE crawlers.settings
RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . /app
RUN python3 setup.py install
