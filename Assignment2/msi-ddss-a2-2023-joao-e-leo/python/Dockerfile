#
# Authors: Nuno Antunes <nmsa@dei.uc.pt>, João Antunes <jcfa@dei.uc.pt>
#

from python:3.12-alpine3.18

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

run pip install flask==3.0.0

run pip install psycopg2-binary

#Added to use function for encrypting password
run pip install argon2-cffi

#Added for TOTP 2FA authentication in Python
run pip install pyotp

copy . /app

volume ["/app"]

workdir /app

run mkdir -p logs

EXPOSE 5000

CMD ["python", "app.py"]
