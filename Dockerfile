FROM jbarlow83/ocrmypdf:latest

# Install packages, including tzdata for timezone support
RUN apt-get update && apt-get install -y python3-flask python3-pip zip tzdata

WORKDIR /app

# Copy application code and entrypoint script
COPY app /app
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Install gunicorn using pip with the flag to override external management
RUN pip3 install --break-system-packages gunicorn

# Expose the application port
EXPOSE 5000

# Override the base image's ENTRYPOINT with our custom script
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
