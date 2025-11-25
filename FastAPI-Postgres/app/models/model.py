from datetime import datetime, time, timedelta
from sqlalchemy.types import String, Integer, Text, Numeric
from sqlalchemy import Column, func, Integer, String, Float, ForeignKey, Text, DateTime, TIMESTAMP
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Integer
from typing import Optional
from datetime import datetime
from app.connection.db import Base

class Users(Base):
    __tablename__ = "users"    
    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(20))
    lastname = Column(String(20))
    email = Column(String(20), unique=True)
    mobile = Column(String(20))
    username = Column(String(20), unique=True)
    password = Column(String(100))
    roles = Column(String(20))
    isactivated = Column(Integer, default=0, nullable=True)
    isblocked = Column(Integer, default=0, nullable=True)
    mailtoken = Column(Integer, default=0, nullable=True)
    secret = Column(Text())
    qrcodeurl = Column(Text())
    userpic = Column(String(100))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
class Products(Base):
    __tablename__ = "products"    
    id = Column(Integer, primary_key=True, index=True)    
    category = Column(String(100))
    descriptions = Column(String(100))
    qty = Column(Integer, default=0, nullable=True)
    unit = Column(String(20))    
    costprice = Column(Numeric(precision=10, scale=2)) 
    sellprice = Column(Numeric(precision=10, scale=2)) 
    saleprice = Column(Numeric(precision=10, scale=2))    
    productpicture = Column(String(100))
    alertstocks = Column(Integer, default=0, nullable=True)
    criticalstocks = Column(Integer, default=0, nullable=True)
    created_at =Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
