# checkov:skip=CKV_DOCKER_2
# checkov:skip=CKV_DOCKER_3
FROM prefecthq/prefect:2.20.7-python3.10

# Install uv (fast Python dependency manager)
RUN pip install --no-cache-dir uv==0.6.16
# This ensures that the dependencies are installed at system python level
# without having to activate a venv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

# Copy dependency files
COPY pyproject.toml uv.lock ./
# Copy your source code
COPY litigation_data_mapper litigation_data_mapper

# Install dependencies using the lockfile without checking if it is up-to-date
RUN uv sync --frozen
