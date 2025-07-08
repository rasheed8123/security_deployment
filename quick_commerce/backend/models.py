from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    PHARMACY_ADMIN = "pharmacy_admin"
    PHARMACIST = "pharmacist"
    DELIVERY_PARTNER = "delivery_partner"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryType(str, enum.Enum):
    STANDARD = "standard"
    EMERGENCY = "emergency"
    EXPRESS = "express"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    # Medical profile
    medical_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    
    # Delivery address
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Verification
    phone_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    prescriptions = relationship("Prescription", foreign_keys="Prescription.user_id", back_populates="user")
    verified_prescriptions = relationship("Prescription", foreign_keys="Prescription.verified_by")
    cart_items = relationship("CartItem", back_populates="user")
    orders = relationship("Order", foreign_keys="Order.user_id", back_populates="user")
    delivery_orders = relationship("Order", foreign_keys="Order.delivery_partner_id")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    medicines = relationship("Medicine", back_populates="category")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    generic_name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Pricing and stock
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    prescription_required = Column(Boolean, default=False, nullable=False)
    
    # Medicine details
    dosage_form = Column(String, nullable=True)  # tablet, syrup, etc.
    strength = Column(String, nullable=True)     # 500mg, 10ml, etc.
    manufacturer = Column(String, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Quick commerce specific
    delivery_time_minutes = Column(Integer, default=30, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="medicines")
    cart_items = relationship("CartItem", back_populates="medicine")
    order_items = relationship("OrderItem", back_populates="medicine")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Prescription details
    image_url = Column(String, nullable=False)
    doctor_name = Column(String, nullable=True)
    hospital_name = Column(String, nullable=True)
    prescription_date = Column(DateTime, nullable=True)
    
    # Status
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="prescriptions")
    verifier = relationship("User", foreign_keys=[verified_by], overlaps="verified_prescriptions")
    medicines = relationship("PrescriptionMedicine", back_populates="prescription")

class PrescriptionMedicine(Base):
    __tablename__ = "prescription_medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    
    # Prescription details
    dosage = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    
    # Relationships
    prescription = relationship("Prescription", back_populates="medicines")
    medicine = relationship("Medicine")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    
    quantity = Column(Integer, default=1, nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    medicine = relationship("Medicine", back_populates="cart_items")
    prescription = relationship("Prescription")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order details
    order_number = Column(String, unique=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    
    # Delivery details
    delivery_address = Column(Text, nullable=False)
    delivery_city = Column(String, nullable=False)
    delivery_pincode = Column(String, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    
    # Status and timing
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    delivery_type = Column(Enum(DeliveryType), default=DeliveryType.STANDARD, nullable=False)
    estimated_delivery_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    
    # Delivery partner
    delivery_partner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_proof_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    delivery_partner = relationship("User", foreign_keys=[delivery_partner_id], overlaps="delivery_orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    medicine = relationship("Medicine", back_populates="order_items")
    prescription = relationship("Prescription")

class DeliveryPartner(Base):
    __tablename__ = "delivery_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Partner details
    vehicle_number = Column(String, nullable=True)
    vehicle_type = Column(String, nullable=True)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    
    # Status
    is_available = Column(Boolean, default=True, nullable=False)
    current_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    current_order = relationship("Order") 