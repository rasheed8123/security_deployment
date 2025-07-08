from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from . import models, schemas, auth
from .models import UserRole, OrderStatus, DeliveryType

# User CRUD operations
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        medical_conditions=user.medical_conditions,
        allergies=user.allergies,
        emergency_contact=user.emergency_contact,
        address=user.address,
        city=user.city,
        state=user.state,
        pincode=user.pincode
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def verify_phone(db: Session, phone: str, verification_code: str):
    # In a real app, you'd verify against stored code
    # For demo, accept any 6-digit code
    if len(verification_code) == 6 and verification_code.isdigit():
        user = get_user_by_phone(db, phone)
        if user:
            user.phone_verified = True
            db.commit()
            return user
    return None

# Category CRUD operations
def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int):
    return db.query(models.Category).filter(models.Category.id == category_id).first()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, category: schemas.CategoryUpdate):
    db_category = get_category(db, category_id)
    if db_category:
        for field, value in category.dict(exclude_unset=True).items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

# Medicine CRUD operations
def get_medicines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Medicine).filter(models.Medicine.is_available == True).offset(skip).limit(limit).all()

def get_medicine(db: Session, medicine_id: int):
    return db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()

def search_medicines(db: Session, search_params: schemas.MedicineSearch):
    query = db.query(models.Medicine).filter(models.Medicine.is_available == True)
    
    if search_params.q:
        query = query.filter(
            or_(
                models.Medicine.name.contains(search_params.q),
                models.Medicine.generic_name.contains(search_params.q),
                models.Medicine.description.contains(search_params.q)
            )
        )
    
    if search_params.category_id:
        query = query.filter(models.Medicine.category_id == search_params.category_id)
    
    if search_params.prescription_required is not None:
        query = query.filter(models.Medicine.prescription_required == search_params.prescription_required)
    
    if search_params.min_price:
        query = query.filter(models.Medicine.price >= search_params.min_price)
    
    if search_params.max_price:
        query = query.filter(models.Medicine.price <= search_params.max_price)
    
    return query.all()

def create_medicine(db: Session, medicine: schemas.MedicineCreate):
    db_medicine = models.Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

def update_medicine(db: Session, medicine_id: int, medicine: schemas.MedicineUpdate):
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        for field, value in medicine.dict(exclude_unset=True).items():
            setattr(db_medicine, field, value)
        db.commit()
        db.refresh(db_medicine)
    return db_medicine

def update_medicine_stock(db: Session, medicine_id: int, stock_update: schemas.StockUpdate):
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        db_medicine.stock_quantity = stock_update.stock_quantity
        db_medicine.is_available = stock_update.stock_quantity > 0
        db.commit()
        db.refresh(db_medicine)
    return db_medicine

def delete_medicine(db: Session, medicine_id: int):
    db_medicine = get_medicine(db, medicine_id)
    if db_medicine:
        db.delete(db_medicine)
        db.commit()
    return db_medicine

def get_alternative_medicines(db: Session, medicine_id: int):
    medicine = get_medicine(db, medicine_id)
    if medicine:
        return db.query(models.Medicine).filter(
            and_(
                models.Medicine.category_id == medicine.category_id,
                models.Medicine.id != medicine_id,
                models.Medicine.is_available == True
            )
        ).all()
    return []

# Prescription CRUD operations
def create_prescription(db: Session, user_id: int, prescription: schemas.PrescriptionCreate, image_url: str):
    db_prescription = models.Prescription(
        user_id=user_id,
        image_url=image_url,
        **prescription.dict()
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def get_user_prescriptions(db: Session, user_id: int):
    return db.query(models.Prescription).filter(models.Prescription.user_id == user_id).all()

def get_prescription(db: Session, prescription_id: int):
    return db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()

def verify_prescription(db: Session, prescription_id: int, verification: schemas.PrescriptionVerification, verified_by: int):
    db_prescription = get_prescription(db, prescription_id)
    if db_prescription:
        db_prescription.is_verified = verification.is_verified
        db_prescription.verified_by = verified_by
        db_prescription.verification_notes = verification.verification_notes
        db.commit()
        db.refresh(db_prescription)
    return db_prescription

# Cart CRUD operations
def get_user_cart(db: Session, user_id: int):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    total_amount = sum(item.quantity * item.medicine.price for item in cart_items)
    return {
        "items": cart_items,
        "total_items": len(cart_items),
        "total_amount": total_amount
    }

def add_to_cart(db: Session, user_id: int, cart_item: schemas.CartItemCreate):
    # Check if item already exists in cart
    existing_item = db.query(models.CartItem).filter(
        and_(
            models.CartItem.user_id == user_id,
            models.CartItem.medicine_id == cart_item.medicine_id
        )
    ).first()
    
    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        db_cart_item = models.CartItem(
            user_id=user_id,
            **cart_item.dict()
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def update_cart_item(db: Session, cart_item_id: int, user_id: int, quantity: int):
    db_cart_item = db.query(models.CartItem).filter(
        and_(
            models.CartItem.id == cart_item_id,
            models.CartItem.user_id == user_id
        )
    ).first()
    
    if db_cart_item:
        db_cart_item.quantity = quantity
        db.commit()
        db.refresh(db_cart_item)
    return db_cart_item

def remove_from_cart(db: Session, cart_item_id: int, user_id: int):
    db_cart_item = db.query(models.CartItem).filter(
        and_(
            models.CartItem.id == cart_item_id,
            models.CartItem.user_id == user_id
        )
    ).first()
    
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item

def clear_cart(db: Session, user_id: int):
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()

# Order CRUD operations
def create_order(db: Session, user_id: int, order_data: schemas.OrderCreate):
    # Get user's cart
    cart = get_user_cart(db, user_id)
    if not cart["items"]:
        return None
    
    # Generate order number
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Calculate totals
    subtotal = cart["total_amount"]
    delivery_fee = 50.0 if order_data.delivery_type == DeliveryType.STANDARD else 100.0
    tax_amount = subtotal * 0.18  # 18% GST
    total_amount = subtotal + delivery_fee + tax_amount
    
    # Create order
    db_order = models.Order(
        user_id=user_id,
        order_number=order_number,
        total_amount=total_amount,
        delivery_fee=delivery_fee,
        tax_amount=tax_amount,
        delivery_address=order_data.delivery_address,
        delivery_city=order_data.delivery_city,
        delivery_pincode=order_data.delivery_pincode,
        delivery_latitude=order_data.delivery_latitude,
        delivery_longitude=order_data.delivery_longitude,
        delivery_type=order_data.delivery_type,
        estimated_delivery_time=datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Create order items
    for cart_item in cart["items"]:
        order_item = models.OrderItem(
            order_id=db_order.id,
            medicine_id=cart_item.medicine_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.medicine.price,
            total_price=cart_item.quantity * cart_item.medicine.price,
            prescription_id=cart_item.prescription_id
        )
        db.add(order_item)
        
        # Update medicine stock
        medicine = cart_item.medicine
        medicine.stock_quantity -= cart_item.quantity
        if medicine.stock_quantity <= 0:
            medicine.is_available = False
    
    db.commit()
    
    # Clear cart
    clear_cart(db, user_id)
    
    return db_order

def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def update_order_status(db: Session, order_id: int, status: OrderStatus):
    db_order = get_order(db, order_id)
    if db_order:
        db_order.status = status
        if status == OrderStatus.DELIVERED:
            db_order.actual_delivery_time = datetime.utcnow()
        db.commit()
        db.refresh(db_order)
    return db_order

def upload_delivery_proof(db: Session, order_id: int, proof_url: str):
    db_order = get_order(db, order_id)
    if db_order:
        db_order.delivery_proof_url = proof_url
        db.commit()
        db.refresh(db_order)
    return db_order

# Delivery CRUD operations
def get_delivery_estimate(db: Session, estimate_data: schemas.DeliveryEstimate):
    # Mock delivery estimation
    base_time = 30 if estimate_data.delivery_type == DeliveryType.STANDARD else 15
    delivery_fee = 50.0 if estimate_data.delivery_type == DeliveryType.STANDARD else 100.0
    
    return {
        "estimated_time_minutes": base_time,
        "delivery_fee": delivery_fee,
        "available_partners": 5  # Mock data
    }

def get_nearby_pharmacies(db: Session, latitude: float, longitude: float, radius_km: float = 5.0):
    # Mock nearby pharmacies
    pharmacies = [
        {
            "id": 1,
            "name": "City Pharmacy",
            "address": "123 Main St, City Center",
            "distance_km": 1.2,
            "available_medicines": 150,
            "estimated_delivery_time": 25
        },
        {
            "id": 2,
            "name": "Health Plus Pharmacy",
            "address": "456 Oak Ave, Downtown",
            "distance_km": 2.8,
            "available_medicines": 200,
            "estimated_delivery_time": 35
        }
    ]
    return [p for p in pharmacies if p["distance_km"] <= radius_km]

def create_emergency_delivery(db: Session, user_id: int, emergency_data: schemas.EmergencyDelivery):
    # Create emergency order with priority
    order_data = schemas.OrderCreate(
        delivery_address=emergency_data.delivery_address,
        delivery_city=emergency_data.delivery_city,
        delivery_pincode=emergency_data.delivery_pincode,
        delivery_type=DeliveryType.EMERGENCY
    )
    
    # For emergency, we'd create a special order with priority
    return create_order(db, user_id, order_data) 