# Use the official Python image as the base image for a stable and small environment.
# 'slim' is preferred for smaller image size.
FROM python:3.11-slim

# Set the working directory inside the container to /app.
# All subsequent commands will be executed from this directory.
WORKDIR /app

# Copy the requirements file first. This optimizes Docker's build cache.
# If only the code changes, this layer won't be rebuilt.
COPY requirements.txt .

# Install Python dependencies specified in requirements.txt.
# --no-cache-dir reduces the size of the final image.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (including the 'src' and 'templates' folders) 
# from the local machine into the container's working directory (/app).
COPY . .

# Set the PORT environment variable. Cloud Run expects the container to listen on 8080.
# We set it here, and Gunicorn will use it (as we bind to 0.0.0.0:8080).
ENV PORT 8080

# The command to execute when the container starts.
# We use Gunicorn as the production-grade web server.
# The format 'src.app:app' tells Gunicorn to look inside the 'src' folder 
# for the 'app.py' file, and find the Flask instance named 'app'.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src.app:app"]