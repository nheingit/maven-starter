from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .database import get_db, initialize_database
from .schemas import BlogPost

initialize_database()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update this with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/blog/{post_id}", response_model=BlogPost)
def get_blog_post(post_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM blog_posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
    if post is None:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    return BlogPost(id=post[0], title=post[1], content=post[2])

@app.get("/api/blog", response_model=List[BlogPost])
def get_all_blog_posts():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM blog_posts")
        posts = cursor.fetchall()
    
    return [BlogPost(id=post[0], title=post[1], content=post[2]) for post in posts]