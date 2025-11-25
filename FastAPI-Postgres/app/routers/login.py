from dotenv import load_dotenv
import os
import time
import jwt
from fastapi import APIRouter
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from app.models.model import Users
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.utils.hashing import Hasher

load_dotenv() 
router = APIRouter(prefix="/api", tags=["api"])

@router.post("/signin/")
async def signin(request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    usrname = data['username']
    pwd = data['password']
    
    user = db.query(Users).filter(Users.username == usrname).first()
    if user:
        if Hasher.verify_password(pwd, user.password):
            
            payload = {
                "userid": user.email,
                "expires": time.time() + 28800000
            }
            
            JWTSECRET = os.getenv("JWT_SECRET")
            JWTALGORITHM = os.getenv("JWT_ALGORITHM")
                        
            token = jwt.encode(payload, JWTSECRET, algorithm=JWTALGORITHM)
            
            return { 
                'id': user.id,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'email': user.email,
                'username': user.username,
                'isactivated': user.isactivated,
                'userpic': user.userpic,
                'qrcodeurl': user.qrcodeurl,
                'roles': user.roles,
                'token': token,
                'message': 'Logged-in successfull.'
            }       
             
        else:
            return JSONResponse(
            status_code=404,
            content={"message": 'Invalid Password, please try again.'},
            )
                
    else:
        return JSONResponse(
        status_code=404,
        content={"message": 'Username not found, please register.'},
        )
    