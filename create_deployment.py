import os

from prefect import Flow
from prefect.blocks.system import JSON
from prefect.docker.docker_image import DockerImage

from litigation_data_mapper.flows import automatic_updates, sync_wordpress_to_s3_flow

MEGABYTES_PER_GIGABYTE = 1024
DEFAULT_FLOW_VARIABLES = {
    "cpu": MEGABYTES_PER_GIGABYTE * 1,
    "memory": MEGABYTES_PER_GIGABYTE * 2,
}


def create_deployment(flow: Flow, cron: str) -> None:
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
        # this is scheduled to run daily at midnight
        cron="0 0 * * *",
        work_queue_name="default",
        job_variables=job_variables,
        build=False,
        push=False,
    )


if __name__ == "__main__":
    # at midnight
    create_deployment(automatic_updates, cron="0 0 * * *")
    # every 4 hours from 3-23
    # this means this will have run before the midnight run above
    create_deployment(sync_wordpress_to_s3_flow, cron="0 3,7,11,15,19,23 * * *")
