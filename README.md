# notes-api
Backend for the Note-taking web app, using Django and Django REST Framework


# API Documentation

## Authentication
**All endpoints (except obtaining tokens) require authentication.**
You must include the Access Token in the header of your requests:
* **Header:** `Authorization`
* **Value:** `Bearer <your_access_token>`

---

## 1. Auth & Tokens

### **Login (Obtain Token)**
> **`POST`** `/api/token/`

**Description**
Exchange a username and password for an access and refresh token.

**Request Body**
```json
{
  "username": "myusername",
  "password": "mypassword"
}