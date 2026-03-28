from pages.login import render_login
from fastapi import FastAPI, Request, BackgroundTasks

fastapi = FastAPI(title="Agent Backend")


if __name__ == "__main__":
    render_login()

