import os

from prefect import Flow
from prefect.blocks.system import JSON
from prefect.docker.docker_image import DockerImage

from litigation_data_mapper.flows import automatic_updates

MEGABYTES_PER_GIGABYTE = 1024
DEFAULT_FLOW_VARIABLES = {
    "cpu": MEGABYTES_PER_GIGABYTE * 1,
    "memory": MEGABYTES_PER_GIGABYTE * 2,
}


def create_deployment(
    flow: Flow,
) -> None:
    """Create a deployment for the specified flow"""
    aws_env = os.environ["AWS_ENV"]
    docker_registry = os.environ["DOCKER_REGISTRY"]

    # trunk ignore
    default_variables = JSON.load(f"default-job-variables-prefect-mvp-{aws_env}").value  # type: ignore
    job_variables = {**default_variables, **DEFAULT_FLOW_VARIABLES}

    _ = flow.deploy(
        "litigation-automatic-updates-deployment",
        work_pool_name=f"mvp-{aws_env}-ecs",
        image=DockerImage(
            name=f"{docker_registry}/litigation-data-mapper",
            tag="latest",
            dockerfile="Dockerfile",
        ),
        cron="0 0 * * *",
        work_queue_name=f"mvp-{aws_env}",
        job_variables=job_variables,
        build=False,
        push=False,
    )


if __name__ == "__main__":
    create_deployment(automatic_updates)
