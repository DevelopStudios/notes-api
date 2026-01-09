# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the application code
COPY . .

# 6. Collect Static Files (CSS/JS for Admin)
# We set a dummy secret key just for this build step so it doesn't crash
RUN python manage.py collectstatic --noinput --clear

# 7. Expose the port (Kinsta uses 8080 internally often, but 8000 is fine if configured)
EXPOSE 8080

# 8. Run Gunicorn (Production Server)
# 'config.wsgi' refers to the folder 'config' containing 'wsgi.py'
# Check your folder structure: if your main folder is named 'config', use 'config.wsgi'
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "config.wsgi:application"]