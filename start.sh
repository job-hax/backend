#!/usr/bin/env bash
python3 manage.py runserver 0.0.0.0:8001 &
python3 manage.py process_tasks