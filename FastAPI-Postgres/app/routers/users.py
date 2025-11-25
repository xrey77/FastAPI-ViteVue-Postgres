import os
import io
import math
import json
import pyotp
import qrcode
import base64
from fastapi import File, APIRouter, UploadFile, Request, Response, Depends, HTTPException
from PIL import Image
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlalchemy.future import select
from fastapi_pagination import Page, paginate, LimitOffsetPage
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from app.utils.hashing import Hasher
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import List, Dict
from app.models.model import Users
from app.schemas.user import UserSchema
from sqlalchemy.orm import Session
from app.connection.db import get_db

router = APIRouter(prefix="/api", tags=["api"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/getuserid/{id}/")
async def getuserid(id: int, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    user = db.query(Users).filter(Users.id == id).first()    
    if user is not None:    
        return {
            "id": user.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "email": user.email,
            "mobile": user.mobile,
            "username": user.username,
            "qrcodeurl": user.qrcodeurl,
            "userpic": user.userpic
        }
    else:
        return JSONResponse(
        status_code=404,
        content={"message": 'No record(s) found.'},
        )
                
@router.get("/getallusers/{page}/")
def get_users(page: int, token: Annotated[str, Depends(oauth2_scheme)] ,db: Session = Depends(get_db)):
    try:
        perpage = 5
        offset = math.ceil((page - 1) * perpage)
        totalrecs = db.query(Users).count()
        totalpage = math.ceil(totalrecs / perpage)
        users = db.query(Users).offset(offset).limit(perpage).all()    
        return {"page": page, "totpage": totalpage, "totalrecords": totalrecs, "users": users}    
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'No record(s) found.'},
        )
        
@router.patch("/updateprofile/{id}/")
async def updateProfile(id: int, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    fname = data["firstname"]
    lname = data["lastname"]
    mobile = data["mobile"]
    try:
        user = db.query(Users).filter(Users.id == id).first()
        if user is not None:
            user.lastname = lname
            user.firstname = fname    
            user.mobile = mobile
            db.commit()    
            return {"message": "Your Profile Updated Successfully.."}
        else:
            return JSONResponse(
            status_code=404,
            content={"message": 'User record found.'},
            )
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'Error! unable to update profile.'},
        )
                        
@router.patch("/changepassword/{id}/")
async def changePassword(id: int, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    try:
        data = await request.json()
        passwd = data["password"]    
        user = db.query(Users).filter(Users.id == id).first()
        if user is not None:
            hash = Hasher.get_password_hash(passwd)
            user.password = hash
            db.commit()
            return {"message": "You have changed your password Successfully.."}            
        else:
            return JSONResponse(
            status_code=404,
            content={"message": 'User record found.'},
            )
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'Error! unable to change password.'},
        )

@router.patch("/uploadpicture/{id}/")
async def userprofilepic(id: int, userpic: UploadFile = File(), db: Session = Depends(get_db)) -> dict:
    img = Image.open(userpic.file)
    ext = "." + img.format

    MAX_SIZE = (100, 100) 
    img.thumbnail(MAX_SIZE)
    path =  "static/users/"
    newfile = "00"+str(id) +  ext
    try:
     os.remove("static/users/00"+str(id)+ext)
    except Exception:
        print(None)
        
    final_filepath = os.path.join(path, newfile)
    img.save(final_filepath)
    urlimg ="/users/"+newfile
    user = db.query(Users).filter(Users.id == int(id)).first()
    if user:
        user.userpic = urlimg
        db.commit()    
        return {"userpic": urlimg, "message": "You have changed your profile pictuer successfully."}
    else:
        return JSONResponse(
        status_code=404,
        content={"message": 'Error! unable to upate your profile.'},
        )
        
                        
@router.patch("/mfa/activate/{id}/")
async def enableMfa(id: int, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    if data["TwoFactorEnabled"]:
        
        user = db.query(Users).filter(Users.id == id).first()
        if user is not None:
            email = user.email
            pytopsecret = pyotp.random_base32()
            fullname = user.firstname + " " + user.lastname
            provisioning_uri = pyotp.totp.TOTP(pytopsecret).provisioning_uri(name=email, issuer_name="SUPERCARS INC.")

            img = qrcode.make(provisioning_uri)            
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()
            qrcodeb64 = base64.b64encode(img_bytes)

            user.secret = pytopsecret
            user.qrcodeurl = qrcodeb64
            db.commit()                
        
        return {
        'qrcodeurl': qrcodeb64 ,
        'message': 'Multi-Factor has been enabled.'}                    
        
    else:

        user = db.query(Users).filter(Users.id == id).first()
        if user is not None:
            user.qrcodeurl = None
            db.commit()

        return {
        'message': 'Multi-Factor has been disabled.'}
                    
@router.patch("/mfa/verifytotp/{id}/")
async def verifyMfa(id: int, request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    otp = int(data["otp"])
    try:    
        user = db.query(Users).filter(Users.id == id).first()        
        if user is not None:
            token = otp
            totp = pyotp.TOTP(user.secret)
            isOk = totp.verify(token)        
            if isOk:
                return {'statuscode': 200, 'message': 'OTP validation is successful.','username': user.username}
            else:        
                return JSONResponse(
                status_code=404,
                content={"message": 'Invalid OTP code..'},
                )
            
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'Error! OTP code validation problem.'},
        )
    
            
    
    
