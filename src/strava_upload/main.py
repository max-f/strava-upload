import os
from typing import Annotated

import typer
from loguru import logger as log
from stravalib.client import Client
from stravalib.exc import ActivityUploadFailed

from . import utils

app = typer.Typer()
client: Client


@app.command()
def upload(number: Annotated[int, typer.Option(help="Number of files to upload")] = 1):
    log.info("Uploading files to strava..")
    log.info("Checking if Garmin head unit is mounted..")

    user: str = os.getlogin()
    try:
        os.chdir(f"/run/media/{user}/GARMIN/Garmin/Activities/")
        # os.chdir(f"/home/{user}/var/music")

    except FileNotFoundError:
        log.error("Garmin head unit not mounted.")
        log.error("Exiting..")
        raise SystemExit(1)

    file_names: list[str] = os.listdir()
    file_names.sort(reverse=True)
    print(file_names)
    print(int(number))
    for file_name in file_names[:number]:
        upload_file(file_name)


def upload_file(file: str):
    try:
        typer.confirm(f"Do you want to upload {file}?", abort=True)
    except typer.Abort:
        log.info(f"Skipping upload of file {file}")
        return
    activity_title = typer.prompt("Enter a title for the activity", default="")
    with open(file, "rb") as payload:
        try:
            uploader_response = client.upload_activity(payload, name=activity_title, data_type="fit")
            uploader_response.wait()
        except ActivityUploadFailed as e:
            if e.args and 'access_token' in e.args[0] and 'invalid' in e.args[0]:
                log.error("Access token invalid, please run `rye run auth` again")
                raise SystemExit(1)
            else:
                log.error(e)
                raise SystemExit(1)


try:
    client = utils.load_object(utils.TOKEN_FILE)
    log.info(f"Got client {client.access_token}")
except FileNotFoundError:
    log.error("No token file found. Please run `rye run auth` first.")
    raise SystemExit(1)

if __name__ == "__main__":
    app()
