FROM golang:1.22.2-alpine

COPY golang_import /code/golang_import
WORKDIR /code/golang_import

RUN go install github.com/swaggo/swag/cmd/swag@latest
RUN go mod tidy
RUN go build
RUN swag init

CMD go run main