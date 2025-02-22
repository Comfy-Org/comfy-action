# Use the official Python slim image based on Debian Bookworm
# syntax=docker/dockerfile:1.9
FROM debian:bookworm-slim

# Copy the UV package manager binary from its official image
COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /usr/local/bin/uv

# Set UV environment variables:
# - UV_LINK_MODE=copy: Copy dependencies instead of symlinking
# - UV_COMPILE_BYTECODE=1: Compile Python bytecode during installation
# - UV_PROJECT_ENVIRONMENT: Specify virtual environment location
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Create a non-root user 'comfy' for security
# RUN groupadd -g 1000 comfy && useradd -u 1000 -g 1000 -d /home/comfy -m comfy

# Create and set ownership of the application directory
RUN mkdir -p /app

# Define build arguments for Python and PyTorch versions
ARG TORCH_VERSION=stable
ARG CUDA_VERSION=cu124
ARG PYTHON_VERSION=3.12

# Create virtual environment and install PyTorch with CUDA support
# Uses a cache mount to speed up builds by caching pip downloads
RUN --mount=type=cache,target=/root/.cache \
    uv venv /app/.venv --python ${PYTHON_VERSION} && \
    . /app/.venv/bin/activate && \
    if [ "${TORCH_VERSION}" = "stable" ]; then \
        uv pip install torch torchvision torchaudio \
            --index-url "https://download.pytorch.org/whl/${CUDA_VERSION}"; \
    elif [ "${TORCH_VERSION}" = "nightly" ]; then \
        uv pip install --pre torch torchvision torchaudio \
            --index-url "https://download.pytorch.org/whl/nightly/${CUDA_VERSION}"; \
    else \
        uv pip install torch=="${TORCH_VERSION}+${CUDA_VERSION}" \
            torchvision torchaudio \
            --index-url "https://download.pytorch.org/whl/${CUDA_VERSION}"; \
    fi

# Copy the application code and set correct ownership
COPY . /app

# Set the working directory
WORKDIR /app

# Create directories for models, input, and output with correct permissions
RUN mkdir -p /app/models /app/input /app/output && chmod -R 755 /app/models /app/input /app/output

# Install remaining Python dependencies from requirements.txt
# Again uses cache mount for faster builds
RUN --mount=type=cache,target=/root/.cache \
    . /app/.venv/bin/activate && \
    uv pip install -r requirements.txt

# Switch to non-root user for security
# USER comfy

# Expose the port that the application will run on
EXPOSE 8188

# Default command (placeholder for development/debugging)
CMD ["sleep", "infinity"]
