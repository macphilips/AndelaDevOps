# FROM node:carbon
FROM node:9.3.0

# File Author / Maintainer
MAINTAINER tmorolari@gmail.com

RUN apt-get install -y git-core

# Create app directory
RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

# Clone and Install app dependencie
RUN git clone git://github.com/macphilips/UserManager.git /usr/src/app \
 && npm install

#COPY env /usr/src/app
#RUN mv env .env

EXPOSE 3000
ENTRYPOINT "/bin/bash"

#CMD ["npm","start"]

