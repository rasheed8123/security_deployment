import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Quick Commerce Medicine Delivery",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .medicine-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-pending { background-color: #ffd700; color: #000; }
    .status-confirmed { background-color: #87ceeb; color: #000; }
    .status-preparing { background-color: #ffa500; color: #000; }
    .status-delivering { background-color: #ff6347; color: #fff; }
    .status-delivered { background-color: #32cd32; color: #fff; }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = []

# API helper functions
def api_request(method, endpoint, data=None, token=None):
    """Make API request with authentication"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Authentication functions
def login_user(username, password):
    """Login user and store token"""
    data = {"username": username, "password": password}
    response = api_request("POST", "/auth/login", data)
    if response:
        st.session_state.token = response["access_token"]
        user_info = api_request("GET", "/auth/me", token=st.session_state.token)
        if user_info:
            st.session_state.user = user_info
            st.success("Login successful!")
            return True
    return False

def register_user(user_data):
    """Register new user"""
    response = api_request("POST", "/auth/register", user_data)
    if response:
        st.success("Registration successful! Please login.")
        return True
    return False

def logout_user():
    """Logout user"""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.cart = []
    st.success("Logged out successfully!")

# Main navigation
def main_navigation():
    """Main navigation sidebar"""
    st.sidebar.title("💊 Quick Commerce")
    
    if st.session_state.token:
        st.sidebar.write(f"Welcome, {st.session_state.user['username']}!")
        st.sidebar.write(f"Role: {st.session_state.user['role']}")
        
        page = st.sidebar.selectbox(
            "Navigation",
            ["🏠 Dashboard", "💊 Medicines", "🛒 Cart", "📋 Orders", "📄 Prescriptions", "👤 Profile", "🚚 Delivery"]
        )
        
        if st.sidebar.button("Logout"):
            logout_user()
            st.rerun()
        
        return page
    else:
        st.sidebar.write("Please login to continue")
        return "Login"

# Dashboard page
def dashboard_page():
    """Main dashboard"""
    st.markdown('<h1 class="main-header">🏥 Quick Commerce Medicine Delivery</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Orders", "15")
        st.metric("Pending Deliveries", "3")
    
    with col2:
        st.metric("Available Medicines", "250+")
        st.metric("Delivery Partners", "12")
    
    with col3:
        st.metric("Average Delivery Time", "25 min")
        st.metric("Customer Rating", "4.8 ⭐")
    
    # Recent orders chart
    st.subheader("Recent Orders")
    orders_data = {
        'Date': ['2024-01-15', '2024-01-14', '2024-01-13', '2024-01-12', '2024-01-11'],
        'Orders': [8, 12, 6, 15, 10]
    }
    df = pd.DataFrame(orders_data)
    fig = px.line(df, x='Date', y='Orders', title='Daily Orders')
    st.plotly_chart(fig, use_container_width=True)

# Medicines page
def medicines_page():
    """Medicines catalog"""
    st.title("💊 Medicine Catalog")
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search medicines", placeholder="Enter medicine name...")
    
    with col2:
        categories = api_request("GET", "/categories")
        if categories:
            category_names = [cat["name"] for cat in categories]
            selected_category = st.selectbox("Category", ["All"] + category_names)
        else:
            selected_category = "All"
    
    with col3:
        prescription_required = st.selectbox("Prescription", ["All", "Required", "Not Required"])
    
    # Get medicines
    medicines = api_request("GET", "/medicines")
    
    if medicines:
        # Filter medicines
        filtered_medicines = medicines
        
        if search_query:
            filtered_medicines = [m for m in filtered_medicines if search_query.lower() in m["name"].lower()]
        
        if selected_category != "All":
            filtered_medicines = [m for m in filtered_medicines if m["category"]["name"] == selected_category]
        
        if prescription_required == "Required":
            filtered_medicines = [m for m in filtered_medicines if m["prescription_required"]]
        elif prescription_required == "Not Required":
            filtered_medicines = [m for m in filtered_medicines if not m["prescription_required"]]
        
        # Display medicines
        for medicine in filtered_medicines:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.subheader(medicine["name"])
                    if medicine["generic_name"]:
                        st.write(f"Generic: {medicine['generic_name']}")
                    st.write(f"Category: {medicine['category']['name']}")
                    st.write(f"Price: ₹{medicine['price']}")
                    st.write(f"Stock: {medicine['stock_quantity']} units")
                    
                    if medicine["prescription_required"]:
                        st.warning("⚠️ Prescription Required")
                
                with col2:
                    st.write(f"**₹{medicine['price']}**")
                    st.write(f"Delivery: {medicine['delivery_time_minutes']} min")
                
                with col3:
                    if medicine["stock_quantity"] > 0:
                        quantity = st.number_input(f"Qty", min_value=1, max_value=medicine["stock_quantity"], key=f"qty_{medicine['id']}")
                        if st.button("Add to Cart", key=f"add_{medicine['id']}"):
                            add_to_cart(medicine["id"], quantity)
                    else:
                        st.error("Out of Stock")

# Cart page
def cart_page():
    """Shopping cart"""
    st.title("🛒 Shopping Cart")
    
    cart = api_request("GET", "/cart", token=st.session_state.token)
    
    if cart and cart["items"]:
        total_amount = 0
        
        for item in cart["items"]:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{item['medicine']['name']}**")
                    st.write(f"Price: ₹{item['medicine']['price']} per unit")
                
                with col2:
                    st.write(f"Quantity: {item['quantity']}")
                
                with col3:
                    item_total = item['quantity'] * item['medicine']['price']
                    total_amount += item_total
                    st.write(f"**₹{item_total}**")
                
                with col4:
                    if st.button("Remove", key=f"remove_{item['id']}"):
                        remove_from_cart(item['id'])
                        st.rerun()
        
        st.divider()
        st.write(f"**Total Amount: ₹{total_amount}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Cart"):
                clear_cart()
                st.rerun()
        
        with col2:
            if st.button("Proceed to Checkout", type="primary"):
                st.session_state.checkout = True
                st.rerun()
    
    else:
        st.info("Your cart is empty. Add some medicines!")

# Orders page
def orders_page():
    """User orders"""
    st.title("📋 My Orders")
    
    orders = api_request("GET", "/orders", token=st.session_state.token)
    
    if orders:
        for order in orders:
            with st.expander(f"Order #{order['order_number']} - {order['status']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Order Date:** {order['created_at'][:10]}")
                    st.write(f"**Total Amount:** ₹{order['total_amount']}")
                    st.write(f"**Delivery Address:** {order['delivery_address']}")
                    st.write(f"**Delivery Type:** {order['delivery_type']}")
                
                with col2:
                    status_class = f"status-{order['status']}"
                    st.markdown(f'<span class="status-badge {status_class}">{order["status"].upper()}</span>', unsafe_allow_html=True)
                    
                    if order['estimated_delivery_time']:
                        st.write(f"**Estimated Delivery:** {order['estimated_delivery_time'][:16]}")
                    
                    if order['actual_delivery_time']:
                        st.write(f"**Delivered:** {order['actual_delivery_time'][:16]}")
                
                # Order items
                st.subheader("Items:")
                for item in order['items']:
                    st.write(f"• {item['medicine']['name']} x{item['quantity']} - ₹{item['total_price']}")
    else:
        st.info("No orders found.")

# Prescriptions page
def prescriptions_page():
    """User prescriptions"""
    st.title("📄 My Prescriptions")
    
    # Upload new prescription
    st.subheader("Upload New Prescription")
    uploaded_file = st.file_uploader("Choose prescription image", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            doctor_name = st.text_input("Doctor Name")
        with col2:
            hospital_name = st.text_input("Hospital Name")
        
        if st.button("Upload Prescription"):
            # Handle file upload
            st.success("Prescription uploaded successfully!")
    
    # View existing prescriptions
    st.subheader("My Prescriptions")
    prescriptions = api_request("GET", "/prescriptions", token=st.session_state.token)
    
    if prescriptions:
        for prescription in prescriptions:
            with st.expander(f"Prescription #{prescription['id']} - {prescription['created_at'][:10]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Doctor:** {prescription['doctor_name'] or 'Not specified'}")
                    st.write(f"**Hospital:** {prescription['hospital_name'] or 'Not specified'}")
                
                with col2:
                    if prescription['is_verified']:
                        st.success("✅ Verified")
                    else:
                        st.warning("⏳ Pending Verification")
                
                if prescription['verification_notes']:
                    st.write(f"**Notes:** {prescription['verification_notes']}")
    else:
        st.info("No prescriptions found.")

# Profile page
def profile_page():
    """User profile"""
    st.title("👤 My Profile")
    
    if st.session_state.user:
        user = st.session_state.user
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** {user['username']}")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Phone:** {user['phone']}")
            st.write(f"**Role:** {user['role']}")
        
        with col2:
            st.write(f"**Address:** {user['address'] or 'Not specified'}")
            st.write(f"**City:** {user['city'] or 'Not specified'}")
            st.write(f"**State:** {user['state'] or 'Not specified'}")
            st.write(f"**Pincode:** {user['pincode'] or 'Not specified'}")
        
        # Update profile
        st.subheader("Update Profile")
        with st.form("update_profile"):
            new_address = st.text_input("Address", value=user.get('address', ''))
            new_city = st.text_input("City", value=user.get('city', ''))
            new_state = st.text_input("State", value=user.get('state', ''))
            new_pincode = st.text_input("Pincode", value=user.get('pincode', ''))
            
            if st.form_submit_button("Update Profile"):
                update_data = {
                    "address": new_address,
                    "city": new_city,
                    "state": new_state,
                    "pincode": new_pincode
                }
                response = api_request("PUT", "/auth/profile", update_data, st.session_state.token)
                if response:
                    st.success("Profile updated successfully!")
                    st.session_state.user = response
                    st.rerun()

# Delivery page
def delivery_page():
    """Delivery tracking and estimates"""
    st.title("🚚 Delivery Services")
    
    tab1, tab2, tab3 = st.tabs(["Delivery Estimate", "Nearby Pharmacies", "Emergency Delivery"])
    
    with tab1:
        st.subheader("Get Delivery Estimate")
        with st.form("delivery_estimate"):
            address = st.text_input("Delivery Address")
            city = st.text_input("City")
            pincode = st.text_input("Pincode")
            delivery_type = st.selectbox("Delivery Type", ["standard", "express", "emergency"])
            
            if st.form_submit_button("Get Estimate"):
                if address and city and pincode:
                    estimate = api_request("GET", f"/delivery/estimate?delivery_address={address}&delivery_city={city}&delivery_pincode={pincode}&delivery_type={delivery_type}")
                    if estimate:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Estimated Time", f"{estimate['estimated_time_minutes']} min")
                        with col2:
                            st.metric("Delivery Fee", f"₹{estimate['delivery_fee']}")
                        with col3:
                            st.metric("Available Partners", estimate['available_partners'])
    
    with tab2:
        st.subheader("Nearby Pharmacies")
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=12.9716)
        with col2:
            lon = st.number_input("Longitude", value=77.5946)
        
        if st.button("Find Nearby Pharmacies"):
            pharmacies = api_request("GET", f"/nearby-pharmacies?latitude={lat}&longitude={lon}")
            if pharmacies:
                for pharmacy in pharmacies:
                    with st.container():
                        st.write(f"**{pharmacy['name']}**")
                        st.write(f"Address: {pharmacy['address']}")
                        st.write(f"Distance: {pharmacy['distance_km']} km")
                        st.write(f"Available Medicines: {pharmacy['available_medicines']}")
                        st.write(f"Estimated Delivery: {pharmacy['estimated_delivery_time']} min")
                        st.divider()
    
    with tab3:
        st.subheader("Emergency Medicine Delivery")
        st.warning("⚠️ Use this only for genuine medical emergencies")
        
        with st.form("emergency_delivery"):
            medicines = api_request("GET", "/medicines")
            if medicines:
                medicine_options = [f"{m['name']} (₹{m['price']})" for m in medicines]
                selected_medicines = st.multiselect("Select Medicines", medicine_options)
            
            emergency_address = st.text_input("Emergency Delivery Address")
            emergency_city = st.text_input("City")
            emergency_pincode = st.text_input("Pincode")
            urgency = st.selectbox("Urgency Level", ["high", "medium", "low"])
            
            if st.form_submit_button("Request Emergency Delivery"):
                st.error("Emergency delivery feature requires additional setup and verification.")

# Helper functions for cart operations
def add_to_cart(medicine_id, quantity):
    """Add medicine to cart"""
    data = {"medicine_id": medicine_id, "quantity": quantity}
    response = api_request("POST", "/cart/items", data, st.session_state.token)
    if response:
        st.success("Added to cart!")

def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    response = api_request("DELETE", f"/cart/items/{cart_item_id}", token=st.session_state.token)
    if response:
        st.success("Removed from cart!")

def clear_cart():
    """Clear entire cart"""
    response = api_request("DELETE", "/cart", token=st.session_state.token)
    if response:
        st.success("Cart cleared!")

# Login/Register page
def auth_page():
    """Authentication page"""
    st.markdown('<h1 class="main-header">🏥 Quick Commerce Medicine Delivery</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                if username and password:
                    if login_user(username, password):
                        st.rerun()
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_phone = st.text_input("Phone", key="reg_phone")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_address = st.text_input("Address", key="reg_address")
            reg_city = st.text_input("City", key="reg_city")
            reg_state = st.text_input("State", key="reg_state")
            reg_pincode = st.text_input("Pincode", key="reg_pincode")
            
            if st.form_submit_button("Register"):
                if all([reg_username, reg_email, reg_phone, reg_password]):
                    user_data = {
                        "username": reg_username,
                        "email": reg_email,
                        "phone": reg_phone,
                        "password": reg_password,
                        "address": reg_address,
                        "city": reg_city,
                        "state": reg_state,
                        "pincode": reg_pincode
                    }
                    if register_user(user_data):
                        st.rerun()
                else:
                    st.error("Please fill all required fields")

# Main app
def main():
    """Main application"""
    page = main_navigation()
    
    if page == "Login":
        auth_page()
    elif page == "🏠 Dashboard":
        dashboard_page()
    elif page == "💊 Medicines":
        medicines_page()
    elif page == "🛒 Cart":
        cart_page()
    elif page == "📋 Orders":
        orders_page()
    elif page == "📄 Prescriptions":
        prescriptions_page()
    elif page == "👤 Profile":
        profile_page()
    elif page == "🚚 Delivery":
        delivery_page()

if __name__ == "__main__":
    main() 