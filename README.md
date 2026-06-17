# 🚀 Backend Dev Blog (FastAPI)

A full-stack blog platform built using **FastAPI, PostgreSQL, and SQLAlchemy**, designed to demonstrate real-world backend development skills including authentication, pagination, search, email workflows, and dynamic UI rendering.

---

## 🚀 Project Overview

The **Backend Dev Blog** is a modern web application that allows users to create, view, and manage blog posts with secure authentication and a responsive UI. It includes features like JWT login, password reset via email, search functionality, and efficient pagination.

The system is designed with clean architecture principles and scalable backend practices.

---

## 🖥️ Tech Stack

### Frontend
- HTML
- CSS
- Bootstrap 5
- JavaScript (AJAX for dynamic loading)
- Jinja2 Templates

### Backend
- FastAPI (Python Web Framework)

### Database
- PostgreSQL
- SQLAlchemy ORM

### Authentication
- JWT (JSON Web Tokens)
- OAuth2 Password Flow

---

## ✨ Features

### 🔐 Authentication System
- User registration and login
- JWT-based authentication
- Secure password hashing
- Forgot password via email reset link
- Change password functionality

---

### 📝 Blog System
- Create and view posts
- Author-based post ownership
- Clean relational database design
- RESTful API structure

---

### 🔍 Search Functionality
- Search posts by title or content
- Case-insensitive partial matching
- Efficient database-level filtering

---

### 📄 Pagination
- Offset-based pagination (`skip` / `limit`)
- Load More button using AJAX
- Optimized API response handling

---

### 📧 Email System
- Password reset email system
- Background task execution using FastAPI BackgroundTasks

---

### 🖼 Profile Management
- User profile image upload
- Static and media file handling
- Image processing utilities

---

## 🔌 API Endpoints

Below is the complete list of API endpoints available in the application, categorized by their Swagger UI tags. Endpoints marked with 🔒 require an active JWT authorization token.

### 👥 Users
- **GET** `/api/posts` - Get Posts
- **POST** `/api/users` - Create User
- **GET** `/api/users/{user_id}` - Get User
- **PATCH** `/api/users/{user_id}` - Update User 🔒
- **DELETE** `/api/users/{user_id}` - Delete User 🔒
- **GET** `/api/users/{user_id}/posts` - Get User Posts

### 📝 Posts
- **POST** `/api/posts` - Create Post 🔒
- **GET** `/api/post/{post_id}` - Get Post
- **PUT** `/api/posts/{post_id}` - Update Post Full 🔒
- **PATCH** `/api/posts/{post_id}` - Update Post Partial 🔒
- **DELETE** `/api/posts/{post_id}` - Delete Post 🔒
- **GET** `/api/post` - Get Posts

### 🖼️ Profile
- **GET** `/api/me` - Me 🔒
- **PATCH** `/api/{user_id}/picture` - Upload Profile Picture 🔒
- **DELETE** `/api/{user_id}/picture` - Delete User Picture 🔒

### 🔐 Auth
- **POST** `/api/auth/login` - Login For Access Token
- **POST** `/api/auth/forgot-password` - Forgot Password
- **POST** `/api/auth/reset-password` - Reset Password
- **PATCH** `/api/auth/change-password` - Change Password 🔒

---

## 📸 Swagger API Documentation

*(Make sure the image files `Swaager_docs_page1.png` and `Swaager_docs_page2.png` are in the same directory as this README file for them to display properly).*

![Swagger UI Page 1](Swaager_docs_page1.png)

![Swagger UI Page 2](Swaager_docs_page2.png)

---

## ▶️ Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
