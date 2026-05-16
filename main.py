from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(TEMPLATES_DIR):
    os.makedirs(TEMPLATES_DIR)

from database import get_db, User, Location, DailyUsage, MembershipPlan, ServiceStatus, BomberLog, SearchLog
from auth import hash_password, verify_password, create_access_token, decode_token, get_user_from_token
from email_service import generate_verification_code, send_verification_email, send_welcome_email
from bomber import run_bomber
from crypto import router as crypto_router

app = FastAPI(title="Black Whale Security System")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crypto_router)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    public_paths = ["/", "/login", "/register", "/verify", "/static", "/crypto", "/crypto/", "/api/crypto"]
    
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=302)
    
    payload = decode_token(token)
    if not payload:
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie("access_token")
        return response
    
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/crypto", response_class=HTMLResponse)
async def crypto_page(request: Request):
    return templates.TemplateResponse("crypto.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/verify", response_class=HTMLResponse)
async def verify_page(request: Request, email: str = ""):
    return templates.TemplateResponse("verify.html", {"request": request, "email": email})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return RedirectResponse(url="/login")
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily = db.query(DailyUsage).filter(DailyUsage.user_id == user.id, DailyUsage.date == today).first()
    if not daily:
        daily = DailyUsage(user_id=user.id, date=today)
        db.add(daily)
        db.commit()
    
    plan = db.query(MembershipPlan).filter(MembershipPlan.name == user.membership).first()
    services = db.query(ServiceStatus).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "daily": daily,
        "plan": plan,
        "services": services
    })

@app.get("/bomber", response_class=HTMLResponse)
async def bomber_page(request: Request):
    return templates.TemplateResponse("bomber.html", {"request": request})

@app.get("/scraper", response_class=HTMLResponse)
async def scraper_page(request: Request):
    return templates.TemplateResponse("scraper.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/location", response_class=HTMLResponse)
async def location_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("location.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user or user.role != "admin":
        return RedirectResponse(url="/dashboard")
    
    users = db.query(User).all()
    logs = db.query(BomberLog).order_by(BomberLog.created_at.desc()).limit(100).all()
    services = db.query(ServiceStatus).all()
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "users": users,
        "logs": logs,
        "services": services
    })

@app.post("/api/register")
async def api_register(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter((User.email == email) | (User.username == username)).first()
    if existing:
        return {"success": False, "message": "Email or username already exists"}
    
    code = generate_verification_code()
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        verification_code=code,
        membership="bronze",
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    
    send_verification_email(email, code)
    return {"success": True, "message": "Verification code sent", "email": email}

@app.post("/api/verify")
async def api_verify(
    email: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email, User.verification_code == code).first()
    if not user:
        return {"success": False, "message": "Invalid verification code"}
    
    user.is_verified = True
    user.verification_code = None
    db.commit()
    
    send_welcome_email(email, user.username)
    return {"success": True, "message": "Email verified successfully"}

@app.post("/api/login")
async def api_login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "Invalid credentials"}
    
    if not user.is_verified:
        return {"success": False, "message": "Please verify your email first"}
    
    if not verify_password(password, user.password_hash):
        return {"success": False, "message": "Invalid credentials"}
    
    user.last_login = datetime.now()
    db.commit()
    
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    response = JSONResponse({"success": True, "redirect": "/dashboard"})
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=43200, path="/")
    return response

@app.get("/api/logout")
async def api_logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response

@app.get("/api/user/limits")
async def api_user_limits(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return {"error": "Unauthorized"}
    
    plan = db.query(MembershipPlan).filter(MembershipPlan.name == user.membership).first()
    today = datetime.now().strftime("%Y-%m-%d")
    daily = db.query(DailyUsage).filter(DailyUsage.user_id == user.id, DailyUsage.date == today).first()
    
    return {
        "membership": user.membership,
        "daily_bomber_limit": plan.daily_bomber_limit if plan else 50,
        "daily_search_limit": plan.daily_search_limit if plan else 20,
        "bomber_used": daily.bomber_used if daily else 0,
        "search_used": daily.search_used if daily else 0
    }

@app.post("/api/bomber/start")
async def api_bomber_start(
    request: Request,
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return {"success": False, "error": "Unauthorized"}
    
    if not phone.startswith('09') or len(phone) != 11:
        return {"success": False, "error": "Invalid phone number"}
    
    plan = db.query(MembershipPlan).filter(MembershipPlan.name == user.membership).first()
    today = datetime.now().strftime("%Y-%m-%d")
    daily = db.query(DailyUsage).filter(DailyUsage.user_id == user.id, DailyUsage.date == today).first()
    
    if not daily:
        daily = DailyUsage(user_id=user.id, date=today)
        db.add(daily)
        db.commit()
    
    remaining = (plan.daily_bomber_limit if plan else 50) - daily.bomber_used
    if remaining <= 0:
        return {"success": False, "error": f"Daily limit reached. Upgrade your plan."}
    
    limit = min(remaining, 5)
    result = run_bomber(phone, limit)
    
    daily.bomber_used += limit
    db.commit()
    
    log = BomberLog(
        user_id=user.id,
        target_phone=phone,
        success_count=result['success'],
        failed_count=result['failed'],
        total_requests=result['total'],
        created_at=datetime.now()
    )
    db.add(log)
    db.commit()
    
    return {
        "success": True,
        "stats": result,
        "remaining": (plan.daily_bomber_limit if plan else 50) - daily.bomber_used,
        "membership": user.membership
    }

@app.post("/api/locations/save")
async def save_location(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return {"success": False, "error": "Unauthorized"}
    
    data = await request.json()
    
    location = Location(
        user_id=user.id,
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        address=data.get("address"),
        ip_address=request.client.host,
        browser_info=request.headers.get("user-agent", ""),
        created_at=datetime.now()
    )
    db.add(location)
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily = db.query(DailyUsage).filter(DailyUsage.user_id == user.id, DailyUsage.date == today).first()
    if daily:
        daily.location_used += 1
    else:
        daily = DailyUsage(user_id=user.id, date=today, location_used=1)
        db.add(daily)
    
    db.commit()
    
    return {"success": True, "message": "Location saved"}

@app.get("/api/locations/history")
async def get_location_history(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    user = get_user_from_token(token, db)
    if not user:
        return {"success": False, "error": "Unauthorized"}
    
    locations = db.query(Location).filter(Location.user_id == user.id).order_by(Location.created_at.desc()).limit(50).all()
    
    return {
        "success": True,
        "locations": [
            {
                "id": loc.id,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "address": loc.address,
                "created_at": loc.created_at.isoformat()
            }
            for loc in locations
        ]
    }

@app.post("/api/admin/user/upgrade")
async def api_admin_upgrade(
    request: Request,
    user_id: int = Form(...),
    membership: str = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    admin = get_user_from_token(token, db)
    if not admin or admin.role != "admin":
        return {"success": False, "error": "Unauthorized"}
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"success": False, "error": "User not found"}
    
    user.membership = membership
    db.commit()
    
    return {"success": True}

@app.post("/api/admin/service/status")
async def api_admin_service_status(
    request: Request,
    service_id: int = Form(...),
    is_online: bool = Form(...),
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    admin = get_user_from_token(token, db)
    if not admin or admin.role != "admin":
        return {"success": False, "error": "Unauthorized"}
    
    service = db.query(ServiceStatus).filter(ServiceStatus.id == service_id).first()
    if service:
        service.is_online = is_online
        service.last_check = datetime.now()
        db.commit()
    
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    from database import init_db
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)