from django.contrib import admin
from django.db import connection
from django.urls import path
from django.shortcuts import render, redirect
import string
import random


# LOGIN

def login_page(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        cursor = connection.cursor()

        query = """
        SELECT * FROM users
        WHERE email=%s
        AND password=%s
        AND role=%s
        """

        cursor.execute(
            query,
            [email, password, role]
        )

        user = cursor.fetchone()

        if user:

            request.session['email'] = email
            request.session['role'] = role

            return redirect('dashboard')

        else:

            return render(
                request,
                'login.html',
                {
                    'error':
                    'Invalid Credentials'
                }
            )

    return render(request, 'login.html')


# SIGNUP

def signup_page(request):

    if request.method == "POST":

        username = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get(
            'confirm_password'
        )
        role = request.POST.get('role')

        # Password match check

        if password != confirm_password:

            return render(
                request,
                'signup.html',
                {
                    'error':
                    'Passwords do not match'
                }
            )

        cursor = connection.cursor()

        # Duplicate email check

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            [email]
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return render(
                request,
                'signup.html',
                {
                    'error':
                    'Email already exists'
                }
            )

        # Insert user

        cursor.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password,
                role
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            [
                username,
                email,
                password,
                role
            ]
        )

        return redirect('login')

    return render(
        request,
        'signup.html'
    )


# FORGOT PASSWORD

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get('email')

        cursor = connection.cursor()

        # Check email exists

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email=%s
            """,
            [email]
        )

        user = cursor.fetchone()

        if not user:

            return render(
                request,
                'forgot_password.html',
                {
                    'error':
                    'Email not found'
                }
            )

        # Generate random password

        new_password = ''.join(
            random.choices(
                string.ascii_letters +
                string.digits,
                k=8
            )
        )

        # Update password

        cursor.execute(
            """
            UPDATE users
            SET password=%s
            WHERE email=%s
            """,
            [new_password, email]
        )

        return render(
            request,
            'forgot_password.html',
            {
                'success':
                f'New Password: {new_password}'
            }
        )

    return render(
        request,
        'forgot_password.html'
    )
def purchase_order_page(request):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
        q.quotation_id,
        r.title,
        v.company_name,
        q.price,
        q.status

        FROM quotations q

        JOIN rfq r
        ON q.rfq_id =
        r.rfq_id

        JOIN vendors v
        ON q.vendor_id =
        v.vendor_id

        WHERE q.status =
        'approved'
        """
    )

    purchase_orders = cursor.fetchall()

    return render(
        request,
        'purchase_order.html',
        {
            'purchase_orders':
            purchase_orders
        }
    )
def vendors_page(request):

    # Admin only

    if request.session.get('role') != 'admin':
        return redirect('dashboard')

    cursor = connection.cursor()

    # Add Vendor

    if request.method == "POST":

        company_name = request.POST.get(
            'company_name'
        )

        gst_number = request.POST.get(
            'gst_number'
        )

        contact_person = request.POST.get(
            'contact_person'
        )

        email = request.POST.get(
            'email'
        )

        phone = request.POST.get(
            'phone'
        )

        category = request.POST.get(
            'category'
        )

        status = request.POST.get(
            'status'
        )

        cursor.execute(
            """
            INSERT INTO vendors
            (
                company_name,
                gst_number,
                contact_person,
                email,
                phone,
                category,
                status
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s)
            """,
            [
                company_name,
                gst_number,
                contact_person,
                email,
                phone,
                category,
                status
            ]
        )

    # Fetch Vendors

    cursor.execute(
        """
        SELECT *
        FROM vendors
        """
    )

    vendors = cursor.fetchall()

    return render(
        request,
        'vendors.html',
        {
            'vendors': vendors
        }
    )
def invoice_page(request):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
        q.quotation_id,
        r.title,
        v.company_name,
        q.price,
        q.status

        FROM quotations q

        JOIN rfq r
        ON q.rfq_id = r.rfq_id

        JOIN vendors v
        ON q.vendor_id = v.vendor_id
        """
    )

    invoices = cursor.fetchall()

    return render(
        request,
        'invoice.html',
        {
            'invoices': invoices,
            'role':
            request.session.get(
                'role'
            )
        }
    )
# DASHBOARD

def dashboard(request):

    if 'email' not in request.session:
        return redirect('login')

    email = request.session.get('email')
    role = request.session.get('role')

    cursor = connection.cursor()

    # Vendors count

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM vendors
        """
    )

    vendor_count = cursor.fetchone()[0]

    # RFQ count

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM rfq
        """
    )

    rfq_count = cursor.fetchone()[0]

    # Approval count

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM approvals
        """
    )

    approval_count = cursor.fetchone()[0]

    # Invoice count

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM invoices
        """
    )

    invoice_count = cursor.fetchone()[0]

    return render(
        request,
        'dashboard.html',
        {
            'email': email,
            'role': role,
            'vendor_count': vendor_count,
            'rfq_count': rfq_count,
            'approval_count': approval_count,
            'invoice_count': invoice_count
        }
    )


# RFQ PAGE
# PROCUREMENT OFFICER ONLY

def rfq_page(request):

    # Only Procurement Officer

    if request.session.get(
        'role'
    ) != 'procurement_officer':

        return redirect('dashboard')

    cursor = connection.cursor()

    # Add RFQ

    if request.method == "POST":

        title = request.POST.get(
            'title'
        )

        product_name = request.POST.get(
            'product_name'
        )

        quantity = request.POST.get(
            'quantity'
        )

        deadline = request.POST.get(
            'deadline'
        )

        vendor_id = request.POST.get(
            'vendor_id'
        )

        cursor.execute(
            """
            INSERT INTO rfq
            (
                title,
                product_name,
                quantity,
                deadline,
                vendor_id
            )
            VALUES
            (%s,%s,%s,%s,%s)
            """,
            [
                title,
                product_name,
                quantity,
                deadline,
                vendor_id
            ]
        )

    # Fetch Vendors dropdown

    cursor.execute(
        """
        SELECT vendor_id,
        company_name
        FROM vendors
        """
    )

    vendors = cursor.fetchall()

    # Fetch RFQ table

    cursor.execute(
        """
        SELECT
        r.rfq_id,
        r.title,
        r.product_name,
        r.quantity,
        r.deadline,
        v.company_name,
        r.status

        FROM rfq r

        LEFT JOIN vendors v
        ON r.vendor_id =
        v.vendor_id
        """
    )

    rfqs = cursor.fetchall()

    return render(
        request,
        'rfq.html',
        {
            'vendors': vendors,
            'rfqs': rfqs
        }
    )


# APPROVAL PAGE
# MANAGER ONLY

def approval_page(request):

    if request.session.get(
        'role'
    ) != 'manager':

        return redirect('dashboard')

    cursor = connection.cursor()

    # APPROVE

    if request.GET.get('approve'):

        quotation_id = request.GET.get(
            'approve'
        )

        cursor.execute(
            """
            UPDATE quotations
            SET status='approved'
            WHERE quotation_id=%s
            """,
            [quotation_id]
        )

    # REJECT

    if request.GET.get('reject'):

        quotation_id = request.GET.get(
            'reject'
        )

        cursor.execute(
            """
            UPDATE quotations
            SET status='rejected'
            WHERE quotation_id=%s
            """,
            [quotation_id]
        )

    # FETCH

    cursor.execute(
        """
        SELECT
        q.quotation_id,
        r.title,
        v.company_name,
        q.price,
        q.delivery_days,
        q.status

        FROM quotations q

        JOIN rfq r
        ON q.rfq_id =
        r.rfq_id

        JOIN vendors v
        ON q.vendor_id =
        v.vendor_id
        """
    )

    quotations = cursor.fetchall()

    return render(
        request,
        'approval.html',
        {
            'quotations':
            quotations
        }
    )


# QUOTATION PAGE
# VENDOR ONLY

def quotation_page(request):

    if request.session.get(
        'role'
    ) != 'vendor':

        return redirect('dashboard')

    cursor = connection.cursor()

    # Submit quotation

    if request.method == "POST":

        rfq_id = request.POST.get(
            'rfq_id'
        )

        vendor_id = request.POST.get(
            'vendor_id'
        )

        price = request.POST.get(
            'price'
        )

        delivery_days = request.POST.get(
            'delivery_days'
        )

        remarks = request.POST.get(
            'remarks'
        )

        cursor.execute(
            """
            INSERT INTO quotations
            (
                rfq_id,
                vendor_id,
                price,
                delivery_days,
                remarks
            )
            VALUES
            (%s,%s,%s,%s,%s)
            """,
            [
                rfq_id,
                vendor_id,
                price,
                delivery_days,
                remarks
            ]
        )

    # Fetch RFQ + ALL vendors

    cursor.execute(
        """
        SELECT
        r.rfq_id,
        r.title,
        v.vendor_id,
        v.company_name

        FROM rfq r
        CROSS JOIN vendors v
        """
    )

    rfqs = cursor.fetchall()

    # Submitted quotations

    cursor.execute(
        """
        SELECT
        q.quotation_id,
        r.title,
        v.company_name,
        q.price,
        q.delivery_days,
        q.status

        FROM quotations q

        JOIN rfq r
        ON q.rfq_id =
        r.rfq_id

        JOIN vendors v
        ON q.vendor_id =
        v.vendor_id
        """
    )

    quotations = cursor.fetchall()

    return render(
        request,
        'quotation.html',
        {
            'rfqs': rfqs,
            'quotations':
            quotations,
            'role':
            request.session.get(
                'role'
            )
        }
    )
def quotation_comparison(request):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
        q.quotation_id,
        r.title,
        v.company_name,
        q.price,
        q.delivery_days,
        q.status

        FROM quotations q

        JOIN rfq r
        ON q.rfq_id =
        r.rfq_id

        JOIN vendors v
        ON q.vendor_id =
        v.vendor_id

        ORDER BY
        r.title,
        q.price ASC
        """
    )

    quotations = cursor.fetchall()

    return render(
        request,
        'quotation_comparison.html',
        {
            'quotations':
            quotations
        }
    )

# LOGOUT

def logout(request):

    request.session.flush()

    return redirect('login')

def my_rfq_page(request):

    # Vendor only

    if request.session.get(
        'role'
    ) != 'vendor':

        return redirect('dashboard')

    cursor = connection.cursor()

    # TEMPORARY:
    # Show all RFQ assigned to vendors

    cursor.execute(
        """
        SELECT
        r.rfq_id,
        r.title,
        r.product_name,
        r.quantity,
        r.deadline,
        v.company_name,
        r.status

        FROM rfq r

        JOIN vendors v
        ON r.vendor_id =
        v.vendor_id
        """
    )

    rfqs = cursor.fetchall()

    return render(
        request,
        'my_rfq.html',
        {
            'rfqs': rfqs
        }
    )

    
urlpatterns = [

    path('admin/', admin.site.urls),

    # Login
    path('', login_page, name='login'),

    # Signup
    path(
        'signup/',
        signup_page,
        name='signup'
    ),

    # Forgot Password
    path(
        'forgot-password/',
        forgot_password,
        name='forgot_password'
    ),
    path(
    'quotation-comparison/',
    quotation_comparison,
    name='quotation_comparison'
    ),
    # Dashboard
    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),
    path(
        'invoice/',
        invoice_page,
        name='invoice'
    ),
    # Vendors
    path(
        'vendors/',
        vendors_page,
        name='vendors'
    ),

    path(
    'my-rfq/',
    my_rfq_page,
    name='my_rfq'
    ),
    # RFQ
    path(
        'rfq/',
        rfq_page,
        name='rfq'
    ),
    path(
        'purchase-order/',
        purchase_order_page,
        name='purchase_order'
    ),
    # Approval
    path(
        'approval/',
        approval_page,
        name='approval'
    ),

    # Quotation
    path(
        'quotation/',
        quotation_page,
        name='quotation'
    ),
    path(
        'quotation-comparison/',
        quotation_comparison,
        name='quotation_comparison'
    ),
    # Logout
    path(
        'logout/',
        logout,
        name='logout'
    ),
    path(
    'vendors/',
    vendors_page,
    name='vendors'
),
]