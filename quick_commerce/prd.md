Quick Commerce Medicine Delivery Application
Requirements
Create a complete, quick commerce medicine delivery platform with user authentication, medicine catalog management, prescription handling, and rapid delivery functionality.

Full API Endpoints
Authentication & Users:
POST /auth/register - Register new user with medical profile
POST /auth/login - User login
GET /auth/me - Get current user profile
PUT /auth/profile - Update user profile and delivery address
POST /auth/verify-phone - Verify phone number for delivery
Medicines (Public & Pharmacy Admin):
GET /medicines - Get all medicines with availability and pricing
POST /medicines - Add new medicine (pharmacy admin only)
PUT /medicines/{id} - Update medicine details (pharmacy admin only)
DELETE /medicines/{id} - Remove medicine (pharmacy admin only)
GET /medicines/search?q=term&category=id&prescription_required=true&min_price=50
GET /medicines/{id}/alternatives - Get alternative medicines for the same condition
PATCH /medicines/{id}/stock - Update medicine stock levels
Medicine Categories:
GET /categories - Get all medicine categories (Pain Relief, Antibiotics, etc.)
POST /categories - Create new category (pharmacy admin)
PUT /categories/{id} - Update category (pharmacy admin)
DELETE /categories/{id} - Delete category (pharmacy admin)
Prescriptions:
POST /prescriptions/upload - Upload prescription image
GET /prescriptions - Get user's prescriptions
GET /prescriptions/{id} - Get specific prescription details
PUT /prescriptions/{id}/verify - Verify prescription (pharmacist only)
GET /prescriptions/{id}/medicines - Get medicines from prescription
Shopping Cart (User only):
GET /cart - Get user's cart with prescription validation
POST /cart/items - Add medicine to cart
PUT /cart/items/{id} - Update cart item quantity
DELETE /cart/items/{id} - Remove medicine from cart
DELETE /cart - Clear entire cart
POST /cart/validate-prescriptions - Validate prescription medicines in cart
Orders & Delivery:
POST /orders - Create order from cart with delivery details
GET /orders - Get user's orders with delivery status
GET /orders/{id} - Get specific order details
PATCH /orders/{id}/status - Update order status (pharmacy/delivery partner)
GET /orders/{id}/track - Real-time order tracking
POST /orders/{id}/delivery-proof - Upload delivery confirmation
Quick Delivery Features:
GET /delivery/estimate - Get delivery time estimate
GET /delivery/partners - Get available delivery partners
POST /delivery/emergency - Create emergency medicine delivery request
GET /nearby-pharmacies - Find nearby pharmacies with stock
Quick Commerce Specific:
10-30 minute delivery promise
Real-time inventory tracking
Dynamic pricing based on urgency
Location-based medicine availability
Delivery partner optimization
Design & UX
Optimized for quick medicine ordering
Accessibility features for elderly users
Error handling with clear medical guidance
Push notifications for delivery updates and medicine reminders