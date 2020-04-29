# Learning platform api

## INSTALATION
```
$: pip install virtualenv
$: virtualenv {env}
$: source {env}/bin/activate
$: git clone {url}
$: pip install -r requirements.txt
```

## PROJECT SETTINGS
```
$: cp local_settings.py.template local_settings.py

Set DATABASE, MAIL, API and FGPE data in local_settings.py
Generate and set SECRETS in local_settings.py
```

## DATABASE
```
To create database or make migration based on changes in tables.py use:

$: python db_manager.py
```

## RUN
```
$: python wsig.py
```

## gunicorn
```
$: gunicorn --bind 0.0.0.0:9000 -w 4 wsgi:app
```
