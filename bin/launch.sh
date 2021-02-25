#!/bin/bash

uwsgi --http  0.0.0.0:8080 --callable app --wsgi-file rest_endpoints.py --master --threads 2 --processes 4
