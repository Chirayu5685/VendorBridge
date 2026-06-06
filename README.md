# VendorBridge
Odoo Hackathon
# VendorBridge ERP

## Team Project

Vendor Management & Procurement ERP System

### Modules Implemented

* Login / Signup / Forgot Password
* Role Based Access System (RBAS)
* Vendor Management
* RFQ Management
* Vendor RFQ Status
* Quotation Submission
* Quotation Comparison
* Approval Management
* Purchase Order
* Invoice Management

### Roles

#### Admin

* Vendor Management

#### Procurement Officer

* RFQ Creation
* Quotation Comparison
* Invoice View

#### Vendor

* My RFQ
* Submit Quotation

#### Manager

* Approvals
* Purchase Orders
* Invoice Approval

### Setup Instructions

1. Install requirements

```bash
pip install -r requirements.txt
```

2. Import Database

Import:

```text
database/vendorbridge_db.sql
```

into MySQL Workbench.

3. Configure MySQL credentials in:

```text
vendorbridge/settings.py
```

4. Run Project

```bash
python manage.py runserver
```
