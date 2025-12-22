module.exports = {
  apps: [
    {
      name: "attendance-app",
      script: "/var/www/html/UrbanFitnessFaceRec/myenv/bin/python3",
      interpreter: "none",
      args: [
        "-m",
        "streamlit",
        "run",
        "Home.py",
        "--server.address=127.0.0.1",
        "--server.port=8501",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.enableWebsocketCompression=false"
      ],
      cwd: "/var/www/html/UrbanFitnessFaceRec",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
}
