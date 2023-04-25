FROM python:3.9-alpine as base

RUN apk --update add ffmpeg

FROM base as builder

RUN apk --update add git

WORKDIR /install
COPY requirements.txt /requirements.txt

RUN apk add gcc libc-dev zlib zlib-dev jpeg-dev
RUN pip install --prefix="/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local/lib/python3.9/site-packages
RUN mv /usr/local/lib/python3.9/site-packages/lib/python3.9/site-packages/* /usr/local/lib/python3.9/site-packages/

COPY zotify /app/zotify

WORKDIR /app
CMD ["python3", "-m", "zotify"]
