# API Documentation

## Authentication

### Register
POST `/api/v1/users/register/`
```json
{
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "password": "StrongPass123!",
    "password_confirm": "StrongPass123!"
}
```

### Login
POST `/api/v1/users/login/`
```json
{
    "email": "user@example.com",
    "password": "StrongPass123!"
}
```

## Products

### List Products
GET `/api/v1/products/`

Query params: `search`, `category`, `brand`, `min_price`, `max_price`, `rating`, `in_stock`, `sort_by`

### Get Product
GET `/api/v1/products/{id}/`

## Cart

### Get Cart
GET `/api/v1/cart/`

### Add to Cart
POST `/api/v1/cart/add-item/`
```json
{
    "product_id": "uuid",
    "quantity": 1
}
```

## Orders

### Create Order
POST `/api/v1/orders/`
```json
{
    "shipping_address_id": "uuid",
    "payment_method": "credit_card"
}
```

## Reviews

### Create Review
POST `/api/v1/reviews/`
```json
{
    "product_id": "uuid",
    "rating": 5,
    "body": "Great product!"
}
```

## Search

### Search Products
GET `/api/v1/search/?q=headphones`

### Autocomplete
GET `/api/v1/autocomplete/?q=hea`
