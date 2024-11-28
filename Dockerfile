# Use Python 2.7 image
FROM python:2.7

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Expose the necessary port
EXPOSE 10000

# Set environment variables
ENV NODE_TYPE=${NODE_TYPE}
ENV NODE_ID=${NODE_ID}
ENV HOST_IP=${HOST_IP}
ENV PORT=${PORT}

# Run the process
CMD ["python", "env.py", "config.txt", "${NODE_ID}", "${NODE_TYPE}"]
