FROM node:20-alpine

WORKDIR /usr/src/app

RUN npm install -g live-server

COPY . .

EXPOSE 8080

ENV PORT=8080
ENV HOST=0.0.0.0

CMD ["sh", "-c", "live-server /usr/src/app --host=$HOST --port=$PORT --entry-file=index.html"]
