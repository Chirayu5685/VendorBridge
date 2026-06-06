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

    if request.session.get(
        'role'
    ) != 'procurement_officer':

        return redirect('dashboard')

    return render(request, 'rfq.html')


# APPROVAL PAGE
# MANAGER ONLY

def approval_page(request):

    if request.session.get(
        'role'
    ) != 'manager':

        return redirect('dashboard')

    return render(request, 'approval.html')


# QUOTATION PAGE
# VENDOR ONLY

def quotation_page(request):

    if request.session.get(
        'role'
    ) != 'vendor':

        return redirect('dashboard')

    return render(
        request,
        'quotation.html'
    )


# LOGOUT

def logout(request):

    request.session.flush()

    return redirect('login')


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

    # Dashboard
    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    # Vendors
    path(
        'vendors/',
        vendors_page,
        name='vendors'
    ),

    # RFQ
    path(
        'rfq/',
        rfq_page,
        name='rfq'
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