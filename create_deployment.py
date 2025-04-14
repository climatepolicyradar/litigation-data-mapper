from prefect import flow
from prefect.docker.docker_image import DockerImage
from prefect.schedules import CronSchedule

from litigation_data_mapper.cli import automatic_updates

if __name__ == "__main__":
    automatic_updates.deploy(
        name="litigation-automatic-updates-deployment",
        work_pool_name="litigation-automatic-updates-work-pool",
        image=DockerImage(
            name="532586131621.dkr.ecr.eu-west-1.amazonaws.com/litigation-data-mapper",
            tag="latest",
            dockerfile="Dockerfile",
        ),
        schedule=CronSchedule(cron="* * * * *"),
    )
