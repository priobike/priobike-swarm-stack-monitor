FROM alpine
RUN apk add python3
RUN apk add docker
COPY run.py /run.py
CMD ["python3", "/run.py"]