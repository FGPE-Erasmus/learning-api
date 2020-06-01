# Learning platform API

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


## Requirements

* Python 3
* Docker + Docker Compose

## Installation

```bash
$: virtualenv -p python3 {env}
$: source {env}/bin/activate
$: git clone {url}
$: pip install -r requirements.txt
```

## Configuration

```bash
$: cp local_settings.py.template local_settings.py

Set DATABASE, MAIL, API and FGPE data in local_settings.py
Generate and set SECRETS in local_settings.py

To create database or make migration based on changes in tables.py use:

$: python db_manager.py
```

## Outside Docker containers

TODO
