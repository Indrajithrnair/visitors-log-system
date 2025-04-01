#!/bin/bash

# Set the Python path to include the current directory and the visitor_log directory
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/visitor_log

# Run gunicorn with the correct WSGI application
exec gunicorn visitor_log.wsgi:application --bind 0.0.0.0:$PORT 