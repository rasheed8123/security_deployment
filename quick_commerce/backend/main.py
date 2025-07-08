from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from . import crud, schemas, auth, models
from .database import engine, get_db
from .dependencies import get_current_active_user, require_pharmacy_admin, require_pharmacist, require_delivery_partner

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quick Commerce Medicine Delivery API",
    description="A comprehensive medicine delivery platform with quick commerce features",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Authentication endpoints
@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_phone(db, user.phone):
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    return crud.create_user(db, user)

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    return current_user

@app.put("/auth/profile", response_model=schemas.UserOut)
def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.update_user(db, current_user.id, user_update)

@app.post("/auth/verify-phone")
def verify_phone(verification: schemas.PhoneVerification, db: Session = Depends(get_db)):
    user = crud.verify_phone(db, verification.phone, verification.verification_code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    return {"message": "Phone number verified successfully"}

# Medicine endpoints
@app.get("/medicines", response_model=List[schemas.MedicineOut])
def get_medicines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_medicines(db, skip=skip, limit=limit)

@app.get("/medicines/search", response_model=List[schemas.MedicineOut])
def search_medicines(
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    prescription_required: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    search_params = schemas.MedicineSearch(
        q=q,
        category_id=category_id,
        prescription_required=prescription_required,
        min_price=min_price,
        max_price=max_price
    )
    return crud.search_medicines(db, search_params)

@app.get("/medicines/{medicine_id}", response_model=schemas.MedicineOut)
def get_medicine(medicine_id: int, db: Session = Depends(get_db)):
    medicine = crud.get_medicine(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@app.get("/medicines/{medicine_id}/alternatives", response_model=List[schemas.MedicineOut])
def get_alternative_medicines(medicine_id: int, db: Session = Depends(get_db)):
    return crud.get_alternative_medicines(db, medicine_id)

@app.post("/medicines", response_model=schemas.MedicineOut)
def create_medicine(
    medicine: schemas.MedicineCreate,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    return crud.create_medicine(db, medicine)

@app.put("/medicines/{medicine_id}", response_model=schemas.MedicineOut)
def update_medicine(
    medicine_id: int,
    medicine: schemas.MedicineUpdate,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    updated_medicine = crud.update_medicine(db, medicine_id, medicine)
    if not updated_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return updated_medicine

@app.patch("/medicines/{medicine_id}/stock", response_model=schemas.MedicineOut)
def update_medicine_stock(
    medicine_id: int,
    stock_update: schemas.StockUpdate,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    updated_medicine = crud.update_medicine_stock(db, medicine_id, stock_update)
    if not updated_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return updated_medicine

@app.delete("/medicines/{medicine_id}")
def delete_medicine(
    medicine_id: int,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    medicine = crud.delete_medicine(db, medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return {"message": "Medicine deleted successfully"}

# Category endpoints
@app.get("/categories", response_model=List[schemas.CategoryOut])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@app.get("/categories/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.post("/categories", response_model=schemas.CategoryOut)
def create_category(
    category: schemas.CategoryCreate,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    return crud.create_category(db, category)

@app.put("/categories/{category_id}", response_model=schemas.CategoryOut)
def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    updated_category = crud.update_category(db, category_id, category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@app.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    current_user: models.User = Depends(require_pharmacy_admin),
    db: Session = Depends(get_db)
):
    category = crud.delete_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Prescription endpoints
@app.post("/prescriptions/upload", response_model=schemas.PrescriptionOut)
def upload_prescription(
    file: UploadFile = File(...),
    doctor_name: Optional[str] = Form(None),
    hospital_name: Optional[str] = Form(None),
    prescription_date: Optional[str] = Form(None),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"prescription_{current_user.id}_{datetime.now().timestamp()}.jpg")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    prescription_data = schemas.PrescriptionCreate(
        doctor_name=doctor_name,
        hospital_name=hospital_name,
        prescription_date=datetime.fromisoformat(prescription_date) if prescription_date else None
    )
    
    return crud.create_prescription(db, current_user.id, prescription_data, file_path)

@app.get("/prescriptions", response_model=List[schemas.PrescriptionOut])
def get_user_prescriptions(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_prescriptions(db, current_user.id)

@app.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionOut)
def get_prescription(
    prescription_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    prescription = crud.get_prescription(db, prescription_id)
    if not prescription or prescription.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@app.put("/prescriptions/{prescription_id}/verify", response_model=schemas.PrescriptionOut)
def verify_prescription(
    prescription_id: int,
    verification: schemas.PrescriptionVerification,
    current_user: models.User = Depends(require_pharmacist),
    db: Session = Depends(get_db)
):
    prescription = crud.verify_prescription(db, prescription_id, verification, current_user.id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

# Cart endpoints
@app.get("/cart", response_model=schemas.CartOut)
def get_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_cart(db, current_user.id)

@app.post("/cart/items", response_model=schemas.CartItemOut)
def add_to_cart(
    cart_item: schemas.CartItemCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.add_to_cart(db, current_user.id, cart_item)

@app.put("/cart/items/{cart_item_id}", response_model=schemas.CartItemOut)
def update_cart_item(
    cart_item_id: int,
    quantity: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    cart_item = crud.update_cart_item(db, cart_item_id, current_user.id, quantity)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item

@app.delete("/cart/items/{cart_item_id}")
def remove_from_cart(
    cart_item_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    cart_item = crud.remove_from_cart(db, cart_item_id, current_user.id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}

@app.delete("/cart")
def clear_cart(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    crud.clear_cart(db, current_user.id)
    return {"message": "Cart cleared"}

# Order endpoints
@app.post("/orders", response_model=schemas.OrderOut)
def create_order(
    order_data: schemas.OrderCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    order = crud.create_order(db, current_user.id, order_data)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot create order with empty cart")
    return order

@app.get("/orders", response_model=List[schemas.OrderOut])
def get_user_orders(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_orders(db, current_user.id)

@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    order = crud.get_order(db, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.patch("/orders/{order_id}/status", response_model=schemas.OrderOut)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    current_user: models.User = Depends(require_delivery_partner),
    db: Session = Depends(get_db)
):
    order = crud.update_order_status(db, order_id, status_update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders/{order_id}/delivery-proof")
def upload_delivery_proof(
    order_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_delivery_partner),
    db: Session = Depends(get_db)
):
    # Save delivery proof image
    file_path = os.path.join(UPLOAD_DIR, f"delivery_proof_{order_id}_{datetime.now().timestamp()}.jpg")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    order = crud.upload_delivery_proof(db, order_id, file_path)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Delivery proof uploaded successfully"}

# Delivery endpoints
@app.get("/delivery/estimate", response_model=schemas.DeliveryEstimateOut)
def get_delivery_estimate(
    delivery_address: str,
    delivery_city: str,
    delivery_pincode: str,
    delivery_type: schemas.DeliveryType = schemas.DeliveryType.STANDARD,
    db: Session = Depends(get_db)
):
    estimate_data = schemas.DeliveryEstimate(
        delivery_address=delivery_address,
        delivery_city=delivery_city,
        delivery_pincode=delivery_pincode,
        delivery_type=delivery_type
    )
    return crud.get_delivery_estimate(db, estimate_data)

@app.get("/nearby-pharmacies", response_model=List[schemas.NearbyPharmacy])
def get_nearby_pharmacies(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db)
):
    return crud.get_nearby_pharmacies(db, latitude, longitude, radius_km)

@app.post("/delivery/emergency", response_model=schemas.OrderOut)
def create_emergency_delivery(
    emergency_data: schemas.EmergencyDelivery,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    order = crud.create_emergency_delivery(db, current_user.id, emergency_data)
    if not order:
        raise HTTPException(status_code=400, detail="Cannot create emergency delivery")
    return order

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()} 