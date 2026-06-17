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

### 🔐 Authentication
- POST `/api/auth/login`
- POST `/api/auth/forgot-password`
- POST `/api/auth/reset-password`
- PATCH `/api/auth/change-password`

---

### 📝 Posts
- GET `/api/posts`
  - Supports:
    - `search` → filter posts
    - `skip` → pagination offset
    - `limit` → number of posts
- POST `/api/posts`

---

### 👤 Users
- POST `/api/users`
- GET `/api/users/{id}`

---


## ▶️ Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
