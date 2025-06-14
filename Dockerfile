FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

ENV HOME=/home/user
ENV PATH=$PATH:/home/user/.local/bin
ENV TRANSFORMER_HOME=/app/transformer_cache
ENV OMP_NUM_THREADS=1

# Create a directory for the application
WORKDIR /main


COPY --chown=user . /main

# Expose default HuggingFace Spaces port
#EXPOSE ... -> Uncomment and set the port

# Run FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "..."]