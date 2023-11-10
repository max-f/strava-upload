#!/usr/bin/env python

import os
import pickle
import signal
import time
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from loguru import logger as log
from stravalib.client import Client

load_dotenv()
AUTH_URL = os.getenv("STRAVA_AUTH_URL", "https://www.strava.com/oauth/token")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
API_BASE_URL = os.getenv("STRAVA_API_BASE_URL", "https://www.strava.com/api/v3")
REDIRECT_URL = os.getenv("REDIRECT_URL", "http://localhost:8000/authorized")

TOKEN_FILE = "client.pkl"

app = FastAPI()
client = Client()


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    with open(filename, 'rb') as file:
        loaded_object = pickle.load(file)
        return loaded_object


def check_token():
    if time.time() > client.token_expires_at:
        refresh_response = client.refresh_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                                                       refresh_token=client.refresh_token)
        access_token = refresh_response['access_token']
        refresh_token = refresh_response['refresh_token']
        expires_at = refresh_response['expires_at']
        client.access_token = access_token
        client.refresh_token = refresh_token
        client.token_expires_at = expires_at


@app.get("/")
def read_root():
    authorize_url = client.authorization_url(client_id=CLIENT_ID, redirect_uri=REDIRECT_URL,
                                             scope=['read', 'activity:write'])
    return RedirectResponse(authorize_url)


@app.get("/authorized/")
def get_access_code(state=None, code=None, scope=None):
    token_response = client.exchange_code_for_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, code=code)
    access_token = token_response['access_token']
    refresh_token = token_response['refresh_token']
    expires_at = token_response['expires_at']
    client.access_token = access_token
    client.refresh_token = refresh_token
    client.token_expires_at = expires_at
    save_object(client, TOKEN_FILE)
    return {"state": state, "code": code, "scope": scope}


try:
    client = load_object(TOKEN_FILE)
    check_token()
    athlete = client.get_athlete()
    log.info(f"For athlete {athlete.id}, I now have an access token {client.access_token}")
    date = datetime.fromtimestamp(client.token_expires_at).strftime("%d/%m/%Y %H:%M:%S")
    log.info(f"It expires at {date}")
    log.info("Shutting down auth server - you can use the CLI now!")
    os.kill(os.getpid(), signal.SIGTERM)
except FileNotFoundError:
    log.error("No access token stored yet, visit http://localhost:8000/ to get it")
    log.error("After visiting that url, a pickle file is stored, run this file again to upload your activity")
