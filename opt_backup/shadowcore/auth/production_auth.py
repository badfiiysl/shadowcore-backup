#!/usr/bin/env python3
"""
ShadowCore Production Auth Service
Updated for production routing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Cookie, Response
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import json
from datetime import datetime
import bcrypt
import secrets
import uuid
import sqlite3

app = FastAPI(title="ShadowCore Auth")

# CORS - Allow all for now, tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shadowcore.club", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DB_PATH = "/var/lib/shadowcore/users.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subscription_tier TEXT DEFAULT 'free',
            search_queries INTEGER DEFAULT 0,
            search_limit INTEGER DEFAULT 100
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

# Initialize
init_db()

# Templates
templates = Jinja2Templates(directory="/var/www/shadowcore/templates")

# Health endpoint
@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API endpoints
@app.post("/api/register")
async def register(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        
        if not email or not password:
            return JSONResponse({"error": "Email and password required"}, status_code=400)
        
        if len(password) < 8:
            return JSONResponse({"error": "Password must be at least 8 characters"}, status_code=400)
        
        conn = get_db()
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return JSONResponse({"error": "Email already registered"}, status_code=400)
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        c.execute('INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)', 
                 (user_id, email, password_hash))
        
        # Create session
        session_id = secrets.token_hex(32)
        expires_at = datetime.now().isoformat()
        
        c.execute('INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
                 (session_id, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        response = JSONResponse({
            "success": True,
            "message": "Registration successful",
            "user": {"email": email, "user_id": user_id},
            "session_id": session_id
        })
        
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,  # Production: set to True for HTTPS
            samesite="lax",
            max_age=604800
        )
        
        return response
        
    except Exception as e:
        print(f"Registration error: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        
        if not email or not password:
            return JSONResponse({"error": "Email and password required"}, status_code=400)
        
        conn = get_db()
        c = conn.cursor()
        
        c.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return JSONResponse({"error": "Invalid credentials"}, status_code=401)
        
        user_id, password_hash = user
        
        if bcrypt.checkpw(password.encode(), password_hash.encode()):
            # Create session
            session_id = secrets.token_hex(32)
            expires_at = datetime.now().isoformat()
            
            c.execute('INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
                     (session_id, user_id, expires_at))
            
            # Get user data
            c.execute('SELECT email, subscription_tier, search_queries, search_limit FROM users WHERE id = ?', (user_id,))
            user_data = c.fetchone()
            
            conn.commit()
            conn.close()
            
            response = JSONResponse({
                "success": True,
                "message": "Login successful",
                "user": {
                    "email": user_data[0],
                    "user_id": user_id,
                    "subscription": user_data[1],
                    "search_queries": user_data[2],
                    "search_limit": user_data[3]
                },
                "session_id": session_id
            })
            
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=604800
            )
            
            return response
        
        conn.close()
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)
        
    except Exception as e:
        print(f"Login error: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.get("/api/user")
async def get_user(session_id: str = Cookie(None)):
    if not session_id:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT u.id, u.email, u.subscription_tier, u.search_queries, u.search_limit 
        FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.session_id = ?
    ''', (session_id,))
    
    user = c.fetchone()
    conn.close()
    
    if not user:
        return JSONResponse({"error": "Invalid session"}, status_code=401)
    
    return JSONResponse({
        "user": {
            "user_id": user[0],
            "email": user[1],
            "subscription": user[2],
            "search_queries": user[3],
            "search_limit": user[4]
        }
    })

@app.post("/api/search")
async def search_threats(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "").strip()
        
        if not query:
            return JSONResponse({"error": "Search query required"}, status_code=400)
        
        # Simulated threat search
        threats = [
            {
                "id": "THR-001",
                "name": f"{query.capitalize()} Malware Variant",
                "severity": "high",
                "category": "Malware",
                "description": f"Newly detected malware campaign using {query}",
                "confidence": 95
            },
            {
                "id": "THR-002", 
                "name": f"{query.capitalize()} Phishing Campaign",
                "severity": "medium",
                "category": "Phishing",
                "description": f"Active phishing campaign targeting {query} users",
                "confidence": 87
            }
        ]
        
        return JSONResponse({
            "success": True,
            "query": query,
            "results": threats,
            "count": len(threats)
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)

# HTML pages
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request, session_id: str = Cookie(None)):
    if not session_id:
        return RedirectResponse(url="/login")
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM sessions WHERE session_id = ?', (session_id,))
    if not c.fetchone():
        conn.close()
        return RedirectResponse(url="/login")
    
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    print("🚀 Starting ShadowCore Production Auth Service...")
    print("🔐 Secure cookies enabled for HTTPS")
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")
