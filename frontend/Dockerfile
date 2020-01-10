FROM node:9.6.1 AS nodejs
WORKDIR /build/
ENV PATH /build/node_modules/.bin:/build:$PATH

COPY package.json .
COPY yarn.lock .
RUN npm run develop
RUN ls -l /build/node_modules
COPY . .
RUN npm run build


FROM nginx as prod

COPY --from=nodejs /build/build /app
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

FROM prod
