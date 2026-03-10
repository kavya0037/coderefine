import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uvicorn
import os

# Load env variables for API keys
load_dotenv()

from analyzer import analyze_code
from executor import extract_code_block, execute_code
from database import create_user, get_user, verify_password

# JWT configuration
SECRET_KEY = "super_secret_temporary_key_for_hackathon"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="AI Code Assistant API")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# Define request models
class UserAuth(BaseModel):
    username: str
    password: str

class AnalyzeRequest(BaseModel):
    code: str
    analysis_type: str
    language: str

# --- Authentication Endpoints ---

@app.post("/api/register")
async def register(user: UserAuth):
    success = create_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already registered")
    return {"message": "User registered successfully"}

@app.post("/api/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# API Endpoint for analysis
@app.post("/api/analyze")
async def perform_analysis(req: AnalyzeRequest, current_user: dict = Depends(get_current_user)):
    if not req.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty.")
        
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set on the server.")

    try:
        # Call the existing analyzer logic
        result = analyze_code(req.code, req.analysis_type, req.language)
        
        execution_output = None
        # Always attempt to extract and execute a code block if present
        extracted_code = extract_code_block(result, req.language)
        if extracted_code:
            execution_output = execute_code(extracted_code, req.language)
        
        return {
            "result": result,
            "execution_output": execution_output
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files directly. We mount the static directory to /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve front page
@app.get("/")
async def root():
    return FileResponse("static/index.html")

# Serve auth page
@app.get("/login")
async def login_page():
    return FileResponse("static/auth.html")

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
