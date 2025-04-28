# checkov:skip=CKV_DOCKER_2
# checkov:skip=CKV_DOCKER_3
FROM prefecthq/prefect:2.20.7-python3.10

# Install uv (fast Python dependency manager)
RUN pip install --no-cache-dir uv==0.6.16

# Copy dependency files and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync

# Copy your source code
COPY litigation_data_mapper litigation_data_mapper
# Install dependencies
RUN uv sync
