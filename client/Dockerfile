FROM node:20-alpine

WORKDIR /usr/src/app

RUN npm install -g live-server

COPY . .

EXPOSE 8080

ENV HOST=0.0.0.0
ENV PORT=8080

CMD ["sh", "-c", "live-server /usr/src/app/client --host=0.0.0.0 --port=8080 --entry-file=index.html"]