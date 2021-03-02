#!/bin/bash
cd app
uwsgi --http  0.0.0.0:8081 --callable app --wsgi-file rest_endpoints.py --master --threads 2 --processes 4
