from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# JWT Configuration
JWT_ALGORITHM = "HS256"

def get_jwt_secret() -> str:
    return os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")

# Password hashing utilities
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# JWT token creation
def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "type": "access"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

# Auth dependency
async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        populate_by_name = True

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    course: str
    status: str = "active"

    @validator('status')
    def validate_status(cls, v):
        if v not in ['active', 'inactive']:
            raise ValueError('Status must be either active or inactive')
        return v

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    course: Optional[str] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['active', 'inactive']:
            raise ValueError('Status must be either active or inactive')
        return v

class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    course: str
    status: str
    created_at: datetime

# Create router with /api prefix
api_router = APIRouter(prefix="/api")

# Auth Routes
@api_router.post("/auth/register")
async def register(user: RegisterRequest, response: Response):
    email_lower = user.email.lower()
    
    # Check if user exists
    existing = await db.users.find_one({"email": email_lower})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed = hash_password(user.password)
    user_doc = {
        "email": email_lower,
        "password_hash": hashed,
        "name": user.name,
        "role": "user",
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Create tokens
    access_token = create_access_token(user_id, email_lower)
    refresh_token = create_refresh_token(user_id)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "_id": user_id,
        "email": email_lower,
        "name": user.name,
        "role": "user",
        "created_at": user_doc["created_at"]
    }

@api_router.post("/auth/login")
async def login(credentials: LoginRequest, response: Response):
    email_lower = credentials.email.lower()
    
    # Find user
    user = await db.users.find_one({"email": email_lower})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(user["_id"])
    
    # Create tokens
    access_token = create_access_token(user_id, email_lower)
    refresh_token = create_refresh_token(user_id)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {
        "_id": user_id,
        "email": email_lower,
        "name": user.get("name", ""),
        "role": user.get("role", "user"),
        "created_at": user.get("created_at")
    }

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out successfully"}

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

# Student Routes
@api_router.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, current_user: dict = Depends(get_current_user)):
    # Check if email already exists
    existing = await db.students.find_one({"email": student.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    student_doc = {
        "name": student.name,
        "email": student.email.lower(),
        "course": student.course,
        "status": student.status,
        "created_at": datetime.now(timezone.utc)
    }
    
    result = await db.students.insert_one(student_doc)
    student_doc["id"] = str(result.inserted_id)
    
    return student_doc

@api_router.get("/students")
async def get_students(
    current_user: dict = Depends(get_current_user),
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    query = {}
    
    # Search by name or email
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"course": {"$regex": search, "$options": "i"}}
        ]
    
    # Filter by status
    if status and status in ['active', 'inactive']:
        query["status"] = status
    
    # Get total count
    total = await db.students.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * limit
    students_cursor = db.students.find(query).skip(skip).limit(limit).sort("created_at", -1)
    students = await students_cursor.to_list(length=limit)
    
    # Transform students
    for student in students:
        student["id"] = str(student["_id"])
        del student["_id"]
    
    return {
        "students": students,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, current_user: dict = Depends(get_current_user)):
    try:
        student = await db.students.find_one({"_id": ObjectId(student_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid student ID")
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student["id"] = str(student["_id"])
    del student["_id"]
    
    return student

@api_router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid student ID")
    
    # Check if student exists
    existing = await db.students.find_one({"_id": obj_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Build update dict
    update_data = {k: v for k, v in student_update.dict(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Check email uniqueness if email is being updated
    if "email" in update_data:
        email_lower = update_data["email"].lower()
        email_exists = await db.students.find_one({
            "email": email_lower,
            "_id": {"$ne": obj_id}
        })
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already exists")
        update_data["email"] = email_lower
    
    # Update student
    await db.students.update_one({"_id": obj_id}, {"$set": update_data})
    
    # Get updated student
    updated_student = await db.students.find_one({"_id": obj_id})
    updated_student["id"] = str(updated_student["_id"])
    del updated_student["_id"]
    
    return updated_student

@api_router.delete("/students/{student_id}")
async def delete_student(student_id: str, current_user: dict = Depends(get_current_user)):
    try:
        obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid student ID")
    
    result = await db.students.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.students.create_index("email", unique=True)
    
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    existing_admin = await db.users.find_one({"email": admin_email})
    if existing_admin is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hashed,
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.now(timezone.utc)
        })
    elif not verify_password(admin_password, existing_admin["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
