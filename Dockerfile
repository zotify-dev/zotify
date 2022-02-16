FROM python:3.9-alpine as base

RUN apk --update add ffmpeg

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN apk add gcc libc-dev zlib zlib-dev jpeg-dev \
    && pip install --prefix="/install" -r /requirements.txt


FROM base

COPY --from=builder /install /usr/local
COPY zotify /app/zotify
WORKDIR /app
ENTRYPOINT ["python3", "-m", "zotify"]
