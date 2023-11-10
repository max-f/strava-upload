import os
import pickle
from typing import Annotated

import typer
from loguru import logger as log
from stravalib.client import Client

app = typer.Typer()
client: Client
TOKEN_FILE = "client.pkl"


def load_object(filename):
    with open(filename, 'rb') as file:
        loaded_object = pickle.load(file)
        return loaded_object


@app.command()
def upload(number: Annotated[int, typer.Option(help="Number of files to upload")] = 1):
    typer.echo("Uploading files to strava..")
    typer.echo("Checking if Garmin head unit is mounted..")

    user: str = os.getlogin()
    try:
        # os.chdir(f"/run/media/{user}/GARMIN/Garmin/Activities/")
        os.chdir(f"/home/{user}/var/music")

    except FileNotFoundError:
        typer.echo("\n")
        typer.echo("Garmin head unit not mounted.")
        typer.echo("Exiting..")
        return

    file_names: list[str] = os.listdir()
    file_names.sort(reverse=True)
    print(file_names)
    print(int(number))
    for file_name in file_names[:number]:
        upload_file(file_name)


def upload_file(file: str):
    try:
        really_upload = typer.confirm(f"Do you want to upload {file}?", abort=True)
    except typer.Abort:
        typer.echo("Aborting..")
        return
    activity_title = typer.prompt("Enter a title for the activity", default="")
    with open(file, "rb") as payload:
        uploader_response = client.upload_activity(payload, name=activity_title, data_type="fit")
        uploader_response.wait()



try:
    client = load_object(TOKEN_FILE)
    log.info(f"Got client {client.access_token}")
except FileNotFoundError:
    log.error("No token file found. Please run `rye run auth` first.")
    raise SystemExit(1)

if __name__ == "__main__":
    app()
