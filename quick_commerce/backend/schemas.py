from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime
from .models import UserRole, OrderStatus, DeliveryType

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    password: constr(min_length=8)
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None

class UserUpdate(BaseModel):
    medical_conditions: Optional[str] = None
    allergies: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserOut(UserBase):
    id: int
    role: UserRole
    phone_verified: bool
    is_active: bool
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class PhoneVerification(BaseModel):
    phone: str
    verification_code: str

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Medicine Schemas
class MedicineBase(BaseModel):
    name: str
    generic_name: Optional[str] = None
    description: Optional[str] = None
    category_id: int
    price: float
    stock_quantity: int
    prescription_required: bool
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    delivery_time_minutes: int = 30

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    name: Optional[str] = None
    generic_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    prescription_required: Optional[bool] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    delivery_time_minutes: Optional[int] = None
    is_available: Optional[bool] = None

class MedicineOut(MedicineBase):
    id: int
    is_available: bool
    expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: CategoryOut

    class Config:
        from_attributes = True

class MedicineSearch(BaseModel):
    q: Optional[str] = None
    category_id: Optional[int] = None
    prescription_required: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    medicine_id: int
    quantity: int
    unit_price: float
    total_price: float
    prescription_id: Optional[int] = None
    medicine: MedicineOut

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus    

class StockUpdate(BaseModel):
    stock_quantity: int

# Prescription Schemas
class PrescriptionBase(BaseModel):
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    prescription_date: Optional[datetime] = None

class PrescriptionCreate(PrescriptionBase):
    pass

class PrescriptionOut(PrescriptionBase):
    id: int
    user_id: int
    image_url: str
    is_verified: bool
    verified_by: Optional[int] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PrescriptionVerification(BaseModel):
    is_verified: bool
    verification_notes: Optional[str] = None

# Cart Schemas
class CartItemBase(BaseModel):
    medicine_id: int
    quantity: int
    prescription_id: Optional[int] = None

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemOut(CartItemBase):
    id: int
    user_id: int
    medicine: MedicineOut
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CartOut(BaseModel):
    items: List[CartItemOut]
    total_items: int
    total_amount: float

# Order Schemas
class OrderCreate(BaseModel):
    delivery_address: str
    delivery_city: str
    delivery_pincode: str
    delivery_latitude: Optional[float] = None
    delivery_longitude: Optional[float] = None
    delivery_type: DeliveryType = DeliveryType.STANDARD

class OrderOut(BaseModel):
    id: int
    order_number: str
    user_id: int
    total_amount: float
    delivery_fee: float
    tax_amount: float
    delivery_address: str
    delivery_city: str
    delivery_pincode: str
    status: OrderStatus
    delivery_type: DeliveryType
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    delivery_partner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List['OrderItemOut']

    class Config:
        from_attributes = True



class DeliveryProof(BaseModel):
    proof_url: str

# Delivery Schemas
class DeliveryEstimate(BaseModel):
    delivery_address: str
    delivery_city: str
    delivery_pincode: str
    delivery_type: DeliveryType = DeliveryType.STANDARD

class DeliveryEstimateOut(BaseModel):
    estimated_time_minutes: int
    delivery_fee: float
    available_partners: int

class EmergencyDelivery(BaseModel):
    medicine_ids: List[int]
    delivery_address: str
    delivery_city: str
    delivery_pincode: str
    urgency_level: str  # high, medium, low

class NearbyPharmacy(BaseModel):
    id: int
    name: str
    address: str
    distance_km: float
    available_medicines: int
    estimated_delivery_time: int

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 