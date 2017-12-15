# FROM node:carbon
FROM node:9.3.0

RUN apt-get install -y git-core

# Create app directory
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

# Install app dependencie
RUN git clone git://github.com/macphilips/UserManager.git /usr/src/app \
 # && mv .env-sample .env \
 # && printf "PORT=3000\nDB_URL='mongodb://localhost:27017/andelaDB'\n" > .env \
 && npm install
COPY env /usr/src/app
RUN mv env .env
EXPOSE 3000

CMD ["npm","start"]