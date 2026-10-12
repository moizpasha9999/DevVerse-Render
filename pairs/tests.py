from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from pairs.models import Member, Pair, Request

User = get_user_model()


class MemberAuthenticationTests(TestCase):
    """Tests for Member OTP authentication, sessions, and decorator protection."""

    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(
            full_name="Moiz Pasha",
            email_id="moiz@example.com",
            roll_no="CS-101"
        )
        self.login_url = reverse('login')
        self.verify_otp_url = reverse('verify_otp')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home')

    def test_login_page_renders_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pairs/login.html')

    def test_login_unregistered_email_shows_error(self):
        response = self.client.post(self.login_url, {'email': 'unknown@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pairs/login.html')
        # Ensure no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_login_valid_email_sends_otp_and_redirects(self):
        response = self.client.post(self.login_url, {'email': 'moiz@example.com'})
        
        # Should redirect to verify_otp
        self.assertRedirects(response, self.verify_otp_url)

        # Check session data
        session = self.client.session
        self.assertIn('otp_code', session)
        self.assertEqual(session['otp_email'], self.member.email_id)

        # Check that email was sent using Django's test mail outbox
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertIn(session['otp_code'], sent_email.body)
        self.assertIn(self.member.email_id, sent_email.to)

    def test_verify_otp_without_session_redirects_to_login(self):
        response = self.client.get(self.verify_otp_url)
        self.assertRedirects(response, self.login_url)

    def test_verify_otp_incorrect_code(self):
        # Seed session with OTP
        session = self.client.session
        session['otp_code'] = '123456'
        session['otp_email'] = self.member.email_id
        session.save()

        response = self.client.post(self.verify_otp_url, {'otp': '999999'})
        self.assertEqual(response.status_code, 200)
        # Ensure member is NOT authenticated
        self.assertNotIn('member_id', self.client.session)

    def test_verify_otp_correct_code_logs_in(self):
        session = self.client.session
        session['otp_code'] = '123456'
        session['otp_email'] = self.member.email_id
        session.save()

        response = self.client.post(self.verify_otp_url, {'otp': '123456'})
        self.assertRedirects(response, self.home_url)

        # Ensure member_id is stored and OTP data is cleared
        session = self.client.session
        self.assertEqual(session.get('member_id'), self.member.id)
        self.assertNotIn('otp_code', session)
        self.assertNotIn('otp_email', session)

    def test_member_required_decorator_blocks_unauthenticated_user(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, self.login_url)

    def test_logout_flushes_session(self):
        # Set logged in state
        session = self.client.session
        session['member_id'] = self.member.id
        session.save()

        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn('member_id', self.client.session)


class PairingPortalWorkflowTests(TestCase):
    """Tests student portal features: sending requests, pairing, and mutual exclusion."""

    def setUp(self):
        self.client = Client()
        self.m1 = Member.objects.create(full_name="Alice", email_id="alice@test.com", roll_no="1")
        self.m2 = Member.objects.create(full_name="Bob", email_id="bob@test.com", roll_no="2")
        self.m3 = Member.objects.create(full_name="Charlie", email_id="charlie@test.com", roll_no="3")

        # Log in as Alice (m1) by default
        session = self.client.session
        session['member_id'] = self.m1.id
        session.save()

    def test_home_view_shows_unpaired_members(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.m2, response.context['available_members'])
        self.assertIn(self.m3, response.context['available_members'])
        self.assertNotIn(self.m1, response.context['available_members'])

    def test_send_request(self):
        url = reverse('send_request', kwargs={'member_id': self.m2.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('home'))

        self.assertTrue(
            Request.objects.filter(sent_by=self.m1, sent_to=self.m2, status='PENDING').exists()
        )

    def test_send_duplicate_request_does_not_create_multiple(self):
        Request.objects.create(sent_by=self.m1, sent_to=self.m2, status='PENDING')
        url = reverse('send_request', kwargs={'member_id': self.m2.id})
        self.client.post(url)

        self.assertEqual(
            Request.objects.filter(sent_by=self.m1, sent_to=self.m2, status='PENDING').count(), 
            1
        )

    def test_accept_request_creates_pair_and_rejects_other_open_requests(self):
        # Alice sent request to Bob
        req_alice_to_bob = Request.objects.create(sent_by=self.m1, sent_to=self.m2, status='PENDING')
        # Charlie also sent request to Bob
        req_charlie_to_bob = Request.objects.create(sent_by=self.m3, sent_to=self.m2, status='PENDING')

        # Switch session to Bob to respond
        session = self.client.session
        session['member_id'] = self.m2.id
        session.save()

        respond_url = reverse('respond_request', kwargs={'request_id': req_alice_to_bob.id, 'action': 'ACCEPTED'})
        response = self.client.post(respond_url)
        self.assertRedirects(response, reverse('requests_list'))

        # Check Pair is created
        self.assertTrue(Pair.objects.filter(member_1=self.m1, member_2=self.m2).exists())

        # Check Charlie's request was automatically rejected
        req_charlie_to_bob.refresh_from_db()
        self.assertEqual(req_charlie_to_bob.status, 'REJECTED')

    def test_reject_request(self):
        req = Request.objects.create(sent_by=self.m2, sent_to=self.m1, status='PENDING')
        respond_url = reverse('respond_request', kwargs={'request_id': req.id, 'action': 'REJECTED'})
        
        response = self.client.post(respond_url)
        self.assertRedirects(response, reverse('requests_list'))

        req.refresh_from_db()
        self.assertEqual(req.status, 'REJECTED')
        self.assertFalse(Pair.objects.exists())


class CustomAdminTests(TestCase):
    """Tests for custom admin dashboard, pair creation, and pair deletion."""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_user',
            password='Password123!',
            is_staff=True
        )
        self.non_staff_user = User.objects.create_user(
            username='regular_user',
            password='Password123!',
            is_staff=False
        )
        self.m1 = Member.objects.create(full_name="Member One", email_id="m1@test.com", roll_no="10")
        self.m2 = Member.objects.create(full_name="Member Two", email_id="m2@test.com", roll_no="11")

    def test_non_staff_blocked_from_admin_dashboard(self):
        # An unauthenticated or non-staff user should be redirected
        response = self.client.get(reverse('custom_admin_dashboard'))
        self.assertRedirects(response, reverse('custom_admin_login'))

    def test_staff_login_and_dashboard_access(self):
        login_url = reverse('custom_admin_login')
        response = self.client.post(login_url, {
            'username': 'admin_user',
            'password': 'Password123!'
        })
        self.assertRedirects(response, reverse('custom_admin_dashboard'))

        dashboard_response = self.client.get(reverse('custom_admin_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertTemplateUsed(dashboard_response, 'pairs/admin_dashboard.html')

    def test_admin_create_pair_success(self):
        self.client.force_login(self.admin_user)

        url = reverse('admin_create_pair')
        response = self.client.post(url, {
            'member_1': self.m1.id,
            'member_2': self.m2.id,
        })
        self.assertRedirects(response, reverse('custom_admin_dashboard'))
        self.assertTrue(Pair.objects.filter(member_1=self.m1, member_2=self.m2).exists())

    def test_admin_create_pair_same_member_rejected(self):
        self.client.force_login(self.admin_user)

        url = reverse('admin_create_pair')
        response = self.client.post(url, {
            'member_1': self.m1.id,
            'member_2': self.m1.id,
        })
        self.assertRedirects(response, reverse('custom_admin_dashboard'))
        self.assertFalse(Pair.objects.exists())

    def test_admin_delete_pair_dissolves_pair(self):
        self.client.force_login(self.admin_user)
        pair = Pair.objects.create(member_1=self.m1, member_2=self.m2)

        delete_url = reverse('admin_delete_pair', kwargs={'pair_id': pair.id})
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse('custom_admin_dashboard'))

        self.assertFalse(Pair.objects.filter(id=pair.id).exists())