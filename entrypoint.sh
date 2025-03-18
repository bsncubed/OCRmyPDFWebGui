#!/bin/bash
# Set timezone if TZ environment variable is provided
if [ -n "$TZ" ]; then
  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
  echo "$TZ" > /etc/timezone
fi

# Set a default Gunicorn timeout if not provided via environment variable
: ${GUNICORN_TIMEOUT:=30}
echo "Starting Gunicorn with timeout ${GUNICORN_TIMEOUT} seconds..."

# Start Gunicorn with the specified timeout
exec gunicorn --timeout "$GUNICORN_TIMEOUT" --workers 4 --bind 0.0.0.0:5000 app:app
