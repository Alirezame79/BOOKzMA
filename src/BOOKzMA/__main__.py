import uvicorn

uvicorn.run("BOOKzMA.api:create_app", factory=True, host="0.0.0.0", port=8000)
