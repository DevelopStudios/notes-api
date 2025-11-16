# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# 2. Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy and install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Inform Docker that the container listens on port 8000
EXPOSE 8000

# 7. Define the command to run your app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]