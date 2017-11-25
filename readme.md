# Phantom

This project is build when I study with the book-&lt;Flask web development:Developing Web applications with Python&gt;

Build on Python3

Database is Mariadb

Powered by Flask

All code are rewritten by me.


### Run Server
In the root folder, add a env file named <code>.env</code>
this is the sample:

``` shell
CURRENT_ENV = <development|production|unixconfig|testing|default>

ADMIN=<Admin Email>

APP_NAME=<APP name, default is zheer.me>
SECRET_KEY=<It is very important ,must set it, hard to guess>
MAIL_PORT=<sender email port ,default is 25,it depend on your email server>
MAIL_USERNAME=<sender email address,it use to send the register link>
MAIL_PASSWORD=<sender password>
MAIL_SERVER=<smtp server address,eg.smtp.163.com>
MAIL_SUBJECT_PREFIX = <prefix for each email>

DB_USER=<database username>
DB_PWD=<if use mysql. it is the password for connect to the database>
```

run:
```
pip install -r requirements/dev.txt
python manange.py shell
>> db.create_all()
>>exit()
:python manage.py deploy
:python manage.py runserver
```