import secrets
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from .models import Member, Pair, Request
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from .models import Member, Pair, Request


# --- Authentication Decorator ---
def member_required(view_func):
    """Restricts access to students logged in via OTP session."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        member_id = request.session.get('member_id')
        if not member_id or not Member.objects.filter(id=member_id).exists():
            messages.warning(request, "Please log in to access the portal.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Authentication Views ---
def login_view(request):
    if request.session.get('member_id'):
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        member = Member.objects.filter(email_id__iexact=email).first()

        if not member:
            messages.error(request, "This email is not registered in the student database.")
            return render(request, 'pairs/login.html')

        # Generate a random 6-digit code
        otp_code = f"{secrets.randbelow(900000) + 100000}"

        # Store in session
        request.session['otp_code'] = otp_code
        request.session['otp_email'] = member.email_id

        # Send email (prints to terminal if using Console backend)
        send_mail(
            subject='Your Login Code for Presentation Pairing',
            message=f"Hello {member.full_name},\n\nYour verification code is: {otp_code}\n\nUse this code to log into the pairing portal.",
            from_email="moizpasha9999@gmail.com",
            recipient_list=[member.email_id],
            fail_silently=False,
        )

        messages.info(request, "A verification code has been sent to your email.")
        return redirect('verify_otp')

    return render(request, 'pairs/login.html')


def verify_otp_view(request):
    stored_email = request.session.get('otp_email')
    stored_otp = request.session.get('otp_code')

    if not stored_email or not stored_otp:
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        if entered_otp == stored_otp:
            member = Member.objects.get(email_id=stored_email)
            # Authenticate session
            request.session['member_id'] = member.id

            # Clean up OTP session data
            del request.session['otp_code']
            del request.session['otp_email']

            messages.success(request, f"Welcome, {member.full_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid verification code. Please check and try again.")

    return render(request, 'pairs/verify_otp.html', {'email': stored_email})


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('login')


# --- Portal Views ---
@member_required
def home_view(request):
    current_member = Member.objects.get(id=request.session['member_id'])

    # Find paired students
    paired_ids = set(Pair.objects.values_list('member_1_id', flat=True)).union(
        set(Pair.objects.values_list('member_2_id', flat=True))
    )

    available_members = Member.objects.exclude(id__in=paired_ids).exclude(id=current_member.id)

    requested_ids = Request.objects.filter(
        sent_by=current_member,
        status='PENDING'
    ).values_list('sent_to_id', flat=True)
    if current_member.id in paired_ids:
        messages.info(request, "You are already paired. You cannot send new requests.")
        available_members = Member.objects.none()  # No available members if already paired
    context = {
        'current_member': current_member,
        'available_members': available_members,
        'requested_ids': list(requested_ids),
    }
    return render(request, 'pairs/home.html', context)


@member_required
def send_request_view(request, member_id):
    if request.method == 'POST':
        current_member = Member.objects.get(id=request.session['member_id'])
        target_member = get_object_or_404(Member, id=member_id)

        existing_req = Request.objects.filter(sent_by=current_member, sent_to=target_member, status='PENDING').first()
        if not existing_req:
            Request.objects.create(sent_by=current_member, sent_to=target_member)
            messages.success(request, f"Request sent to {target_member.full_name}!")
        else:
            messages.info(request, "Request already pending.")

    return redirect('home')


@member_required
def requests_list_view(request):
    current_member = Member.objects.get(id=request.session['member_id'])

    sent_requests = Request.objects.filter(sent_by=current_member).order_by('-created_at')
    received_requests = Request.objects.filter(sent_to=current_member).order_by('-created_at')

    context = {
        'sent_requests': sent_requests,
        'received_requests': received_requests,
    }
    return render(request, 'pairs/requests.html', context)


@member_required
def respond_request_view(request, request_id, action):
    if request.method == 'POST':
        req = get_object_or_404(Request, id=request_id)
        if action in ['ACCEPTED', 'REJECTED']:
            req.status = action
            req.save()

            if action == 'ACCEPTED':
                Pair.objects.create(member_1=req.sent_by, member_2=req.sent_to)
                
                # Invalidate any other open requests for both members
                Request.objects.filter(
                    Q(sent_by=req.sent_by) | Q(sent_to=req.sent_by) |
                    Q(sent_by=req.sent_to) | Q(sent_to=req.sent_to),
                    status='PENDING'
                ).exclude(id=req.id).update(status='REJECTED')
                
                messages.success(request, f"Pair formed with {req.sent_by.full_name}!")
            else:
                messages.warning(request, "Request rejected.")

    return redirect('requests_list')




# --- Custom Admin Access Decorator ---
def custom_admin_required(view_func):
    """Restricts access to authenticated staff/admin accounts only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "Staff login required to access the admin portal.")
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Admin Authentication Views ---
def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            messages.success(request, f"Welcome back, Administrator {user.username}!")
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, "Invalid administrator credentials.")

    return render(request, 'pairs/admin_login.html')


def admin_logout_view(request):
    auth_logout(request)
    messages.info(request, "Administrator logged out successfully.")
    return redirect('custom_admin_login')


# --- Admin Dashboard View ---
@custom_admin_required
def admin_dashboard_view(request):
    members = Member.objects.all().order_by('roll_no')
    pairs = Pair.objects.select_related('member_1', 'member_2').all().order_by('-date')

    # Map pairs for instant O(1) lookup
    pair_map = {}
    for p in pairs:
        pair_map[p.member_1_id] = {'partner': p.member_2, 'pair_id': p.id}
        pair_map[p.member_2_id] = {'partner': p.member_1, 'pair_id': p.id}

    # Fetch all pending requests to show request activity
    pending_sent_counts = {}
    for req in Request.objects.filter(status='PENDING').values('sent_by_id'):
        pending_sent_counts[req['sent_by_id']] = pending_sent_counts.get(req['sent_by_id'], 0) + 1

    # Build enriched student status list
    student_records = []
    unpaired_members = []
    for m in members:
        pair_info = pair_map.get(m.id)
        is_paired = pair_info is not None
        partner = pair_info['partner'] if is_paired else None
        pair_id = pair_info['pair_id'] if is_paired else None

        student_records.append({
            'member': m,
            'is_paired': is_paired,
            'partner': partner,
            'pair_id': pair_id,
            'pending_sent_count': pending_sent_counts.get(m.id, 0),
        })

        if not is_paired:
            unpaired_members.append(m)

    total_students = members.count()
    total_paired = len(pair_map)
    total_unpaired = total_students - total_paired

    context = {
        'student_records': student_records,
        'unpaired_members': unpaired_members,
        'pairs': pairs,
        'total_students': total_students,
        'total_paired': total_paired,
        'total_unpaired': total_unpaired,
        'total_pairs': pairs.count(),
    }
    return render(request, 'pairs/admin_dashboard.html', context)


# --- Admin Actions: Create & Delete Pairs ---
@custom_admin_required
def admin_create_pair_view(request):
    if request.method == 'POST':
        member_1_id = request.POST.get('member_1')
        member_2_id = request.POST.get('member_2')

        if not member_1_id or not member_2_id or member_1_id == member_2_id:
            messages.error(request, "Please choose two different students.")
            return redirect('custom_admin_dashboard')

        m1 = get_object_or_404(Member, id=member_1_id)
        m2 = get_object_or_404(Member, id=member_2_id)

        # Check if already paired
        m1_paired = Pair.objects.filter(Q(member_1=m1) | Q(member_2=m1)).exists()
        m2_paired = Pair.objects.filter(Q(member_1=m2) | Q(member_2=m2)).exists()

        if m1_paired or m2_paired:
            messages.error(request, "One of the selected students is already in an active pair.")
            return redirect('custom_admin_dashboard')

        # Create pair
        Pair.objects.create(member_1=m1, member_2=m2)

        # Invalidate open requests for both members
        Request.objects.filter(
            Q(sent_by=m1) | Q(sent_to=m1) | Q(sent_by=m2) | Q(sent_to=m2),
            status='PENDING'
        ).update(status='REJECTED')

        messages.success(request, f"Successfully created pair: {m1.full_name} & {m2.full_name}!")

    return redirect('custom_admin_dashboard')


@custom_admin_required
def admin_delete_pair_view(request, pair_id):
    if request.method == 'POST':
        pair = get_object_or_404(Pair, id=pair_id)
        names = f"{pair.member_1.full_name} & {pair.member_2.full_name}"
        pair.delete()
        messages.warning(request, f"Dissolved pair ({names}). Both students are now marked unpaired.")

    return redirect('custom_admin_dashboard')