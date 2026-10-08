FROM python:3.12-slim

# Prevent writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install minimal tools and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged sandbox user
RUN groupadd -g 1001 sandboxgroup && \
    useradd -u 1001 -g sandboxgroup -m -s /bin/bash sandboxuser

WORKDIR /runner
COPY sandbox/requirements.txt /runner/requirements.txt
RUN pip install --no-cache-dir -r /runner/requirements.txt

COPY sandbox/runner/run_test.py /runner/run_test.py
RUN chmod +x /runner/run_test.py

WORKDIR /workspace
RUN chown -R sandboxuser:sandboxgroup /workspace /runner

USER sandboxuser

ENTRYPOINT ["python", "/runner/run_test.py"]
CMD ["/workspace", "test.py"]
