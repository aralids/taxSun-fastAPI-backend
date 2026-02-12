from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://taxsun-frontend-production-ed00.up.railway.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
