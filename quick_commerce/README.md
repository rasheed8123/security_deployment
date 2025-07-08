# 🏥 Quick Commerce Medicine Delivery Application

A comprehensive medicine delivery platform built with FastAPI backend and Streamlit frontend, featuring quick commerce capabilities, prescription management, and real-time delivery tracking.

## 🚀 Features

### Core Features
- **User Authentication & Profiles**: Secure login/register with medical profiles
- **Medicine Catalog**: Comprehensive medicine database with search and filtering
- **Prescription Management**: Upload and verify prescriptions
- **Shopping Cart**: Add medicines with prescription validation
- **Order Management**: Complete order lifecycle with status tracking
- **Quick Delivery**: 10-30 minute delivery promise with real-time tracking
- **Role-Based Access**: Pharmacy admin, pharmacist, delivery partner roles

### Quick Commerce Features
- **Real-time Inventory**: Live stock tracking
- **Dynamic Pricing**: Based on urgency and availability
- **Location-based Availability**: Find nearby pharmacies
- **Delivery Partner Optimization**: Efficient route planning
- **Emergency Delivery**: Priority handling for urgent medicines

### Security & Validation
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive data validation
- **Prescription Verification**: Pharmacist verification system
- **Role-based Permissions**: Granular access control

## 🏗️ Architecture

```
quick_commerce/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API application
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── crud.py             # Database CRUD operations
│   ├── auth.py             # Authentication utilities
│   ├── dependencies.py     # FastAPI dependencies
│   └── database.py         # Database configuration
├── frontend/               # Streamlit frontend
│   └── app.py              # Main Streamlit application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### 1. Clone and Setup
```bash
# Navigate to the project directory
cd quick_commerce

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
# Navigate to backend directory
cd backend

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Start Frontend Application
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Start Streamlit app
streamlit run app.py
```

The frontend will be available at `http://localhost:8501`

## 📋 API Endpoints

### Authentication & Users
- `POST /auth/register` - Register new user with medical profile
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile
- `PUT /auth/profile` - Update user profile and delivery address
- `POST /auth/verify-phone` - Verify phone number for delivery

### Medicines (Public & Pharmacy Admin)
- `GET /medicines` - Get all medicines with availability and pricing
- `POST /medicines` - Add new medicine (pharmacy admin only)
- `PUT /medicines/{id}` - Update medicine details (pharmacy admin only)
- `DELETE /medicines/{id}` - Remove medicine (pharmacy admin only)
- `GET /medicines/search` - Search medicines with filters
- `GET /medicines/{id}/alternatives` - Get alternative medicines
- `PATCH /medicines/{id}/stock` - Update medicine stock levels

### Medicine Categories
- `GET /categories` - Get all medicine categories
- `POST /categories` - Create new category (pharmacy admin)
- `PUT /categories/{id}` - Update category (pharmacy admin)
- `DELETE /categories/{id}` - Delete category (pharmacy admin)

### Prescriptions
- `POST /prescriptions/upload` - Upload prescription image
- `GET /prescriptions` - Get user's prescriptions
- `GET /prescriptions/{id}` - Get specific prescription details
- `PUT /prescriptions/{id}/verify` - Verify prescription (pharmacist only)

### Shopping Cart (User only)
- `GET /cart` - Get user's cart with prescription validation
- `POST /cart/items` - Add medicine to cart
- `PUT /cart/items/{id}` - Update cart item quantity
- `DELETE /cart/items/{id}` - Remove medicine from cart
- `DELETE /cart` - Clear entire cart

### Orders & Delivery
- `POST /orders` - Create order from cart with delivery details
- `GET /orders` - Get user's orders with delivery status
- `GET /orders/{id}` - Get specific order details
- `PATCH /orders/{id}/status` - Update order status
- `POST /orders/{id}/delivery-proof` - Upload delivery confirmation

### Quick Delivery Features
- `GET /delivery/estimate` - Get delivery time estimate
- `GET /delivery/partners` - Get available delivery partners
- `POST /delivery/emergency` - Create emergency medicine delivery request
- `GET /nearby-pharmacies` - Find nearby pharmacies with stock

## 🧪 Testing the Application

### 1. Backend Testing
Visit `http://localhost:8000/docs` for interactive API documentation and testing.

### 2. Frontend Testing
1. Open `http://localhost:8501` in your browser
2. Register a new account or login
3. Browse medicines and add to cart
4. Upload prescriptions
5. Place orders and track delivery

### 3. Sample Data
The application starts with an empty database. You can:
- Register as a regular user
- Create pharmacy admin accounts manually in the database
- Add medicines and categories through the API

## 👥 User Roles

### Regular User
- Browse medicines
- Add items to cart
- Upload prescriptions
- Place orders
- Track deliveries

### Pharmacy Admin
- Manage medicine catalog
- Update stock levels
- Manage categories
- View all orders

### Pharmacist
- Verify prescriptions
- Review medicine orders
- Manage inventory

### Delivery Partner
- Update order status
- Upload delivery proof
- Track deliveries

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./quick_commerce.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database
The application uses SQLite by default. For production, consider:
- PostgreSQL for better performance
- Redis for caching
- Separate database for user data and medicine catalog

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Configure HTTPS
- [ ] Set up proper CORS origins
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Set up backup strategies
- [ ] Configure email service for notifications

### Performance Optimization
- Use PostgreSQL for production database
- Implement Redis for caching
- Set up CDN for static files
- Configure connection pooling
- Add database indexing

## 📱 Mobile Responsiveness

The Streamlit frontend is designed to be mobile-responsive with:
- Responsive layouts
- Touch-friendly interfaces
- Optimized for quick medicine ordering
- Accessibility features for elderly users

## 🔍 Error Handling

The application includes comprehensive error handling:
- Input validation with clear error messages
- API error responses with proper HTTP status codes
- User-friendly error messages in the frontend
- Graceful handling of network issues

## 📊 Monitoring & Analytics

Consider adding:
- Order analytics and reporting
- Delivery performance metrics
- User behavior tracking
- Inventory analytics
- Revenue reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the error logs
- Create an issue in the repository

---

**Quick Commerce Medicine Delivery** - Bringing healthcare to your doorstep in minutes! 🏥💊 