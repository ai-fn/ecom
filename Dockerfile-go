FROM golang:1.22.2-alpine

COPY golang_import /code/golang_import
WORKDIR /code/golang_import

RUN go mod tidy
RUN go build

CMD sleep 9999999