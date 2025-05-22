# We are skipping the healthcheck because it is not needed for the Prefect agent
# since this is a CLI tool and not a service that needs to be monitored
# we also don't have a health endpoint to ping to provide a meaningful healthcheck
# checkov:skip=CKV_DOCKER_2

FROM prefecthq/prefect:2.20.7-python3.10

# Create a non-root user
RUN useradd -m -u 1000 prefect_user

# This ensures that the dependencies are installed at system python level
# without having to activate a venv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

# Copy dependency files
COPY pyproject.toml uv.lock ./
# Copy your source code
COPY litigation_data_mapper litigation_data_mapper

# Install uv (fast Python dependency manager)
RUN UV_VERSION=$(grep "uv>=" pyproject.toml | cut -d'=' -f2 | tr -d '"' | tr -d ' ' | tr -d ',') && \
    pip install --no-cache-dir uv==${UV_VERSION}

# Install dependencies using the lockfile
RUN uv sync --frozen

# Set up permissions for prefect_user
RUN mkdir -p /opt/prefect && \
    chown -R prefect_user:prefect_user /opt/prefect && \
    chmod -R 755 /opt/prefect && \
    chown -R prefect_user:prefect_user /home/prefect_user && \
    chown -R prefect_user:prefect_user /usr/local/lib/python3.10/site-packages

# Switch to non-root user
USER prefect_user

CMD ["sleep", "10000"]
