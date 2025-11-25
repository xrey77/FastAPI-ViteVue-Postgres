from fastapi import APIRouter
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict
from sqlalchemy.orm import Session
from app.connection.db import get_db
from app.utils.hashing import Hasher
from app.models.model import Users

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/signup/")
async def signup(request: Request, response: Response, db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    pwd = data['password']
    hash = Hasher.get_password_hash(pwd)
    
    fname   = data['firstname']
    lname   = data['lastname']
    xemail   = data['email']
    mobile  = data['mobile']
    usrname = data['username']
    urlimg="/users/pix.png"
    
    try:    
        findEmail = db.query(Users).filter(Users.email == xemail).first()
        if findEmail is not None:
            return JSONResponse(
            status_code=404,
            content={"message": "Email Address has alredy taken."},
            )
    except Exception:
        print(None)
        # raise HTTPException(
        #     status_code=404, detail="Email Address has alredy taken."
        # )
    try:
        findUsername = db.query(Users).filter(Users.username == usrname).first()
        if findUsername is not None:
            return JSONResponse(
            status_code=404,
            content={"message": "Username has alredy taken."},
            )
    except Exception:
        print(None)        
        
    # INSERT RECORDS
    try:
        user = Users(
            firstname=fname,
            lastname=lname,
            email=xemail,
            mobile=mobile,
            username=usrname,
            password=hash,
            roles='ROLE_USER',
            isactivated=1,
            userpic=urlimg)
        db.add(user)
        db.commit()    
    except Exception as e:
        return JSONResponse(
        status_code=404,
        content={"message": e},
        )
            
    return {
        'message': 'Successful registration, please login now.'
    }