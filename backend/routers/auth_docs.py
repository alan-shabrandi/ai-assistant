from fastapi import status

REGISTER_DOCS = {
    "status_code": status.HTTP_201_CREATED,
    "summary": "Register a new user",
    "description": "Takes a username and password to create a new user identity in the system. Password will be securely hashed.",
    "responses": {
        201: {"description": "User created successfully."},
        400: {"description": "Username already exists or invalid registration data."}
    }
}

LOGIN_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Authenticate user and obtain session token",
    "description": "Authenticates credentials using standard OAuth2 Form Data. Upon success, issues a secure, HttpOnly JWT access token cookie.",
    "responses": {
        200: {"description": "Authentication successful, secure cookie set."},
        401: {"description": "Incorrect username or password."}
    }
}

LOGOUT_DOCS = {
    "status_code": status.HTTP_200_OK,
    "summary": "Logout current user",
    "description": "Clears and invalidates the secure HttpOnly session token cookie from the client browser.",
    "responses": {
        200: {"description": "Cookie successfully deleted and session terminated."}
    }
}