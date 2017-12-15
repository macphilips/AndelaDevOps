# FROM node:carbon
FROM node:9.3.0

RUN apt-get install -y git-core

# Create app directory
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

# Install app dependencie
RUN git clone git://github.com/macphilips/UserManager.git /usr/src/app \
 && npm install
COPY env /usr/src/app
RUN mv env .env
EXPOSE 3000

CMD ["npm","start"]

