import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks
from scalekit.client import ScalekitClient

load_dotenv()
