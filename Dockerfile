FROM python:3.12.0a6-bullseye

RUN useradd -ms /bin/bash cade

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libfontconfig \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxtst6 \
    libgtk-3-0 \
    libgbm-dev \
    gnupg

# install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
ENV PATH="/usr/local/bin:${PATH}"

# install python requirements
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Add SHA256 Signature method to oauth2 __init__.py
# Add code to __init__.py file
RUN echo "from hashlib import sha256\n\
\n\
class SignatureMethod_HMAC_SHA256(SignatureMethod):\n\
    name = 'HMAC-SHA256'\n\
\n\
    def signing_base(self, request, consumer, token):\n\
        if (not hasattr(request, 'normalized_url') or request.normalized_url is None):\n\
            raise ValueError('Base URL for request is not set.')\n\
\n\
        sig = (\n\
            escape(request.method),\n\
            escape(request.normalized_url),\n\
            escape(request.get_normalized_parameters()),\n\
        )\n\
\n\
        key = '%s&' % escape(consumer.secret)\n\
        if token:\n\
            key += escape(token.secret)\n\
        raw = '&'.join(sig)\n\
        return key.encode('ascii'), raw.encode('ascii')\n\
\n\
    def sign(self, request, consumer, token):\n\
        key, raw = self.signing_base(request, consumer, token)\n\
\n\
        hashed = hmac.new(key, raw, sha256)\n\
\n\
        # Calculate the digest base 64.\n\
        return binascii.b2a_base64(hashed.digest())[:-1]\n"\
         >> $(pip show oauth2 | grep Location | cut -d " " -f 2)/oauth2/__init__.py

ENV CHROME_OPTS="--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"

COPY src/ /app/
RUN chown -R cade:cade /app
USER cade

CMD ["python", "-u", "ingram_scraper.py"]
