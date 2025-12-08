from fastapi import FastAPI
from app.routes import users, posts
from app.database import db

app = FastAPI(title="Blog System", version="1.0.0")

# Подключаем роутеры
app.include_router(users.router)
app.include_router(posts.router)

@app.get("/")
async def root():
    return {
        "message": "Blog System API",
        "users_count": len(db.users),
        "posts_count": len(db.posts)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)