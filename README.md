# 🛒 E-commerce Microservices System

A fully containerized microservices-based e-commerce system built with **Python Flask**, **Docker**, and **PostgreSQL**. 
Designed to be scalable, modular, and production-ready.

---

## 🚀 Project Structure

- **6 Microservices**:
  - `Auth Service`: Handles authentication and JWT token generation
  - `User Service`: Manages user profiles and data
  - `Product Service`: Manages product catalog
  - `Cart Service`: Handles shopping cart logic
  - `Order Service`: Manages order creation and history
  - `Payment Service`: Processes payments (mock)

- **Individual PostgreSQL databases** per service
- **Nginx API Gateway** for request routing to appropriate service
- **Simple HTML/CSS/JS frontend** (in English) for demonstration

---

## 🔧 Tech Stack

- **Backend**: Python + Flask
- **Frontend**: HTML / CSS / JavaScript
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Gateway**: Nginx
- **Authentication**: JWT
- **Communication**: RESTful APIs

---

## 💡 Key Features

### ✅ Backend (Flask Microservices):

- JWT authentication system via `auth-service`
- RESTful APIs for CRUD operations
- Full database isolation per microservice
- Dockerized services for modular deployment
- API Gateway using Nginx for routing
- Clean error handling & status codes

### 🖥️ Frontend:

- Responsive UI (HTML/CSS/JS)
- User Registration & Login
- Product Browsing
- Shopping Cart Management
- Order Placement & History
