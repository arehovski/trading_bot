FROM node:carbon

WORKDIR /app
# Копируем package.json и package-lock.json и делаем npm install, чтобы зависимости закешировались.
COPY frontend/package*.json ./
RUN npm install
# Наши исходники мы примонтируем в другую папку,
# так что надо задать PATH.
ENV PATH /app/node_modules/.bin:$PATH

# Финальный слой содержит билд нашего приложения.
ADD frontend /app/src
WORKDIR /app/src
RUN npm run build
CMD npm run start