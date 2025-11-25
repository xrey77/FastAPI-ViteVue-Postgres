import math
from fastapi import APIRouter
from fastapi import FastAPI, Request, Response, Depends
from typing import Dict
from app.models.model import Products
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi_pagination import Page, paginate, LimitOffsetPage,add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.connection.db import get_db

router = APIRouter(prefix="/api", tags=["api"])

@router.post("/addproduct/")
async def addproduct(request: Request, response: Response,db: Session = Depends(get_db)) -> dict:
    data = await request.json()
    txt_category = data['category']
    txt_descriptions = data['descriptions']
    txt_qty = data['qty']
    txt_unit = data['unit']
    txt_costprice = data['costprice']
    txt_sellprice = data['sellprice']
    txt_saleprice = data['saleprice']
    txt_productpicture = data['productpicture']
    txt_alertstocks = data['alertstocks']
    txt_criticalstocks = data['criticalstocks']
    
    findDescription = db.query(Products).filter(Products.descriptions == txt_descriptions).first()
    if findDescription is not None:
        return JSONResponse(
        status_code=404,
        content={"message": "Product Description is already exists."},
        )
    
    # INSERT RECORDS
    try:
        prods = Products(
            category=txt_category,
            descriptions=txt_descriptions,
            qty=txt_qty,
            unit=txt_unit,
            costprice=txt_costprice,
            sellprice=txt_sellprice,
            saleprice=txt_saleprice,
            productpicture=txt_productpicture,
            alertstocks=txt_alertstocks,
            criticalstocks=txt_criticalstocks)
        db.add(prods)
        db.commit()    
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": "Failed"},
        )
        
    return {
        'message': 'Product Created Successfully.'
    }

@router.get("/products/list/{page}/")
def productsList(page: int ,db: Session = Depends(get_db)):
    try:
        perpage = 5
        offset = math.ceil((page - 1) * perpage)
        totalrecs = db.query(Products).count()
        totalpage = math.ceil(totalrecs / perpage)
        users = db.query(Products).offset(offset).limit(perpage).all()    
        return {"page": page, "totpage": totalpage, "totalrecords": totalrecs, "products": users}    
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'No record(s) found.'},
        )
        
@router.get("/products/search/{page}/{keyword}/")
def productSearch(page: int, keyword: str, db: Session = Depends(get_db)):
    try:        
        search_term = keyword.lower() if keyword else None
        perpage = 5
        offset = math.ceil((page - 1) * perpage)
        search_pattern = f"%{search_term}%"                        
        
        totalrecs = db.query(Products).filter(func.lower(Products.descriptions).like(search_pattern)).count()
        if totalrecs == 0:
            return JSONResponse(
            status_code=404,
            content={"message": "Product not found."},
            )
        totalpage = math.ceil(totalrecs / perpage)      
        users = db.query(Products).filter(func.lower(Products.descriptions).like(search_pattern)).offset(offset).limit(perpage).all()
        return {"page": page, "totpage": totalpage, "totalrecords": totalrecs, "products": users}    
    except Exception:
        return JSONResponse(
        status_code=404,
        content={"message": 'No record(s) found.'},
        )

@router.delete("/deleteproduct/{id}/")
async def getuserbyid(id: int, db: Session = Depends(get_db)) -> dict:
   try:
      product = db.query(Products).filter(Products.id == id).first()
      if product is None:
          return { 'message': f"Product ID NO. {id} is not found"}
      else:
        db.query(Products).filter(Products.id == id).delete()
        db.commit()                
        return {"message": f"Product ID # {id} was Deleted successfully."}      
   except Exception as e:
        return {"statuscode": 404, "message": e}
            