# Sprint 1 Report

## Goal
Ship a super small MVP with only three flows:

- Cashier can create an order
- Barista can see pending orders
- Customer can see queue position

## What was delivered

- Streamlit app shell with role-based views
- SQLite database setup
- `orders` table creation on startup
- Cashier order form that saves to the database
- Barista pending orders table
- Customer queue position lookup by order number
- One pytest covering order creation and queue position logic

## Not included by design

- Split payments
- Inventory system
- Complex architecture
- Fancy UI polish
- Expanded user stories
