from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(200))
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(10))
    role = Column(String(20), default="user")
    membership = Column(String(20), default="bronze")
    membership_expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    locations = relationship("Location", back_populates="user")
    bomber_logs = relationship("BomberLog", back_populates="user")
    search_logs = relationship("SearchLog", back_populates="user")
    daily_usage = relationship("DailyUsage", back_populates="user")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    ip_address = Column(String(50))
    browser_info = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="locations")

class BomberLog(Base):
    __tablename__ = "bomber_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_phone = Column(String(20))
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    total_requests = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="bomber_logs")

class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    search_phone = Column(String(20))
    result_found = Column(Boolean, default=False)
    result_data = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="search_logs")

class ScrapedData(Base):
    __tablename__ = "scraped_data"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50))
    ad_id = Column(String(100))
    title = Column(String(500))
    phone = Column(String(20))
    price = Column(String(100))
    link = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)

class MembershipPlan(Base):
    __tablename__ = "membership_plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    daily_bomber_limit = Column(Integer, default=50)
    daily_search_limit = Column(Integer, default=20)
    monthly_price = Column(Float, default=0)
    color = Column(String(20), default="#cd7f32")

class ServiceStatus(Base):
    __tablename__ = "service_status"
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(50), unique=True)
    is_online = Column(Boolean, default=True)
    last_check = Column(DateTime, default=datetime.now)
    response_time = Column(Integer, default=0)

class DailyUsage(Base):
    __tablename__ = "daily_usage"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String(10), default=datetime.now().strftime("%Y-%m-%d"))
    bomber_used = Column(Integer, default=0)
    search_used = Column(Integer, default=0)
    location_used = Column(Integer, default=0)
    
    user = relationship("User", back_populates="daily_usage")