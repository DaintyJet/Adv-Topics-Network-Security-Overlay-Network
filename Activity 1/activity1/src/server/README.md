## Setting up the server

### Installing server packages

```
$ sudo apt install gcc \
    python3-dev \
    mysql-server \
    libmysqlclient-dev \
    --no-install-recommends
```

```
$ cd activity1/src/server
$ python3 -m pip install --upgrade pip
$ python3 -m pip install pipenv
$ python3 -m pipenv shell

(server) $ pipenv install
(server) $ pipenv install --dev
```

### Starting the server

```
$ sudo  mysql -u root
mysql> CREATE USER 'comp6610'@'localhost' IDENTIFIED WITH mysql_native_password BY 'comp6610';
mysql> CREATE DATABASE comp6610;
mysql> GRANT ALL PRIVILEGES ON *.* TO 'comp6610'@'localhost';
mysql> commit;
mysql> quit;

$ mysql -u comp6610 -p
mysql> USE comp6610;
mysql> SHOW TABLES;
mysql> quit;
```

```
(server) $ cd chat_server
(server) $ python3 manage.py migrate
(server) $ python3 manage.py createsuperuser
Username (leave blank to use 'student'): student
Email address: comp6610_student@uml.edu
Password: 
Password (again): 
Superuser created successfully.
(server) $ python3 manage.py runserver 0.0.0.0:8888
```
