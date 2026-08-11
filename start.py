"""start.py — entry point for Render / IBM Cloud deployment."""
import os
from dotenv import load_dotenv

load_dotenv()

import db as cloudant
import app as application

if __name__ == "__main__":
    cloudant.bootstrap()
    port = int(os.environ.get("PORT", 5052))
    application.app.run(debug=False, host="0.0.0.0", port=port)
