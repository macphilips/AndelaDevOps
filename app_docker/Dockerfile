FROM node:carbon
# FROM node:9.3.0

RUN apt-get install -y git-core

RUN mkdir -p /usr/src/app 

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
RUN git clone git://github.com/macphilips/UserManager.git && cd UserManager

RUN npm install


EXPOSE 3000
CMD [ "npm", "start" ]
