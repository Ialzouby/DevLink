from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.test import Client
from django.test import RequestFactory
from django.test import RequestFactory, Client
from django.test import RequestFactory, TestCase
from django.test import TestCase, Client
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now
from projects.forms import CustomUserCreationForm
from projects.forms import MessageForm
from projects.forms import ProjectForm
from projects.forms import RatingForm
from projects.forms import UserProfileForm
from projects.forms import UserSettingsForm
from projects.models import Comment, Project
from projects.models import Follow
from projects.models import Message
from projects.models import Notification
from projects.models import Project
from projects.models import Project, Comment
from projects.models import Project, Comment, JoinRequest, Update
from projects.models import Project, JoinRequest
from projects.models import Project, JoinRequest, Comment
from projects.models import Project, JoinRequest, Update
from projects.models import Project, UserProfile
from projects.models import UserProfile
from projects.views import active_conversations
from projects.views import check_username_email
from projects.views import create_project
from projects.views import custom_login
from projects.views import delete_account
from projects.views import delete_comment
from projects.views import delete_notification
from projects.views import delete_project
from projects.views import edit_profile
from projects.views import edit_project
from projects.views import follow_user
from projects.views import help_page
from projects.views import home
from projects.views import landing_page
from projects.views import mark_as_read
from projects.views import message_thread
from projects.views import message_thread_partial
from projects.views import network
from projects.views import notifications_view
from projects.views import profile
from projects.views import project
from projects.views import project_detail
from projects.views import register
from projects.views import search_users
from projects.views import settings_page
from projects.views import toggle_project_status
from projects.views import unfollow_user
from projects.views import upload_banner
from unittest.mock import patch
from unittest.mock import patch, MagicMock
import json
import pytest

class TestViews:

    @pytest.fixture
    def authenticated_user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def factory(self):
        return RequestFactory()

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(title='Test Project', owner=user)

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def rf(self):
        return RequestFactory()

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='12345')

    def setUp_10(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )

    def setUp_11(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def setUp_12(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            owner=self.user
        )

    def setUp_13(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            topic='Science',
            owner=self.user,
            created_at=timezone.now()
        )
        UserProfile.objects.create(user=self.user, points=100)

    def setUp_14(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            topic='Technology',
            owner=self.user,
            created_at=timezone.now()
        )
        UserProfile.objects.create(user=self.user, points=100)

    def setUp_15(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project1 = Project.objects.create(
            title='Test Project 1',
            description='Test Description 1',
            topic='Technology',
            owner=self.user
        )
        self.project2 = Project.objects.create(
            title='Test Project 2',
            description='Test Description 2',
            topic='Science',
            owner=self.user,
            completed=True
        )
        UserProfile.objects.create(user=self.user, points=100)

    def setUp_16(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='testuser1', password='12345')
        self.user2 = User.objects.create_user(username='testuser2', password='12345')

    def setUp_17(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='This is a test project',
            owner=self.user
        )

    def setUp_18(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        UserProfile.objects.create(user=self.user1, points=10)
        UserProfile.objects.create(user=self.user2, points=20)

    def setUp_19(self):
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')
        UserProfile.objects.create(user=self.user1, grade_level='Freshman', concentration='Computer Science', points=100)
        UserProfile.objects.create(user=self.user2, grade_level='Junior', concentration='Data Science', points=200)

    def setUp_2(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user)

    def setUp_20(self):
        self.factory = RequestFactory()
        self.sender = User.objects.create_user(username='sender', password='testpass123')
        self.recipient = User.objects.create_user(username='recipient', password='testpass123')

    def setUp_21(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipient = User.objects.create_user(username='recipient', password='12345')
        self.active_conversations_url = reverse('active_conversations')

    def setUp_22(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipient = User.objects.create_user(username='recipient', password='12345')

    def setUp_23(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='testpass123')

    def setUp_24(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.notification = Notification.objects.create(user=self.user, message='Test notification')

    def setUp_25(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.notification = Notification.objects.create(user=self.user, content='Test notification')
        self.delete_notification_url = reverse('delete_notification', args=[self.notification.id])

    def setUp_26(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            owner=self.user
        )
        self.delete_url = reverse('delete_project', args=[self.project.id])

    def setUp_27(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            owner=self.user
        )
        self.edit_project_url = reverse('edit_project', args=[self.project.id])

    def setUp_28(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.recipient = User.objects.create_user(username='recipient', email='recipient@example.com', password='recipientpass123')

    def setUp_29(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_to_follow = User.objects.create_user(username='followme', password='12345')

    def setUp_3(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.user_profile = UserProfile.objects.create(user=self.user)

    def setUp_30(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_to_unfollow = User.objects.create_user(username='userunfollow', password='12345')

    def setUp_4(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def setUp_5(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def setUp_6(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.user_profile = UserProfile.objects.create(user=self.user, skills='Python,Django,JavaScript')

    def setUp_7(self):
        self.factory = RequestFactory()

    def setUp_8(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.home_url = reverse('home')

    def setUp_9(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.home_url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def setup(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_profile = UserProfile.objects.create(user=self.user)

    @pytest.fixture
    def setup_2(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=self.user)

    @pytest.fixture
    def setup_3(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)

    @pytest.fixture(autouse=True)
    def setup_4(self):
        self.factory = RequestFactory()
        self.client = Client()

    @pytest.fixture
    def setup_5(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(title='Test Project', owner=self.user)

    @pytest.fixture
    def setup_6(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            owner=self.user,
            completed=False
        )

    @pytest.fixture
    def setup_7(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def setup_8(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipient = User.objects.create_user(username='recipient', password='12345')

    @pytest.fixture(autouse=True)
    def setup_9(self):
        self.factory = RequestFactory()
        self.existing_user = User.objects.create_user(username='existinguser', email='existing@example.com')

    @pytest.fixture
    def setup_comment(self, setup_user, setup_project):
        return Comment.objects.create(user=setup_user, project=setup_project, content='Test Comment')

    @pytest.fixture
    def setup_data(self):
        # Create some test data
        self.user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=self.user, points=100)
        Project.objects.create(title="Test Project", description="Test Description", topic="Web Development", owner=self.user)
        Project.objects.create(title="Another Project", description="Another Description", topic="Mobile Development", owner=self.user, created_at=timezone.now() - timedelta(days=10))

    @pytest.fixture
    def setup_data_2(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=self.user)
        Project.objects.create(
            title='Test Project',
            description='Test Description',
            topic='Technology',
            owner=self.user,
            created_at=timezone.now() - timedelta(days=10)
        )

    @pytest.fixture
    def setup_data_3(self):
        # Create test data
        self.user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=self.user, points=100)
        
        Project.objects.create(
            title='Test Project 1',
            description='Description 1',
            topic='Web Development',
            owner=self.user,
            created_at=timezone.now() - timedelta(days=10),
            completed=True
        )
        Project.objects.create(
            title='Test Project 2',
            description='Description 2',
            topic='Mobile Development',
            owner=self.user,
            created_at=timezone.now() - timedelta(days=5),
            completed=False
        )

    @pytest.fixture
    def setup_data_4(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(title='Test Project', owner=self.user)

    @pytest.fixture
    def setup_edit_project(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(id=1, title='Test Project', description='Test Description', owner=self.user)

    @pytest.fixture
    def setup_notification(self, setup_user):
        return Notification.objects.create(user=setup_user, message='Test notification')

    @pytest.fixture
    def setup_profile(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = UserProfile.objects.create(user=self.user)

    @pytest.fixture
    def setup_project(self):
        return Project.objects.create(title='Test Project', description='Test Description')

    @pytest.fixture
    def setup_request(self):
        factory = RequestFactory()
        user = User.objects.create_user(username='testuser', password='12345')
        request = factory.post('/project/1/')
        request.user = user

        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        return request

    @pytest.fixture
    def setup_request_2(self, setup_user):
        request = RequestFactory().get('/conversations/')
        request.user = setup_user
        return request

    @pytest.fixture
    def setup_request_3(self):
        self.factory = RequestFactory()

    @pytest.fixture
    def setup_request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def setup_user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def setup_users(self):
        User.objects.create_user(username='user1', password='password1')
        User.objects.create_user(username='user2', password='password2')

    @pytest.fixture
    def setup_users_2(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.recipient = User.objects.create_user(username='recipient', password='12345')

    @pytest.fixture
    def setup_users_3(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_to_follow = User.objects.create_user(username='usertofollow', password='12345')

    @pytest.fixture
    def setup_users_4(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user_to_unfollow = User.objects.create_user(username='userunfollow', password='12345')
        self.factory = RequestFactory()

    def test_active_conversations_2(self):
        """
        Test active_conversations view when a valid message is sent to a recipient.
        """
        self.client.login(username='testuser', password='12345')
        
        # Create a message to establish a conversation
        Message.objects.create(sender=self.user, recipient=self.recipient, content='Test message')

        # Prepare POST data
        post_data = {
            'content': 'New test message'
        }

        # Make a POST request with a recipient
        response = self.client.post(
            f'{self.active_conversations_url}?recipient={self.recipient.username}',
            data=post_data
        )

        # Check if the response is a redirect
        self.assertRedirects(response, f'/conversations/?recipient={self.recipient.username}')

        # Verify that a new message was created
        self.assertTrue(Message.objects.filter(
            sender=self.user,
            recipient=self.recipient,
            content='New test message'
        ).exists())

        # Check if the message appears in the conversation
        conversation_messages = Message.objects.filter(
            (Q(sender=self.user) & Q(recipient=self.recipient)) |
            (Q(sender=self.recipient) & Q(recipient=self.user))
        ).order_by('timestamp')

        self.assertEqual(conversation_messages.count(), 2)  # Original message + new message
        self.assertEqual(conversation_messages.last().content, 'New test message')

    def test_active_conversations_3(self):
        """
        Test active_conversations view with search query, recipient, and invalid POST data.
        """
        # Create a GET request with search query and recipient
        url = reverse('active_conversations')
        request = self.factory.get(f"{url}?q=test&recipient={self.recipient.username}")
        request.user = self.user

        # Create some test messages
        Message.objects.create(sender=self.user, recipient=self.recipient, content="Test message")

        # Simulate a POST request with invalid form data
        post_data = {'content': ''}  # Empty content, which should be invalid
        request.method = 'POST'
        request.POST = post_data

        # Call the view
        response = active_conversations(request)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/active_conversations.html')

        # Check if the context contains the expected data
        self.assertIn('conversation_users', response.context)
        self.assertIn('recipient', response.context)
        self.assertIn('messages', response.context)
        self.assertIn('form', response.context)
        self.assertIn('search_results', response.context)

        # Verify that the form is invalid
        self.assertFalse(response.context['form'].is_valid())

        # Check if the search results are present
        self.assertTrue(len(response.context['search_results']) > 0)

        # Verify that the recipient is set correctly
        self.assertEqual(response.context['recipient'], self.recipient)

        # Check if messages are loaded for the conversation
        self.assertTrue(len(response.context['messages']) > 0)

        # Verify that conversation_users includes the recipient
        self.assertIn(self.recipient, response.context['conversation_users'])

    def test_active_conversations_4(self):
        """
        Test active_conversations view with search query and no recipient username.
        """
        # Create some test messages
        Message.objects.create(sender=self.user, recipient=self.other_user, content="Test message")

        # Create a GET request with a search query
        request = self.factory.get('/conversations/', {'q': 'other'})
        request.user = self.user

        # Call the view
        response = active_conversations(request)

        # Check that the response is rendered correctly
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/active_conversations.html')

        # Check that the context contains the expected data
        context = response.context_data
        self.assertIn('conversation_users', context)
        self.assertIn('recipient', context)
        self.assertIn('messages', context)
        self.assertIn('form', context)
        self.assertIn('search_results', context)

        # Check that the search results are correct
        search_results = context['search_results']
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].username, 'otheruser')

        # Check that there's no recipient
        self.assertIsNone(context['recipient'])

        # Check that the conversation_users queryset is correct
        conversation_users = context['conversation_users']
        self.assertEqual(len(conversation_users), 1)
        self.assertEqual(conversation_users[0], self.other_user)

        # Check that the messages list is empty (no recipient selected)
        self.assertEqual(len(context['messages']), 0)

    def test_active_conversations_empty_search_query(self, setup_request_2):
        """
        Test active_conversations with an empty search query.
        """
        setup_request_2.GET = {'q': ''}
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'search_results' in response.context
        assert len(response.context['search_results']) == 0

    def test_active_conversations_invalid_post_data(self, setup_request_2):
        """
        Test active_conversations with invalid POST data.
        """
        setup_request_2.method = 'POST'
        setup_request_2.POST = {'content': ''}  # Empty message content
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_active_conversations_invalid_recipient(self, setup_request_2):
        """
        Test active_conversations with an invalid recipient username.
        """
        setup_request_2.GET = {'recipient': 'nonexistent_user'}
        with pytest.raises(Http404):
            active_conversations(setup_request_2)

    def test_active_conversations_invalid_search_query_type(self, setup_request_2):
        """
        Test active_conversations with an invalid search query type.
        """
        setup_request_2.GET = {'q': 123}  # Integer instead of string
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'search_results' in response.context
        assert isinstance(response.context['search_results'], QuerySet)

    def test_active_conversations_message_limit(self, setup_request_2, setup_user):
        """
        Test active_conversations respects the message limit of 50.
        """
        recipient = User.objects.create_user(username='recipient', password='12345')
        for i in range(60):  # Create 60 messages
            Message.objects.create(sender=setup_user, recipient=recipient, content=f"Message {i}")
        
        setup_request_2.GET = {'recipient': 'recipient'}
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'messages' in response.context
        assert len(response.context['messages']) == 50

    def test_active_conversations_no_conversations(self, setup_request_2):
        """
        Test active_conversations when the user has no conversations.
        """
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'conversation_users' in response.context
        assert len(response.context['conversation_users']) == 0

    def test_active_conversations_request_method_not_allowed(self, setup_request_2):
        """
        Test active_conversations with a request method that's not GET or POST.
        """
        setup_request_2.method = 'PUT'
        response = active_conversations(setup_request_2)
        assert response.status_code == 200

    def test_active_conversations_with_search_and_new_message(self):
        """
        Test active_conversations view with search query, recipient, and new message creation.
        """
        # Create a message to establish a conversation
        Message.objects.create(sender=self.user, recipient=self.recipient, content="Test message")

        # Prepare the request
        url = reverse('active_conversations')
        data = {
            'q': 'recipient',
            'recipient': self.recipient.username,
            'content': 'New test message'
        }
        request = self.factory.post(url, data)
        request.user = self.user

        # Add GET parameters
        request.GET = request.GET.copy()
        request.GET['q'] = 'recipient'
        request.GET['recipient'] = self.recipient.username

        # Mock the form to always be valid
        def mock_form_is_valid(self):
            return True

        MessageForm.is_valid = mock_form_is_valid

        # Call the view
        response = active_conversations(request)

        # Check if a new message was created
        self.assertEqual(Message.objects.count(), 2)
        
        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/conversations/?recipient={self.recipient.username}')

        # Verify that the search query worked
        search_results = User.objects.filter(
            Q(username__icontains='recipient') |
            Q(first_name__icontains='recipient') |
            Q(last_name__icontains='recipient')
        ).exclude(id=self.user.id)
        self.assertIn(self.recipient, search_results)

        # Verify that the conversation exists
        conversation = Message.objects.filter(
            (Q(sender=self.user) & Q(recipient=self.recipient)) |
            (Q(sender=self.recipient) & Q(recipient=self.user))
        ).exists()
        self.assertTrue(conversation)

    def test_active_conversations_xss_attempt(self, setup_request_2):
        """
        Test active_conversations with a potential XSS attack in the search query.
        """
        setup_request_2.GET = {'q': '<script>alert("XSS")</script>'}
        response = active_conversations(setup_request_2)
        assert response.status_code == 200
        assert 'search_results' in response.context
        assert len(response.context['search_results']) == 0

    @pytest.mark.django_db
    def test_check_username_email_1(self):
        """
        Test that check_username_email returns correct response when username and email don't exist
        """
        # Create a request factory
        factory = RequestFactory()

        # Create a GET request with non-existent username and email
        request = factory.get('/check_username_email/', {'username': 'newuser', 'email': 'newuser@example.com'})

        # Call the view function
        response = check_username_email(request)

        # Check that the response is a JsonResponse
        assert isinstance(response, JsonResponse)

        # Check the content of the response
        content = response.json()
        assert content == {'username_exists': False, 'email_exists': False}

    @pytest.mark.django_db
    def test_check_username_email_2(self):
        """
        Test that check_username_email returns correct response when username exists but email doesn't
        """
        # Create a user with a known username
        User.objects.create_user(username='existinguser', email='existing@example.com', password='testpass123')

        # Create a request factory
        factory = RequestFactory()

        # Create a GET request with existing username and non-existent email
        request = factory.get('/check_username_email/', {'username': 'existinguser', 'email': 'newuser@example.com'})

        # Call the view function
        response = check_username_email(request)

        # Check that the response is a JsonResponse
        assert isinstance(response, JsonResponse)

        # Check the content of the response
        content = response.json()
        assert content == {'username_exists': True, 'email_exists': False}

    @pytest.mark.django_db
    def test_check_username_email_3(self):
        """
        Test that check_username_email returns correct response when both username and email exist
        """
        # Create a user with known username and email
        User.objects.create_user(username='existinguser', email='existing@example.com', password='testpass123')

        # Create a request factory
        factory = RequestFactory()

        # Create a GET request with existing username and email
        request = factory.get('/check_username_email/', {'username': 'existinguser', 'email': 'existing@example.com'})

        # Call the view function
        response = check_username_email(request)

        # Check that the response is a JsonResponse
        assert isinstance(response, JsonResponse)

        # Check the content of the response
        content = response.json()
        assert content == {'username_exists': True, 'email_exists': True}

    def test_check_username_email_case_insensitive(self):
        """Test check_username_email is case-insensitive for username and email"""
        request = self.factory.get('/check_username_email/', {'username': 'ExistingUser', 'email': 'EXISTING@example.com'})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': True, 'email_exists': True}

    def test_check_username_email_empty_input(self):
        """Test check_username_email with empty input"""
        request = self.factory.get('/check_username_email/')
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': False, 'email_exists': False}

    def test_check_username_email_existing_user(self):
        """Test check_username_email with existing user data"""
        request = self.factory.get('/check_username_email/', {'username': 'existinguser', 'email': 'existing@example.com'})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': True, 'email_exists': True}

    def test_check_username_email_incorrect_type(self):
        """Test check_username_email with incorrect input type"""
        request = self.factory.get('/check_username_email/', {'username': 123, 'email': 456})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': False, 'email_exists': False}

    def test_check_username_email_invalid_input(self):
        """Test check_username_email with invalid input"""
        request = self.factory.get('/check_username_email/', {'username': ' ', 'email': 'invalid'})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': False, 'email_exists': False}

    def test_check_username_email_long_input(self):
        """Test check_username_email with input outside accepted bounds"""
        long_string = 'a' * 151  # Assuming 150 is the max length
        request = self.factory.get('/check_username_email/', {'username': long_string, 'email': long_string})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': False, 'email_exists': False}

    def test_check_username_email_non_existent_user(self):
        """Test check_username_email with non-existent user data"""
        request = self.factory.get('/check_username_email/', {'username': 'newuser', 'email': 'new@example.com'})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': False, 'email_exists': False}

    def test_check_username_email_partially_existing(self):
        """Test check_username_email with existing username but new email"""
        request = self.factory.get('/check_username_email/', {'username': 'existinguser', 'email': 'new@example.com'})
        response = check_username_email(request)
        assert isinstance(response, JsonResponse)
        data = response.json()
        assert data == {'username_exists': True, 'email_exists': False}

    def test_create_project_unauthenticated(self):
        """
        Test creating a project when user is not authenticated.
        """
        request = self.factory.post(reverse('create_project'), data={})
        request.user = AnonymousUser()

        with pytest.raises(TypeError):
            create_project(request)

    def test_create_project_valid_form(self):
        """
        Test creating a project with valid form data.
        Expects a redirect to home page and a new project created.
        """
        url = reverse('create_project')
        data = {
            'title': 'Test Project',
            'description': 'This is a test project',
            'topic': 'Web Development',
            'max_members': 5
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

        # Check if the project was created
        self.assertTrue(Project.objects.filter(title='Test Project').exists())

        # Check if the project is associated with the logged-in user
        project = Project.objects.get(title='Test Project')
        self.assertEqual(project.owner, self.user)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project created successfully.')

    def test_create_project_with_empty_form(self, setup_7):
        """
        Test creating a project with an empty form.
        """
        request = self.factory.post(reverse('create_project'), data={})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = create_project(request)
        
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert response.context_data['form'].errors

    def test_create_project_with_incorrect_type(self, setup_7):
        """
        Test creating a project with incorrect input types.
        """
        data = {
            'title': 123,  # Should be string
            'description': 'Test description',
            'topic': 'TEST',
        }
        request = self.factory.post(reverse('create_project'), data=data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = create_project(request)
        
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert response.context_data['form'].errors

    def test_create_project_with_invalid_input(self, setup_7):
        """
        Test creating a project with invalid input (e.g., title too long).
        """
        data = {
            'title': 'A' * 256,  # Assuming max length is 255
            'description': 'Test description',
            'topic': 'TEST',
        }
        request = self.factory.post(reverse('create_project'), data=data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = create_project(request)
        
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert 'title' in response.context_data['form'].errors

    def test_create_project_with_non_existent_topic(self, setup_7):
        """
        Test creating a project with a non-existent topic.
        """
        data = {
            'title': 'Test Project',
            'description': 'Test description',
            'topic': 'NON_EXISTENT_TOPIC',
        }
        request = self.factory.post(reverse('create_project'), data=data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = create_project(request)
        
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert 'topic' in response.context_data['form'].errors

    def test_custom_login_2(self):
        """
        Test custom_login when user is not authenticated.
        It should return the LoginView for unauthenticated users.
        """
        request = self.factory.get(reverse('login'))
        request.user = AnonymousUser()

        response = custom_login(request)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, auth_views.LoginView.as_view()(request).__class__)
        self.assertEqual(response.template_name[0], 'projects/login.html')

    def test_custom_login_authenticated_user(self):
        """
        Test that authenticated users are redirected to home page
        when attempting to access the login page.
        """
        request = self.factory.get(reverse('login'))
        request.user = self.user
        response = custom_login(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_custom_login_authenticated_user_2(self, factory, authenticated_user):
        """
        Test that authenticated users are redirected to home page.
        """
        request = factory.get('/login/')
        request.user = authenticated_user
        response = custom_login(request)
        assert isinstance(response, redirect)
        assert response.url == reverse('home')

    def test_custom_login_invalid_method(self, factory):
        """
        Test that invalid HTTP methods are rejected.
        """
        request = factory.put('/login/')
        request.user = User()
        request.user.is_authenticated = False

        with pytest.raises(ValueError):
            custom_login(request)

    def test_custom_login_missing_user(self, factory):
        """
        Test handling of requests with missing user attribute.
        """
        request = factory.get('/login/')
        delattr(request, 'user')

        with pytest.raises(AttributeError):
            custom_login(request)

    def test_custom_login_post_request(self, factory):
        """
        Test that POST requests are handled correctly.
        """
        request = factory.post('/login/', data={'username': 'testuser', 'password': '12345'})
        request.user = User()
        request.user.is_authenticated = False

        with pytest.raises(ValueError):
            custom_login(request)

    def test_custom_login_unauthenticated_user(self, factory, monkeypatch):
        """
        Test that unauthenticated users are shown the login page.
        """
        request = factory.get('/login/')
        request.user = User()
        request.user.is_authenticated = False

        mock_login_view = pytest.Mock(return_value="Login page")
        monkeypatch.setattr(auth_views.LoginView, 'as_view', lambda **kwargs: mock_login_view)

        response = custom_login(request)
        assert response == "Login page"
        mock_login_view.assert_called_once_with(request)

    def test_delete_account_database_error(self):
        """
        Test delete_account when a database error occurs during user deletion
        """
        request = self.factory.post(reverse('delete_account'))
        request.user = self.user
        
        # Mock the user.delete() method to raise an exception
        def mock_delete():
            raise Exception("Database error")
        
        request.user.delete = mock_delete
        
        # Add message middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = delete_account(request)
        assert response.status_code == 302
        assert response.url == reverse('home')
        
        # Check if an error message was added
        messages = list(messages)
        assert len(messages) == 1
        assert str(messages[0]) == "An error occurred while deleting your account. Please try again."

    def test_delete_account_get_request(self):
        """
        Test that GET request to delete_account renders the confirmation page.
        """
        response = self.client.get(reverse('delete_account'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/delete_account.html')

    def test_delete_account_get_request_2(self):
        """
        Test delete_account with a GET request instead of POST
        """
        request = self.factory.get(reverse('delete_account'))
        request.user = self.user
        response = delete_account(request)
        assert response.status_code == 200
        assert 'projects/delete_account.html' in [t.name for t in response.templates]

    def test_delete_account_invalid_csrf_token(self):
        """
        Test delete_account with an invalid CSRF token
        """
        request = self.factory.post(reverse('delete_account'))
        request.user = self.user
        response = delete_account(request)
        assert response.status_code == 403

    def test_delete_account_successful(self):
        """
        Test successful account deletion when POST request is made.
        """
        response = self.client.post(reverse('delete_account'))
        
        # Check if the user is redirected to home page
        self.assertRedirects(response, reverse('home'))
        
        # Check if the user is deleted
        self.assertFalse(User.objects.filter(username='testuser').exists())
        
        # Check if success message is added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Your account has been deleted successfully.")

    def test_delete_account_unauthenticated(self):
        """
        Test that unauthenticated users are redirected to login page.
        """
        self.client.logout()
        response = self.client.post(reverse('delete_account'))
        
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={reverse("delete_account")}')

    def test_delete_account_unauthenticated_user(self):
        """
        Test delete_account with an unauthenticated user
        """
        request = self.factory.post(reverse('delete_account'))
        request.user = None
        response = delete_account(request)
        assert response.status_code == 302
        assert response.url.startswith(reverse('login'))

    def test_delete_account_user_not_found(self):
        """
        Test delete_account when the user is not found in the database
        """
        request = self.factory.post(reverse('delete_account'))
        request.user = User(username='nonexistent')
        
        # Add message middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        response = delete_account(request)
        assert response.status_code == 302
        assert response.url == reverse('home')
        
        # Check if an error message was added
        messages = list(messages)
        assert len(messages) == 1
        assert str(messages[0]) == "User not found. Unable to delete account."

    @pytest.mark.django_db
    def test_delete_comment_1(self):
        """
        Test successful deletion of a comment by the user who created it
        """
        # Create a test user
        user = User.objects.create_user(username='testuser', password='12345')
        client = Client()
        client.login(username='testuser', password='12345')

        # Create a test project
        project = Project.objects.create(title='Test Project', owner=user)

        # Create a test comment
        comment = Comment.objects.create(project=project, user=user, content='Test comment')

        # Send a POST request to delete the comment
        response = client.post(reverse('delete_comment', kwargs={'pk': comment.pk}))

        # Check if the comment was deleted
        assert Comment.objects.filter(pk=comment.pk).count() == 0

        # Check if the response redirects to the project page
        assert response.status_code == 302
        assert response.url == reverse('project', kwargs={'project_id': project.id})

        # Check if a success message was added
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert str(messages[0]) == 'Comment deleted successfully.'

    def test_delete_comment_database_error(self, setup_user, setup_comment, monkeypatch):
        """
        Test delete_comment when a database error occurs
        """
        def mock_delete(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(Comment, 'delete', mock_delete)

        factory = RequestFactory()
        request = factory.post(reverse('delete_comment', kwargs={'pk': setup_comment.pk}))
        request.user = setup_user

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with pytest.raises(Exception, match="Database error"):
            delete_comment(request, pk=setup_comment.pk)

    def test_delete_comment_get_request(self, setup_user, setup_comment):
        """
        Test delete_comment with a GET request instead of POST
        """
        factory = RequestFactory()
        request = factory.get(reverse('delete_comment', kwargs={'pk': setup_comment.pk}))
        request.user = setup_user

        response = delete_comment(request, pk=setup_comment.pk)
        assert response.status_code == 405

    def test_delete_comment_invalid_pk(self, setup_user):
        """
        Test delete_comment with an invalid primary key (pk)
        """
        factory = RequestFactory()
        request = factory.post(reverse('delete_comment', kwargs={'pk': 9999}))
        request.user = setup_user

        with pytest.raises(Http404):
            delete_comment(request, pk=9999)

    def test_delete_comment_non_existent_project(self, setup_user, setup_comment):
        """
        Test delete_comment when the associated project doesn't exist
        """
        setup_comment.project.delete()
        factory = RequestFactory()
        request = factory.post(reverse('delete_comment', kwargs={'pk': setup_comment.pk}))
        request.user = setup_user

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with pytest.raises(Http404):
            delete_comment(request, pk=setup_comment.pk)

    def test_delete_comment_unauthorized_user(self, setup_user, setup_comment):
        """
        Test delete_comment with a user who didn't create the comment
        """
        unauthorized_user = User.objects.create_user(username='unauthorized', password='12345')
        factory = RequestFactory()
        request = factory.post(reverse('delete_comment', kwargs={'pk': setup_comment.pk}))
        request.user = unauthorized_user

        with pytest.raises(Http404):
            delete_comment(request, pk=setup_comment.pk)

    def test_delete_notification_database_error(self, client, setup_user, setup_notification, mocker):
        """
        Test deleting a notification when a database error occurs.
        """
        client.force_login(setup_user)
        mocker.patch.object(Notification, 'delete', side_effect=Exception('Database error'))
        
        with pytest.raises(Exception) as excinfo:
            client.post(reverse('delete_notification', kwargs={'notification_id': setup_notification.id}))
        
        assert str(excinfo.value) == 'Database error'

    def test_delete_notification_get_method(self, client, setup_user, setup_notification):
        """
        Test deleting a notification using GET method instead of POST.
        """
        client.force_login(setup_user)
        response = client.get(reverse('delete_notification', kwargs={'notification_id': setup_notification.id}))
        assert response.status_code == 405

    def test_delete_notification_get_request(self):
        """
        Test that GET requests are not allowed for delete_notification
        """
        self.client.force_login(self.user)
        response = self.client.get(self.delete_notification_url)
        self.assertEqual(response.status_code, 405)  # Should return 405 Method Not Allowed
        self.assertTrue(Notification.objects.filter(id=self.notification.id).exists())

    def test_delete_notification_invalid_id(self):
        """
        Test deletion attempt with an invalid notification ID
        """
        self.client.force_login(self.user)
        invalid_url = reverse('delete_notification', args=[99999])  # Assuming this ID doesn't exist
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_delete_notification_invalid_id_2(self, client, setup_user):
        """
        Test deleting a notification with an invalid ID.
        """
        client.force_login(setup_user)
        response = client.post(reverse('delete_notification', kwargs={'notification_id': 9999}))
        assert response.status_code == 404

    def test_delete_notification_invalid_notification_id_type(self, client, setup_user):
        """
        Test deleting a notification with an invalid ID type.
        """
        client.force_login(setup_user)
        response = client.post(reverse('delete_notification', kwargs={'notification_id': 'invalid'}))
        assert response.status_code == 404

    def test_delete_notification_non_existent(self, client, setup_user):
        """
        Test deleting a non-existent notification.
        """
        client.force_login(setup_user)
        non_existent_id = Notification.objects.order_by('-id').first().id + 1
        response = client.post(reverse('delete_notification', kwargs={'notification_id': non_existent_id}))
        assert response.status_code == 404

    def test_delete_notification_success(self):
        """
        Test successful deletion of a notification
        """
        self.client.force_login(self.user)
        response = self.client.post(self.delete_notification_url)
        
        # Check if the response redirects to the notifications view
        self.assertRedirects(response, reverse('notifications_view'))
        
        # Check if the notification was deleted
        self.assertFalse(Notification.objects.filter(id=self.notification.id).exists())
        
        # Check if a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Notification deleted successfully.")

    def test_delete_notification_unauthenticated(self):
        """
        Test deletion attempt by an unauthenticated user
        """
        response = self.client.post(self.delete_notification_url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login page
        self.assertTrue(Notification.objects.filter(id=self.notification.id).exists())

    def test_delete_notification_unauthorized_user(self, client, setup_notification):
        """
        Test deleting a notification by an unauthorized user.
        """
        unauthorized_user = User.objects.create_user(username='unauthorized', password='12345')
        client.force_login(unauthorized_user)
        response = client.post(reverse('delete_notification', kwargs={'notification_id': setup_notification.id}))
        assert response.status_code == 404

    def test_delete_notification_wrong_user(self):
        """
        Test deletion attempt by a user who doesn't own the notification
        """
        other_user = User.objects.create_user(username='otheruser', password='12345')
        self.client.force_login(other_user)
        response = self.client.post(self.delete_notification_url)
        self.assertEqual(response.status_code, 404)  # Should return 404 Not Found
        self.assertTrue(Notification.objects.filter(id=self.notification.id).exists())

    def test_delete_project_database_error(self, setup_data_4, mocker):
        """
        Test database error during project deletion.
        """
        request = self.factory.post(reverse('delete_project', kwargs={'project_id': self.project.id}))
        request.user = self.user

        # Mock the delete method to raise an exception
        mocker.patch.object(Project, 'delete', side_effect=Exception("Database error"))

        # Add message middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with pytest.raises(Exception, match="Database error"):
            delete_project(request, self.project.id)

    def test_delete_project_get_request(self, setup_data_4):
        """
        Test sending a GET request to delete_project view.
        """
        request = self.factory.get(reverse('delete_project', kwargs={'project_id': self.project.id}))
        request.user = self.user

        response = delete_project(request, self.project.id)
        assert response.status_code == 200
        assert 'projects/confirm_delete.html' in [t.name for t in response.templates]

    def test_delete_project_invalid_method(self, setup_data_4):
        """
        Test sending an invalid HTTP method to delete_project view.
        """
        request = self.factory.put(reverse('delete_project', kwargs={'project_id': self.project.id}))
        request.user = self.user

        with pytest.raises(AttributeError):
            delete_project(request, self.project.id)

    def test_delete_project_non_existent_id(self, setup_data_4):
        """
        Test deleting a project with a non-existent ID.
        """
        request = self.factory.post(reverse('delete_project', kwargs={'project_id': 9999}))
        request.user = self.user
        
        with pytest.raises(Http404):
            delete_project(request, 9999)

    def test_delete_project_successful(self):
        """
        Test successful project deletion when POST request is made by the project owner.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.delete_url)
        
        # Check if the response redirects to home
        self.assertRedirects(response, reverse('home'))
        
        # Check if the project was actually deleted
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())
        
        # Check if a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project deleted successfully.')

    def test_delete_project_unauthorized_user(self, setup_data_4):
        """
        Test deleting a project by an unauthorized user.
        """
        unauthorized_user = User.objects.create_user(username='unauthorized', password='12345')
        request = self.factory.post(reverse('delete_project', kwargs={'project_id': self.project.id}))
        request.user = unauthorized_user

        with pytest.raises(Http404):
            delete_project(request, self.project.id)

    def test_edit_profile_2(self):
        """
        Test edit_profile view when POST request is valid, no profile picture is uploaded,
        but a banner picture is uploaded.
        """
        url = reverse('edit_profile')
        request = self.factory.post(url, {
            'bio': 'New bio',
            'skills': 'Python, Django',
            'grade_level': 'Sophomore',
            'concentration': 'Computer Science'
        })
        request.user = self.user
        request.FILES = {'banner_picture': MagicMock()}

        # Add messages middleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Mock the form
        mock_form = MagicMock(spec=UserProfileForm)
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'skills': 'Python, Django',
        }
        mock_form.save.return_value = self.user_profile

        # Mock the upload function
        mock_upload_result = {'url': 'http://example.com/banner.jpg'}
        with patch('projects.views.UserProfileForm', return_value=mock_form), \
             patch('projects.views.upload', return_value=mock_upload_result):
            
            response = edit_profile(request)

        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': self.user.username}))

        # Verify that the user profile was updated
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.banner_picture, 'http://example.com/banner.jpg')
        self.assertEqual(self.user_profile.skills, 'Python,Django')

        # Verify that the form's save method was called
        mock_form.save.assert_called_once()

        # Verify that the upload function was called for the banner picture
        with patch('projects.views.upload') as mock_upload:
            mock_upload.assert_called_once_with(request.FILES['banner_picture'], upload_preset='ml_default')

    def test_edit_profile_3(self, setup):
        """
        Test edit_profile view when a valid form is submitted with a profile picture but without a banner picture.
        """
        request = self.factory.post('/edit_profile/')
        request.user = self.user
        request.FILES = {'profile_picture': MagicMock()}

        # Add messages attribute to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        form_data = {
            'bio': 'New bio',
            'skills': 'Python, Django',
            'linkedin': 'https://linkedin.com/testuser',
            'github': 'https://github.com/testuser'
        }

        with patch('projects.views.UserProfileForm') as MockUserProfileForm, \
             patch('projects.views.upload') as mock_upload, \
             patch('projects.views.messages.success') as mock_messages_success:

            mock_form = MockUserProfileForm.return_value
            mock_form.is_valid.return_value = True
            mock_form.cleaned_data = form_data
            mock_form.save.return_value = self.user_profile

            mock_upload.return_value = {'url': 'https://example.com/profile_pic.jpg'}

            response = edit_profile(request)

            MockUserProfileForm.assert_called_once_with(request.POST, request.FILES, instance=self.user_profile)
            mock_form.save.assert_called_once()
            mock_upload.assert_called_once_with(request.FILES['profile_picture'], upload_preset='ml_default')
            mock_messages_success.assert_called_once()

            assert response.status_code == 302
            assert response.url == reverse('profile', kwargs={'username': self.user.username})

            # Verify that the user profile was updated
            updated_profile = UserProfile.objects.get(user=self.user)
            assert updated_profile.bio == 'New bio'
            assert updated_profile.skills == 'Python,Django'
            assert updated_profile.linkedin == 'https://linkedin.com/testuser'
            assert updated_profile.github == 'https://github.com/testuser'
            assert updated_profile.profile_picture == 'https://example.com/profile_pic.jpg'

    @patch('projects.views.upload')
    def test_edit_profile_cloudinary_exception(self, mock_upload):
        """Test edit_profile when Cloudinary upload raises an exception"""
        mock_upload.side_effect = Exception("Cloudinary upload failed")

        data = {'profile_picture': MagicMock()}
        request = self.factory.post(reverse('edit_profile'), data=data)
        request.user = self.user
        request.FILES = {'profile_picture': MagicMock()}
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('There was an issue uploading your profile picture.', [m.message for m in messages])

    def test_edit_profile_empty_input(self):
        """Test edit_profile with empty input"""
        request = self.factory.post(reverse('edit_profile'), data={})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please correct the errors below.', [m.message for m in messages])

    def test_edit_profile_incorrect_type(self):
        """Test edit_profile with incorrect input type"""
        incorrect_type_data = {
            'grade_level': 123,  # Should be a string
            'skills': ['Python', 'Django'],  # Should be a comma-separated string
        }
        request = self.factory.post(reverse('edit_profile'), data=incorrect_type_data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please correct the errors below.', [m.message for m in messages])

    def test_edit_profile_invalid_input(self):
        """Test edit_profile with invalid input"""
        invalid_data = {
            'linkedin': 'not_a_url',
            'github': 'not_a_url',
            'grade_level': 'invalid_grade',
        }
        request = self.factory.post(reverse('edit_profile'), data=invalid_data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please correct the errors below.', [m.message for m in messages])

    def test_edit_profile_skills_edge_case(self):
        """Test edit_profile with edge case for skills input"""
        data = {
            'skills': '  ,  Python  ,  ,  Django,  ,  ',  # Messy input with extra spaces and commas
        }
        request = self.factory.post(reverse('edit_profile'), data=data)
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.skills, 'Python,Django')

    @patch('projects.views.upload')
    def test_edit_profile_successful_update(self, mock_upload):
        """
        Test that edit_profile successfully updates the user profile with valid form data and file uploads.
        """
        mock_upload.return_value = {'url': 'http://test-url.com/image.jpg'}

        url = reverse('edit_profile')
        request = self.factory.post(url, data={
            'bio': 'New bio',
            'skills': 'Python, Django',
        })
        request.user = self.user
        request.FILES = {
            'profile_picture': SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg"),
            'banner_picture': SimpleUploadedFile("banner.jpg", b"file_content", content_type="image/jpeg"),
        }

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_profile(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': self.user.username}))

        # Refresh the user profile from the database
        self.user_profile.refresh_from_db()

        # Check that the profile was updated
        self.assertEqual(self.user_profile.bio, 'New bio')
        self.assertEqual(self.user_profile.skills, 'Python,Django')
        self.assertEqual(self.user_profile.profile_picture, 'http://test-url.com/image.jpg')
        self.assertEqual(self.user_profile.banner_picture, 'http://test-url.com/image.jpg')

        # Verify that upload was called twice (once for profile picture, once for banner)
        self.assertEqual(mock_upload.call_count, 2)

    def test_edit_project_invalid_form_data(self, setup_edit_project):
        """
        Test edit_project with invalid form data (exceeding max length)
        """
        long_title = 'A' * 256  # Assuming max length is 255
        request = self.factory.post(f'/edit_project/{self.project.id}/', {'title': long_title, 'description': 'Valid description'})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_project(request, self.project.id)
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert response.context_data['form'].errors['title']

    def test_edit_project_invalid_input(self, setup_edit_project):
        """
        Test edit_project with invalid input (empty title)
        """
        request = self.factory.post('/edit_project/1/', {'title': '', 'description': 'Updated Description'})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = edit_project(request, self.project.id)
        assert response.status_code == 200
        assert 'form' in response.context_data
        assert response.context_data['form'].errors['title']

    def test_edit_project_invalid_method(self, setup_edit_project):
        """
        Test edit_project with invalid HTTP method (PUT)
        """
        request = self.factory.put(f'/edit_project/{self.project.id}/')
        request.user = self.user

        response = edit_project(request, self.project.id)
        assert response.status_code == 200
        assert isinstance(response.context_data['form'], ProjectForm)

    def test_edit_project_non_existent_project(self, setup_edit_project):
        """
        Test edit_project with non-existent project ID
        """
        request = self.factory.get('/edit_project/999/')
        request.user = self.user

        with pytest.raises(Http404):
            edit_project(request, 999)

    def test_edit_project_success(self):
        """
        Test successful project edit when form is valid and method is POST.
        """
        self.client.login(username='testuser', password='12345')
        
        data = {
            'title': 'Updated Project Title',
            'description': 'Updated Project Description',
            'topic': 'TOPIC1',  # Assuming 'TOPIC1' is a valid choice in your ProjectForm
        }
        
        response = self.client.post(self.edit_project_url, data)
        
        # Check if the response is a redirect
        self.assertRedirects(response, reverse('project', args=[self.project.id]))
        
        # Refresh the project from the database
        self.project.refresh_from_db()
        
        # Check if the project details were updated
        self.assertEqual(self.project.title, 'Updated Project Title')
        self.assertEqual(self.project.description, 'Updated Project Description')
        
        # Check if a success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Project updated successfully.')

    def test_edit_project_unauthorized_user(self, setup_edit_project):
        """
        Test edit_project with unauthorized user
        """
        unauthorized_user = User.objects.create_user(username='unauthorized', password='12345')
        request = self.factory.get(f'/edit_project/{self.project.id}/')
        request.user = unauthorized_user

        with pytest.raises(Http404):
            edit_project(request, self.project.id)

    def test_follow_user_1(self):
        # Existing test case, kept for completeness
        pass

    def test_follow_user_2(self):
        """
        Test that a user cannot follow themselves.
        """
        # Attempt to follow the same user
        response = self.client.get(reverse('follow_user', args=[self.user.username]))

        # Check that the user is redirected to their own profile
        self.assertRedirects(response, reverse('profile', args=[self.user.username]))

        # Verify that no Follow object was created
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.user).exists())

    def test_follow_user_already_following(self):
        """
        Test that following a user who is already followed doesn't create duplicate entries.
        """
        # Create the follow relationship beforehand
        Follow.objects.create(follower=self.user, following=self.user_to_follow)

        request = self.factory.get(reverse('follow_user', kwargs={'username': 'followme'}))
        request.user = self.user

        response = follow_user(request, username='followme')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'followme'}))

        # Check that only one follow relationship exists
        self.assertEqual(Follow.objects.filter(follower=self.user, following=self.user_to_follow).count(), 1)

    def test_follow_user_already_following_2(self, setup_users_3, setup_request_3):
        """
        Test follow_user when the user is already following the target user
        """
        Follow.objects.create(follower=self.user, following=self.user_to_follow)
        request = self.factory.get(f'/follow/{self.user_to_follow.username}/')
        request.user = self.user
        response = follow_user(request, self.user_to_follow.username)
        assert response.status_code == 302  # Expecting a redirect
        assert Follow.objects.filter(follower=self.user, following=self.user_to_follow).count() == 1

    def test_follow_user_database_error(self, setup_users_3, setup_request_3, monkeypatch):
        """
        Test follow_user when a database error occurs
        """
        def mock_get_or_create(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(Follow.objects, 'get_or_create', mock_get_or_create)
        request = self.factory.get(f'/follow/{self.user_to_follow.username}/')
        request.user = self.user
        with pytest.raises(Exception, match="Database error"):
            follow_user(request, self.user_to_follow.username)

    def test_follow_user_empty_username(self, setup_users_3, setup_request_3):
        """
        Test follow_user with an empty username
        """
        request = self.factory.get('/follow/')
        request.user = self.user
        with pytest.raises(ValueError):
            follow_user(request, '')

    def test_follow_user_invalid_username(self, setup_users_3, setup_request_3):
        """
        Test follow_user with an invalid username
        """
        request = self.factory.get('/follow/nonexistentuser/')
        request.user = self.user
        with pytest.raises(User.DoesNotExist):
            follow_user(request, 'nonexistentuser')

    def test_follow_user_not_logged_in(self, setup_users_3, setup_request_3):
        """
        Test follow_user when the user is not logged in
        """
        request = self.factory.get('/follow/usertofollow/')
        request.user = AnonymousUser()
        response = follow_user(request, 'usertofollow')
        assert response.status_code == 302

    def test_follow_user_self(self):
        """
        Test that a user cannot follow themselves.
        """
        request = self.factory.get(reverse('follow_user', kwargs={'username': 'testuser'}))
        request.user = self.user

        response = follow_user(request, username='testuser')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'testuser'}))

        # Check that no follow relationship was created
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.user).exists())

    def test_follow_user_self_2(self, setup_users_3, setup_request_3):
        """
        Test follow_user when a user tries to follow themselves
        """
        request = self.factory.get(f'/follow/{self.user.username}/')
        request.user = self.user
        response = follow_user(request, self.user.username)
        assert response.status_code == 302  # Expecting a redirect
        assert not Follow.objects.filter(follower=self.user, following=self.user).exists()

    def test_follow_user_success(self):
        """
        Test that a user can successfully follow another user.
        """
        request = self.factory.get(reverse('follow_user', kwargs={'username': 'followme'}))
        request.user = self.user

        response = follow_user(request, username='followme')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'followme'}))

        # Check that the follow relationship was created
        self.assertTrue(Follow.objects.filter(follower=self.user, following=self.user_to_follow).exists())

    def test_help_page_authenticated(self, rf, mocker):
        """
        Test that help_page view returns the correct template for authenticated users.
        """
        # Create a request factory
        request = rf.get(reverse('help'))

        # Create a mock user and set it as the authenticated user
        user = User.objects.create_user(username='testuser', password='12345')
        request.user = user

        # Mock the login_required decorator
        mocker.patch('django.contrib.auth.decorators.login_required', lambda x: x)

        # Mock the render function
        mock_render = mocker.patch('projects.views.render')
        mock_render.return_value = "Mocked render response"

        # Call the view function
        response = help_page(request)

        # Assert that render was called with the correct arguments
        mock_render.assert_called_once_with(request, 'projects/help.html')

        # Assert that the response is what we expect
        assert response == "Mocked render response"

    def test_help_page_authenticated_2(self, factory, user):
        """
        Test that authenticated users can access the help page.
        """
        request = factory.get(reverse('help'))
        request.user = user
        response = help_page(request)
        assert response.status_code == 200
        assert 'projects/help.html' in response.template_name

    def test_help_page_post_request(self, factory, user):
        """
        Test that POST requests to the help page are not allowed.
        """
        request = factory.post(reverse('help'))
        request.user = user
        response = help_page(request)
        assert response.status_code == 405

    @pytest.mark.django_db
    def test_help_page_unauthenticated(self, client):
        """
        Test that help_page view redirects unauthenticated users to login page.
        """
        # Make a GET request to the help page
        response = client.get(reverse('help'))

        # Check that the response is a redirect
        assert response.status_code == 302

        # Check that it redirects to the login page
        assert response.url.startswith(reverse('login'))

    def test_help_page_unauthenticated_2(self, factory):
        """
        Test that unauthenticated users are redirected when accessing the help page.
        """
        request = factory.get(reverse('help'))
        request.user = AnonymousUser()
        response = help_page(request)
        assert response.status_code == 302
        assert response.url.startswith(reverse('login'))

    def test_help_page_with_invalid_session(self, factory):
        """
        Test help page access with an invalid session.
        """
        request = factory.get(reverse('help'))
        request.user = None
        response = help_page(request)
        assert response.status_code == 302
        assert response.url.startswith(reverse('login'))

    def test_help_page_with_query_params(self, factory, user):
        """
        Test that query parameters are ignored in the help page.
        """
        request = factory.get(reverse('help') + '?param=value')
        request.user = user
        response = help_page(request)
        assert response.status_code == 200
        assert 'projects/help.html' in response.template_name

    def test_home_1(self, setup_data):
        """
        Test the home view with specific filters and constraints.
        """
        factory = RequestFactory()
        request = factory.get('/?q=Test&date_posted=7&status=active&concentration=Web Development')
        request.user = self.user

        response = home(request, topic="Web Development")

        assert response.status_code == 200
        assert 'projects' in response.context_data
        assert 'topics' in response.context_data
        assert 'top_users' in response.context_data
        assert 'selected_topic' in response.context_data
        assert 'search_query' in response.context_data

        projects = response.context_data['projects']
        assert len(projects) == 1
        assert projects[0].title == "Test Project"
        assert projects[0].topic == "Web Development"
        assert not projects[0].completed

        assert response.context_data['selected_topic'] == "Web Development"
        assert response.context_data['search_query'] == "Test"

        top_users = response.context_data['top_users']
        assert len(top_users) == 1
        assert top_users[0].user == self.user
        assert top_users[0].points == 100

        assert response.template_name == ['projects/home.html']

    def test_home_5(self, setup_data_3):
        """
        Test home view with topic, search query, date filter, closed status, and concentration filter
        """
        factory = RequestFactory()
        request = factory.get('/home/?q=Test&date_posted=15&status=closed&concentration=Web Development')
        request.user = self.user

        response = home(request, topic='Web Development')

        assert response.status_code == 200
        context = response.context_data

        # Check if the correct template is used
        assert response.template_name == ['projects/home.html']

        # Verify filtered projects
        projects = context['projects']
        assert projects.count() == 1
        assert projects[0].title == 'Test Project 1'
        assert projects[0].topic == 'Web Development'
        assert projects[0].completed == True

        # Verify other context variables
        assert context['topics'] == [choice[0] for choice in Project.TOPIC_CHOICES]
        assert len(context['top_users']) <= 3
        assert context['selected_topic'] == 'Web Development'
        assert context['search_query'] == 'Test'

        # Verify that the projects are filtered correctly
        assert projects.filter(
            Q(title__icontains='Test') | Q(description__icontains='Test'),
            created_at__gte=timezone.now() - timedelta(days=15),
            completed=True,
            topic='Web Development'
        ).exists()

    def test_home_6(self, setup_data_2):
        """
        Test home view with topic, search query, date posted, status, and concentration filters
        """
        request = self.factory.get('/home/?q=Test&date_posted=30&status=pending&concentration=Technology')
        request.user = self.user

        response = home(request, topic='Technology')

        assert response.status_code == 200
        assert 'projects' in response.context_data
        assert 'topics' in response.context_data
        assert 'top_users' in response.context_data
        assert 'selected_topic' in response.context_data
        assert 'search_query' in response.context_data

        # Verify filters are applied correctly
        projects = response.context_data['projects']
        assert len(projects) == 1
        assert projects[0].title == 'Test Project'
        assert projects[0].topic == 'Technology'

        assert response.context_data['selected_topic'] == 'Technology'
        assert response.context_data['search_query'] == 'Test'

        # Verify top users are present
        assert len(response.context_data['top_users']) <= 3

        # Verify the template used
        assert response.template_name == ['projects/home.html']

    @pytest.mark.django_db
    def test_home_7(self):
        """
        Test home view with topic, search query, date posted, and concentration filters.
        """
        # Create a request factory
        factory = RequestFactory()

        # Create test data
        topic = "Science"
        search_query = "test"
        date_posted = "7"
        concentration = "Biology"

        # Create test projects
        Project.objects.create(title="Test Project 1", description="This is a test project", topic="Science", created_at=timezone.now())
        Project.objects.create(title="Old Project", description="This is an old project", topic="Math", created_at=timezone.now() - timedelta(days=10))
        Project.objects.create(title="Biology Project", description="This is a biology project", topic="Biology", created_at=timezone.now())

        # Create top users
        for i in range(3):
            user = User.objects.create(username=f"user{i}")
            UserProfile.objects.create(user=user, points=100-i)

        # Create a GET request with query parameters
        request = factory.get(f'/home/{topic}/?q={search_query}&date_posted={date_posted}&concentration={concentration}')

        # Call the home view
        response = home(request, topic=topic)

        # Assert that the response is rendered with the correct template
        assert response.template_name == ['projects/home.html']

        # Assert that the context contains the expected keys
        assert 'projects' in response.context_data
        assert 'topics' in response.context_data
        assert 'top_users' in response.context_data
        assert 'selected_topic' in response.context_data
        assert 'search_query' in response.context_data

        # Assert that the filters are applied correctly
        projects = response.context_data['projects']
        assert len(projects) == 1  # Only one project should match all criteria
        assert projects[0].title == "Test Project 1"
        assert projects[0].topic == "Science"

        # Assert that the selected topic is correct
        assert response.context_data['selected_topic'] == topic

        # Assert that the search query is correct
        assert response.context_data['search_query'] == search_query

        # Assert that top users are present
        assert len(response.context_data['top_users']) == 3

        # Assert that topics are present
        assert len(response.context_data['topics']) > 0

    @pytest.mark.django_db
    def test_home_database_error(self, factory, user, monkeypatch):
        """
        Test home view when a database error occurs
        """
        def mock_filter(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(Project.objects, 'filter', mock_filter)
        request = factory.get('/')
        request.user = user
        with pytest.raises(Exception, match="Database error"):
            home(request)

    def test_home_empty_search_query(self, factory, user):
        """
        Test home view with an empty search query
        """
        request = factory.get('/?q=')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert len(response.context_data['projects']) == Project.objects.count()

    def test_home_extremely_long_search_query(self, factory, user):
        """
        Test home view with an extremely long search query
        """
        long_query = 'a' * 1000
        request = factory.get(f'/?q={long_query}')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert len(response.context_data['projects']) == 0

    def test_home_filtered_and_active(self):
        """
        Test home view with search query, date filter, active status, and concentration filter
        """
        request = self.factory.get('/home/?q=Test&date_posted=7&status=active&concentration=Technology')
        request.user = self.user

        response = home(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context_data)
        self.assertIn('topics', response.context_data)
        self.assertIn('top_users', response.context_data)
        self.assertIn('selected_topic', response.context_data)
        self.assertIn('search_query', response.context_data)

        projects = response.context_data['projects']
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], self.project)

        self.assertEqual(response.context_data['search_query'], 'Test')
        self.assertIsNone(response.context_data['selected_topic'])

        top_users = response.context_data['top_users']
        self.assertEqual(len(top_users), 1)
        self.assertEqual(top_users[0], self.user.userprofile)

        self.assertTemplateUsed(response, 'projects/home.html')

    @pytest.mark.django_db
    def test_home_filtered_by_topic_query_date_and_active_status(self):
        """
        Test home view with filters for topic, search query, date posted, and active status.
        """
        # Set up test data
        factory = RequestFactory()
        topic = "Test Topic"
        query = "Test Query"
        date_posted = "7"
        status = "active"

        # Create test projects
        Project.objects.create(title="Active Recent Project", description="Test", topic=topic, created_at=timezone.now())
        Project.objects.create(title="Active Old Project", description="Test", topic=topic, created_at=timezone.now() - timedelta(days=10))
        Project.objects.create(title="Completed Project", description="Test", topic=topic, completed=True)
        Project.objects.create(title="Unrelated Project", description="Unrelated", topic="Other Topic")

        # Create top users
        for i in range(3):
            user = User.objects.create(username=f"user{i}")
            UserProfile.objects.create(user=user, points=100-i)

        # Create request
        request = factory.get(f'/?q={query}&date_posted={date_posted}&status={status}')

        # Call the view
        response = home(request, topic=topic)

        # Check if the response is rendered correctly
        assert response.status_code == 200
        assert response.template_name == ['projects/home.html']

        # Check if the context data is correct
        context = response.context_data
        assert 'projects' in context
        assert 'topics' in context
        assert 'top_users' in context
        assert 'selected_topic' in context
        assert 'search_query' in context

        # Verify filtered projects
        projects = context['projects']
        assert projects.count() == 1
        assert projects.first().title == "Active Recent Project"

        # Verify other context data
        assert context['selected_topic'] == topic
        assert context['search_query'] == query
        assert len(context['top_users']) == 3
        assert [choice[0] for choice in Project.TOPIC_CHOICES] == context['topics']

    def test_home_invalid_date_posted(self, factory, user):
        """
        Test home view with an invalid date_posted parameter
        """
        request = factory.get('/?date_posted=invalid')
        request.user = user
        with pytest.raises(ValueError):
            home(request)

    def test_home_invalid_status(self, factory, user):
        """
        Test home view with an invalid status parameter
        """
        request = factory.get('/?status=invalid')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert len(response.context_data['projects']) == Project.objects.count()

    def test_home_invalid_topic(self, factory, user):
        """
        Test home view with an invalid topic
        """
        request = factory.get('/')
        request.user = user
        response = home(request, topic='invalid_topic')
        assert response.status_code == 200
        assert len(response.context_data['projects']) == 0

    def test_home_negative_date_posted(self, factory, user):
        """
        Test home view with a negative date_posted parameter
        """
        request = factory.get('/?date_posted=-1')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert len(response.context_data['projects']) == 0

    def test_home_non_existent_concentration(self, factory, user):
        """
        Test home view with a non-existent concentration
        """
        request = factory.get('/?concentration=non_existent')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert len(response.context_data['projects']) == 0

    def test_home_sql_injection_attempt(self, factory, user):
        """
        Test home view with a potential SQL injection attempt
        """
        sql_injection = "'; DROP TABLE projects; --"
        request = factory.get(f'/?q={sql_injection}')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert Project.objects.exists()

    def test_home_with_filters(self):
        """
        Test home view with topic, date_posted, status, and concentration filters.
        """
        # Create a request with query parameters
        request = self.factory.get('/home/?date_posted=7&status=active&concentration=Science')
        request.user = self.user

        # Call the home view with a topic
        response = home(request, topic='Science')

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'projects/home.html')

        # Check if the context contains the expected keys
        self.assertIn('projects', response.context)
        self.assertIn('topics', response.context)
        self.assertIn('top_users', response.context)
        self.assertIn('selected_topic', response.context)
        self.assertIn('search_query', response.context)

        # Check if the filters are applied correctly
        projects = response.context['projects']
        self.assertTrue(all(p.topic == 'Science' for p in projects))
        self.assertTrue(all(p.created_at >= timezone.now() - timedelta(days=7) for p in projects))
        self.assertTrue(all(p.completed == False for p in projects))

        # Check if the selected topic is correct
        self.assertEqual(response.context['selected_topic'], 'Science')

        # Check if the search query is empty
        self.assertEqual(response.context['search_query'], '')

        # Check if top users are present
        self.assertTrue(len(response.context['top_users']) > 0)

    def test_home_with_filters_2(self):
        """
        Test home view with topic, search query, status, and concentration filters
        """
        url = reverse('home')
        request = self.factory.get(url, {'q': 'Test', 'status': 'active', 'concentration': 'Technology'})
        request.user = self.user

        response = home(request, topic='Technology')

        self.assertEqual(response.status_code, 200)
        self.assertIn('projects', response.context_data)
        self.assertIn('topics', response.context_data)
        self.assertIn('top_users', response.context_data)
        self.assertIn('selected_topic', response.context_data)
        self.assertIn('search_query', response.context_data)

        projects = response.context_data['projects']
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], self.project1)

        self.assertEqual(response.context_data['selected_topic'], 'Technology')
        self.assertEqual(response.context_data['search_query'], 'Test')

        topics = response.context_data['topics']
        self.assertIn('Technology', topics)
        self.assertIn('Science', topics)

        top_users = response.context_data['top_users']
        self.assertEqual(len(top_users), 1)
        self.assertEqual(top_users[0].user, self.user)

        self.assertTemplateUsed(response, 'projects/home.html')

    def test_home_xss_attempt(self, factory, user):
        """
        Test home view with a potential XSS attempt
        """
        xss_attempt = "<script>alert('XSS')</script>"
        request = factory.get(f'/?q={xss_attempt}')
        request.user = user
        response = home(request)
        assert response.status_code == 200
        assert xss_attempt not in response.content.decode()

    def test_landing_page_1(self):
        """
        Test that landing_page view returns correct context and renders the correct template
        """
        request = self.factory.get(reverse('landing_page'))
        response = landing_page(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/landing.html')

        context = response.context_data
        self.assertEqual(context['title'], 'Welcome to My Website')
        self.assertIsInstance(context['features'], list)
        self.assertEqual(len(context['features']), 3)

        expected_features = [
            {'title': 'Collaborate easily', 'description': 'Work seamlessly with your team.'},
            {'title': 'Secure code', 'description': 'Your projects are safe with us.'},
            {'title': 'Build together', 'description': 'Join forces to create something amazing.'},
        ]
        self.assertEqual(context['features'], expected_features)

    def test_landing_page_with_invalid_request(self, rf):
        """
        Test landing_page with an invalid request object
        """
        request = rf.get('/landing')
        request.META = None  # Invalidate the request object
        
        with pytest.raises(AttributeError):
            landing_page(request)

    def test_landing_page_with_large_query_string(self, rf):
        """
        Test landing_page with an extremely large query string
        """
        large_query = 'a' * 10000
        request = rf.get(f'/landing?param={large_query}')
        response = landing_page(request)
        
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_landing_page_with_malformed_request(self, rf):
        """
        Test landing_page with a malformed request
        """
        request = rf.get('/landing')
        del request.GET  # Remove GET attribute to simulate malformed request
        
        response = landing_page(request)
        
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_landing_page_with_unexpected_method(self, rf):
        """
        Test landing_page with an unexpected HTTP method
        """
        request = rf.post('/landing')  # Use POST instead of GET
        response = landing_page(request)
        
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_landing_page_with_unicode_characters(self, rf):
        """
        Test landing_page with Unicode characters in the request
        """
        request = rf.get('/landing', {'param': '📚'})
        response = landing_page(request)
        
        assert isinstance(response, HttpResponse)
        assert response.status_code == 200

    def test_mark_as_read_1(self):
        """
        Test that mark_as_read marks the notification as read and redirects to notifications page
        """
        request = self.factory.get(reverse('mark_as_read', args=[self.notification.id]))
        request.user = self.user

        response = mark_as_read(request, self.notification.id)

        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('notifications'))

        # Refresh the notification from the database
        self.notification.refresh_from_db()

        # Check if the notification is marked as read
        self.assertTrue(self.notification.is_read)

    def test_mark_as_read_already_read_notification(self, setup_7):
        """
        Test marking an already read notification.
        """
        notification = Notification.objects.create(user=self.user, message='Test', is_read=True)

        request = self.factory.get(f'/mark_as_read/{notification.id}')
        request.user = self.user

        response = mark_as_read(request, notification.id)
        assert response.status_code == 302  # Redirects even if already read
        assert Notification.objects.get(id=notification.id).is_read == True

    def test_mark_as_read_invalid_notification_id(self, setup_7):
        """
        Test marking a notification with an invalid ID.
        """
        request = self.factory.get('/mark_as_read/invalid')
        request.user = self.user

        with pytest.raises(Http404):
            mark_as_read(request, 'invalid')

    def test_mark_as_read_nonexistent_notification(self, setup_7):
        """
        Test marking a non-existent notification as read.
        """
        request = self.factory.get('/mark_as_read/999')
        request.user = self.user

        with pytest.raises(Http404):
            mark_as_read(request, 999)

    def test_mark_as_read_notification_of_another_user(self, setup_7):
        """
        Test marking a notification that belongs to another user.
        """
        other_user = User.objects.create_user(username='otheruser', password='54321')
        notification = Notification.objects.create(user=other_user, message='Test')

        request = self.factory.get(f'/mark_as_read/{notification.id}')
        request.user = self.user

        with pytest.raises(Http404):
            mark_as_read(request, notification.id)

    def test_mark_as_read_unauthenticated_user(self, setup_7):
        """
        Test marking a notification as read by an unauthenticated user.
        """
        notification = Notification.objects.create(user=self.user, message='Test')

        request = self.factory.get(f'/mark_as_read/{notification.id}')
        request.user = None

        with pytest.raises(AttributeError):  # Raises AttributeError due to @login_required decorator
            mark_as_read(request, notification.id)

    def test_message_thread_1(self):
        """
        Test that a valid POST request creates a new message and redirects.
        """
        url = reverse('message_thread', kwargs={'username': self.recipient.username})
        data = {
            'content': 'Test message content'
        }
        request = self.factory.post(url, data)
        request.user = self.sender

        # Add session and message middleware to the request
        SessionMiddleware(lambda x: None).process_request(request)
        MessageMiddleware(lambda x: None).process_request(request)
        request.session.save()

        response = message_thread(request, self.recipient.username)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)

        # Check if the message was created
        self.assertTrue(Message.objects.filter(
            sender=self.sender,
            recipient=self.recipient,
            content='Test message content'
        ).exists())

    def test_message_thread_database_error(self, setup_8, monkeypatch):
        """
        Test message_thread when a database error occurs
        """
        def mock_save(*args, **kwargs):
            raise ValidationError("Database error")

        monkeypatch.setattr(Message, 'save', mock_save)

        request = self.factory.post(reverse('message_thread', kwargs={'username': 'recipient'}), data={'content': 'Test message'})
        request.user = self.user
        response = message_thread(request, 'recipient')
        assert response.status_code == 200
        assert Message.objects.count() == 0

    def test_message_thread_empty_message(self, setup_8):
        """
        Test message_thread with an empty message
        """
        request = self.factory.post(reverse('message_thread', kwargs={'username': 'recipient'}), data={'content': ''})
        request.user = self.user
        response = message_thread(request, 'recipient')
        assert response.status_code == 200
        assert Message.objects.count() == 0

    def test_message_thread_invalid_form_data(self, setup_8):
        """
        Test message_thread with invalid form data
        """
        request = self.factory.post(reverse('message_thread', kwargs={'username': 'recipient'}), data={'invalid_field': 'test'})
        request.user = self.user
        response = message_thread(request, 'recipient')
        assert response.status_code == 200
        assert Message.objects.count() == 0

    def test_message_thread_invalid_username(self, setup_8):
        """
        Test message_thread with an invalid username
        """
        request = self.factory.get(reverse('message_thread', kwargs={'username': 'nonexistent_user'}))
        request.user = self.user
        with pytest.raises(Http404):
            message_thread(request, 'nonexistent_user')

    def test_message_thread_message_too_long(self, setup_8):
        """
        Test message_thread with a message that exceeds the maximum length
        """
        long_message = 'a' * 1001  # Assuming max length is 1000
        request = self.factory.post(reverse('message_thread', kwargs={'username': 'recipient'}), data={'content': long_message})
        request.user = self.user
        response = message_thread(request, 'recipient')
        assert response.status_code == 200
        assert Message.objects.count() == 0

    def test_message_thread_partial(self):
        """
        Test that message_thread_partial returns the correct render with messages and recipient
        """
        # Create some test messages
        Message.objects.create(sender=self.user, recipient=self.recipient, content="Hello")
        Message.objects.create(sender=self.recipient, recipient=self.user, content="Hi there")

        # Create a GET request
        request = self.factory.get(reverse('message_thread_partial', kwargs={'recipient_username': self.recipient.username}))
        request.user = self.user

        # Call the view
        response = message_thread_partial(request, self.recipient.username)

        # Check that the response uses the correct template
        self.assertTemplateUsed(response, 'projects/message_thread_partial.html')

        # Check that the context contains the correct data
        self.assertEqual(response.context_data['recipient'], self.recipient)
        
        # Check that the messages in the context are correct
        messages = response.context_data['messages']
        self.assertEqual(messages.count(), 2)
        self.assertTrue(all(isinstance(msg, Message) for msg in messages))

        # Check that the messages are ordered by timestamp
        self.assertTrue(all(messages[i].timestamp <= messages[i+1].timestamp for i in range(len(messages)-1)))

        # Check that only messages between the user and recipient are included
        self.assertTrue(all(
            (msg.sender == self.user and msg.recipient == self.recipient) or
            (msg.sender == self.recipient and msg.recipient == self.user)
            for msg in messages
        ))

    def test_message_thread_partial_empty_recipient(self, request_factory, setup_users_2):
        """
        Test message_thread_partial with an empty recipient username.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        with pytest.raises(Http404):
            message_thread_partial(request, '')

    @pytest.mark.django_db
    def test_message_thread_partial_exception_handling(self, request_factory, setup_users_2, mocker):
        """
        Test message_thread_partial exception handling when database query fails.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        # Mock the Message.objects.filter to raise an exception
        mocker.patch('projects.models.Message.objects.filter', side_effect=Exception('Database error'))

        with pytest.raises(Exception, match='Database error'):
            message_thread_partial(request, self.recipient.username)

    def test_message_thread_partial_integer_recipient(self, request_factory, setup_users_2):
        """
        Test message_thread_partial with an integer as recipient username.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        with pytest.raises(Http404):
            message_thread_partial(request, 12345)

    def test_message_thread_partial_invalid_recipient(self, request_factory, setup_users_2):
        """
        Test message_thread_partial with an invalid recipient username.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        with pytest.raises(Http404):
            message_thread_partial(request, 'nonexistent_user')

    def test_message_thread_partial_long_username(self, request_factory, setup_users_2):
        """
        Test message_thread_partial with an extremely long username.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        long_username = 'a' * 1000  # Create a username with 1000 characters
        with pytest.raises(Http404):
            message_thread_partial(request, long_username)

    def test_message_thread_partial_no_messages(self, request_factory, setup_users_2):
        """
        Test message_thread_partial when there are no messages between users.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        response = message_thread_partial(request, self.recipient.username)
        assert response.status_code == 200
        assert len(response.context_data['messages']) == 0

    def test_message_thread_partial_none_recipient(self, request_factory, setup_users_2):
        """
        Test message_thread_partial with None as recipient username.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        with pytest.raises(Http404):
            message_thread_partial(request, None)

    def test_message_thread_partial_self_recipient(self, request_factory, setup_users_2):
        """
        Test message_thread_partial when the recipient is the same as the sender.
        """
        request = request_factory.get('/message_thread/')
        request.user = self.user

        response = message_thread_partial(request, self.user.username)
        assert response.status_code == 200
        assert len(response.context_data['messages']) == 0

    def test_message_thread_self_messaging(self, setup_8):
        """
        Test message_thread when a user tries to message themselves
        """
        request = self.factory.get(reverse('message_thread', kwargs={'username': 'testuser'}))
        request.user = self.user
        response = message_thread(request, 'testuser')
        assert response.status_code == 200
        assert 'You cannot send messages to yourself' in str(response.content)

    def test_network_displays_all_users(self):
        """
        Test that the network view displays all users.
        """
        request = self.factory.get(reverse('network'))
        response = network(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/network.html')
        
        users_in_context = response.context_data['users']
        self.assertQuerysetEqual(
            users_in_context,
            User.objects.all(),
            ordered=False
        )
        self.assertIn(self.user1, users_in_context)
        self.assertIn(self.user2, users_in_context)

    def test_network_search_functionality(self):
        """
        Test the network view with search functionality.
        """
        request = self.factory.get('/network/', {'q': 'user'})
        response = network(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/network.html')

        users_in_context = response.context_data['users']
        self.assertEqual(users_in_context.count(), 2)
        self.assertIn(self.user1, users_in_context)
        self.assertIn(self.user2, users_in_context)

        # Test search by username
        request = self.factory.get('/network/', {'q': 'user1'})
        response = network(request)
        users_in_context = response.context_data['users']
        self.assertEqual(users_in_context.count(), 1)
        self.assertIn(self.user1, users_in_context)

        # Test search by grade level
        request = self.factory.get('/network/', {'q': 'Junior'})
        response = network(request)
        users_in_context = response.context_data['users']
        self.assertEqual(users_in_context.count(), 1)
        self.assertIn(self.user2, users_in_context)

        # Test search by concentration
        request = self.factory.get('/network/', {'q': 'Data Science'})
        response = network(request)
        users_in_context = response.context_data['users']
        self.assertEqual(users_in_context.count(), 1)
        self.assertIn(self.user2, users_in_context)

        # Test ordering by points
        request = self.factory.get('/network/', {'q': ''})
        response = network(request)
        users_in_context = list(response.context_data['users'])
        self.assertEqual(users_in_context, [self.user2, self.user1])

    def test_network_with_empty_query(self, setup_users):
        """
        Test network view with an empty search query.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == User.objects.count()

    def test_network_with_empty_user_list(self, request_factory):
        """
        Test network view when there are no users in the database.
        """
        request = request_factory.get('/network/')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_incorrect_type(self, setup_users):
        """
        Test network view with an incorrect type for the query parameter.
        """
        factory = RequestFactory()
        request = factory.get('/network/')
        request.GET = {'q': 123}  # Set query to an integer instead of a string
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_invalid_query(self, setup_users):
        """
        Test network view with an invalid search query.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=@#$%^')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_invalid_query_parameter(self, request_factory):
        """
        Test network view with an invalid query parameter.
        """
        request = request_factory.get('/network/?invalid_param=test')
        response = network(request)
        assert response.status_code == 200
        # Ensure the view doesn't crash with invalid parameters

    def test_network_with_large_number_of_users(self, request_factory):
        """
        Test network view with a large number of users to check performance.
        """
        # Create a large number of users
        for i in range(1000):
            User.objects.create_user(username=f'testuser{i}', password='testpass')

        request = request_factory.get('/network/')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 1000

    def test_network_with_long_query(self, setup_users):
        """
        Test network view with an extremely long search query.
        """
        factory = RequestFactory()
        long_query = 'a' * 1000  # A string of 1000 'a' characters
        request = factory.get(f'/network/?q={long_query}')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_malformed_request(self, request_factory):
        """
        Test network view with a malformed request.
        """
        request = request_factory.get('/network/')
        request.META = None  # Simulate a malformed request
        with pytest.raises(AttributeError):
            network(request)

    def test_network_with_malformed_request_2(self, setup_users):
        """
        Test network view with a malformed request object.
        """
        request = HttpRequest()
        request.method = 'GET'
        # Intentionally not setting request.GET
        with pytest.raises(AttributeError):
            network(request)

    def test_network_with_multiple_spaces(self, setup_users):
        """
        Test network view with multiple spaces in the search query.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=  multiple   spaces  ')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_non_existent_user(self, request_factory):
        """
        Test network view when trying to access a non-existent user.
        """
        request = request_factory.get('/network/non_existent_user/')
        with pytest.raises(Http404):
            network(request, username='non_existent_user')

    def test_network_with_non_existent_user_2(self, setup_users):
        """
        Test network view with a search query for a non-existent user.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=nonexistentuser')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_sql_injection_attempt(self, setup_users):
        """
        Test network view with a potential SQL injection attempt.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=1%27%20OR%20%271%27=%271')  # URL encoded "1' OR '1'='1"
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_with_unicode_characters(self, setup_users):
        """
        Test network view with Unicode characters in the search query.
        """
        factory = RequestFactory()
        request = factory.get('/network/?q=🚀🌟')
        response = network(request)
        assert response.status_code == 200
        assert len(response.context_data['users']) == 0

    def test_network_without_query(self):
        """
        Test network view without search query.
        Ensures all users are returned, ordered by points.
        """
        request = self.factory.get('/network/')
        response = network(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/network.html')
        
        users_in_context = response.context_data['users']
        self.assertEqual(list(users_in_context), [self.user2, self.user1])

    def test_notifications_view_authenticated_user(self):
        """
        Test that notifications_view returns the correct template and context for an authenticated user
        """
        # Create some test notifications for the user
        Notification.objects.create(user=self.user, message="Test notification 1")
        Notification.objects.create(user=self.user, message="Test notification 2")

        # Create a GET request
        request = self.factory.get(reverse('notifications'))
        request.user = self.user

        # Call the view
        response = notifications_view(request)

        # Check that the response uses the correct template
        self.assertEqual(response.template_name, ['projects/notifications.html'])

        # Check that the context contains the notifications
        notifications = response.context_data['notifications']
        self.assertEqual(notifications.count(), 2)
        self.assertQuerysetEqual(
            notifications,
            Notification.objects.filter(user=self.user).order_by('-timestamp'),
            transform=lambda x: x
        )

    def test_notifications_view_exception_handling(self, setup_user, setup_request_factory, monkeypatch):
        """
        Test that the view handles exceptions gracefully.
        """
        def mock_filter(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(Notification.objects, 'filter', mock_filter)
        request = setup_request_factory.get(reverse('notifications'))
        request.user = setup_user
        with pytest.raises(Exception):
            notifications_view(request)

    def test_notifications_view_no_notifications(self, setup_user, setup_request_factory):
        """
        Test that the view works correctly when the user has no notifications.
        """
        request = setup_request_factory.get(reverse('notifications'))
        request.user = setup_user
        response = notifications_view(request)
        assert response.status_code == 200
        assert list(response.context_data['notifications']) == []

    def test_notifications_view_ordering(self, setup_user, setup_request_factory):
        """
        Test that notifications are ordered by timestamp in descending order.
        """
        Notification.objects.create(user=setup_user, message="Old notification")
        Notification.objects.create(user=setup_user, message="New notification")
        request = setup_request_factory.get(reverse('notifications'))
        request.user = setup_user
        response = notifications_view(request)
        assert response.status_code == 200
        notifications = list(response.context_data['notifications'])
        assert len(notifications) == 2
        assert notifications[0].message == "New notification"
        assert notifications[1].message == "Old notification"

    def test_notifications_view_other_users_notifications(self, setup_user, setup_request_factory):
        """
        Test that the view doesn't display notifications belonging to other users.
        """
        other_user = User.objects.create_user(username='otheruser', password='12345')
        Notification.objects.create(user=other_user, message="Other user's notification")
        request = setup_request_factory.get(reverse('notifications'))
        request.user = setup_user
        response = notifications_view(request)
        assert response.status_code == 200
        assert list(response.context_data['notifications']) == []

    def test_notifications_view_unauthenticated_user(self):
        """
        Test that notifications_view redirects unauthenticated users to the login page
        """
        # Create a GET request
        request = self.factory.get(reverse('notifications'))
        request.user = AnonymousUser()

        # Call the view
        response = notifications_view(request)

        # Check that the response is a redirect to the login page
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_notifications_view_unauthenticated_user_2(self, setup_request_factory):
        """
        Test that an unauthenticated user is redirected to the login page.
        """
        request = setup_request_factory.get(reverse('notifications'))
        request.user = None
        response = notifications_view(request)
        assert isinstance(response, HttpResponseRedirect)
        assert response.url.startswith(reverse('login'))

    def test_notifications_view_with_notifications(self, setup_user, setup_request_factory):
        """
        Test that the view correctly displays notifications when they exist.
        """
        Notification.objects.create(user=setup_user, message="Test notification")
        request = setup_request_factory.get(reverse('notifications'))
        request.user = setup_user
        response = notifications_view(request)
        assert response.status_code == 200
        assert len(response.context_data['notifications']) == 1
        assert response.context_data['notifications'][0].message == "Test notification"

    @pytest.mark.django_db
    def test_profile_database_error(self, setup_profile, monkeypatch):
        """Test profile view when a database error occurs."""
        def mock_get_or_create(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(UserProfile.objects, 'get_or_create', mock_get_or_create)
        request = self.factory.get('/profile/testuser/')
        with pytest.raises(Exception, match="Database error"):
            profile(request, username='testuser')

    def test_profile_empty_skills(self):
        """
        Test that the profile view handles empty skills correctly
        """
        self.user_profile.skills = ''
        self.user_profile.save()

        request = self.factory.get('/profile/testuser/')
        response = profile(request, username='testuser')

        self.assertEqual(response.status_code, 200)
        context = response.context_data
        self.assertEqual(context['skills_list'], [])

    def test_profile_empty_username(self, setup_profile):
        """Test profile view with an empty username."""
        request = self.factory.get('/profile/')
        with pytest.raises(Http404):
            profile(request, username='')

    def test_profile_invalid_username(self, setup_profile):
        """Test profile view with an invalid username format."""
        request = self.factory.get('/profile/invalid@user/')
        with pytest.raises(Http404):
            profile(request, username='invalid@user')

    def test_profile_nonexistent_user(self):
        """
        Test that the profile view returns a 404 for a non-existent user
        """
        request = self.factory.get('/profile/nonexistentuser/')
        response = profile(request, username='nonexistentuser')

        self.assertEqual(response.status_code, 404)

    def test_profile_nonexistent_user_2(self, setup_profile):
        """Test profile view with a non-existent username."""
        request = self.factory.get('/profile/nonexistentuser/')
        with pytest.raises(Http404):
            profile(request, username='nonexistentuser')

    def test_profile_user_without_profile(self, setup_profile):
        """Test profile view for a user without a UserProfile."""
        new_user = User.objects.create_user(username='newuser', password='12345')
        request = self.factory.get('/profile/newuser/')
        response = profile(request, username='newuser')
        assert response.status_code == 200
        assert 'profile_user' in response.context_data
        assert response.context_data['profile_user'] == new_user
        assert 'skills_list' in response.context_data
        assert response.context_data['skills_list'] == []

    def test_profile_view(self):
        """
        Test that the profile view returns the correct context and uses the correct template
        """
        request = self.factory.get('/profile/testuser/')
        response = profile(request, username='testuser')

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, render)
        self.assertEqual(response.template_name, ['projects/profile.html'])

        context = response.context_data
        self.assertIn('profile_user', context)
        self.assertEqual(context['profile_user'], self.user)
        self.assertIn('skills_list', context)
        self.assertEqual(context['skills_list'], ['Python', 'Django', 'JavaScript'])

    def test_profile_with_empty_skills(self, setup_profile):
        """Test profile view with empty skills."""
        self.profile.skills = ''
        self.profile.save()
        request = self.factory.get('/profile/testuser/')
        response = profile(request, username='testuser')
        assert response.status_code == 200
        assert 'skills_list' in response.context_data
        assert response.context_data['skills_list'] == []

    def test_profile_with_malformed_skills(self, setup_profile):
        """Test profile view with malformed skills string."""
        self.profile.skills = ',,skill1,,skill2,,'
        self.profile.save()
        request = self.factory.get('/profile/testuser/')
        response = profile(request, username='testuser')
        assert response.status_code == 200
        assert 'skills_list' in response.context_data
        assert '' not in response.context_data['skills_list']
        assert len(response.context_data['skills_list']) == 2

    @pytest.mark.django_db
    def test_project_2(self):
        """
        Test adding a comment to a project.
        """
        # Create a user and log them in
        user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a project
        test_project = Project.objects.create(
            title='Test Project',
            description='This is a test project',
            owner=user
        )
        
        # Create a POST request
        factory = RequestFactory()
        request = factory.post(reverse('project', kwargs={'project_id': test_project.id}), {
            'comment': 'This is a test comment'
        })
        
        # Simulate a logged-in user
        request.user = user
        
        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Call the view function
        response = project(request, project_id=test_project.id)
        
        # Check if the response is a redirect
        assert response.status_code == 302
        assert response.url == reverse('project', kwargs={'project_id': test_project.id})
        
        # Check if the comment was added to the database
        assert Comment.objects.filter(project=test_project, user=user, content='This is a test comment').exists()

    @pytest.mark.django_db
    def test_project_3(self):
        """
        Test joining a completed project.
        
        Ensures that when a user attempts to join a completed project,
        an error message is added and the user is redirected to the project page.
        """
        # Create a test user
        user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a completed project
        completed_project = Project.objects.create(
            title="Completed Project",
            description="This is a completed project",
            owner=user,
            completed=True
        )
        
        # Set up the request
        factory = RequestFactory()
        request = factory.post(reverse('project', args=[completed_project.id]), data={'join_project': 'true'})
        request.user = user
        
        # Add message middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Call the view
        response = project(request, completed_project.id)
        
        # Check that the response is a redirect
        assert response.status_code == 302
        assert response.url == reverse('project', args=[completed_project.id])
        
        # Check that an error message was added
        messages = list(messages)
        assert len(messages) == 1
        assert str(messages[0]) == "This project is completed and no longer accepting join requests."

    def test_project_4(self):
        """
        Test joining a project when conditions are met:
        - POST request
        - 'join_project' in POST data
        - Project is not completed
        - User is not a member of the project
        """
        request = self.factory.post(reverse('project', args=[self.project.id]), {'join_project': 'true'})
        request.user = User.objects.create_user(username='newuser', password='12345')
        
        # Set up messages
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = project(request, self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('project', args=[self.project.id]))
        
        # Check if a JoinRequest was created
        self.assertTrue(JoinRequest.objects.filter(user=request.user, project=self.project, status='pending').exists())

    @pytest.mark.django_db
    def test_project_6(self):
        """
        Test rejecting a join request for a project.
        """
        # Create a test user and project
        user = User.objects.create_user(username='testuser', password='12345')
        project_obj = Project.objects.create(title='Test Project', owner=user)
        
        # Create a join request
        requester = User.objects.create_user(username='requester', password='12345')
        join_request = JoinRequest.objects.create(user=requester, project=project_obj, status='pending')

        # Set up the request
        factory = RequestFactory()
        request = factory.post(f'/project/{project_obj.id}/', {'reject_request': join_request.id})
        request.user = user

        # Add session and messages middleware
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Call the view function
        response = project(request, project_obj.id)

        # Check if the response is a redirect
        assert isinstance(response, type(redirect('project', project_id=project_obj.id)))

        # Check if the join request status was updated to 'rejected'
        updated_join_request = JoinRequest.objects.get(id=join_request.id)
        assert updated_join_request.status == 'rejected'

        # Check if the redirect is to the correct URL
        assert response.url == f'/project/{project_obj.id}/'

    def test_project_7(self):
        """
        Test case for project view when POST request is made with invalid rating form.
        """
        url = reverse('project', args=[self.project.id])
        request = self.factory.post(url, data={'rating': 'invalid'})
        request.user = self.user

        # Add message middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = project(request, self.project.id)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project.html')

        # Check that the form in the context is invalid
        self.assertFalse(response.context_data['form'].is_valid())

        # Verify that the project rating hasn't changed
        self.project.refresh_from_db()
        self.assertEqual(self.project.rating, 0)  # Assuming initial rating is 0

        # Check that the context contains the expected keys
        self.assertIn('project', response.context_data)
        self.assertIn('comments', response.context_data)
        self.assertIn('form', response.context_data)
        self.assertIn('is_owner', response.context_data)
        self.assertIn('is_pending_request', response.context_data)
        self.assertIn('join_requests', response.context_data)
        self.assertIn('updates', response.context_data)

    @pytest.mark.django_db
    def test_project_8(self, setup_request):
        """
        Test the project view when POST request is made without any specific action.
        """
        # Arrange
        request = setup_request
        project_instance = Project.objects.create(
            title="Test Project",
            description="Test Description",
            owner=request.user
        )
        project_id = project_instance.id

        # Act
        response = project(request, project_id)

        # Assert
        assert response.status_code == 200
        assert isinstance(response, render)
        assert response.template_name == ['projects/project.html']

        context = response.context_data
        assert 'project' in context
        assert context['project'] == project_instance
        assert 'comments' in context
        assert 'form' in context
        assert isinstance(context['form'], RatingForm)
        assert 'is_owner' in context
        assert 'is_pending_request' in context
        assert 'join_requests' in context
        assert 'updates' in context

        # Check that updates are correctly populated
        updates = context['updates']
        assert len(updates) >= 1  # At least the project creation update
        assert updates[0]['content'] == "Project created"
        assert updates[0]['created_at'] == project_instance.created_at

    @pytest.mark.django_db
    def test_project_approve_join_request(self):
        """
        Test approving a join request for a project.
        """
        # Create a user and log them in
        user = User.objects.create_user(username='testuser', password='12345')
        
        # Create a project
        project_obj = Project.objects.create(title='Test Project', owner=user)
        
        # Create a join request
        requester = User.objects.create_user(username='requester', password='12345')
        join_request = JoinRequest.objects.create(user=requester, project=project_obj, status='pending')
        
        # Create a POST request
        factory = RequestFactory()
        request = factory.post(reverse('project', args=[project_obj.id]), data={
            'approve_request': join_request.id
        })
        
        # Set up the user on the request
        request.user = user
        
        # Set up messages
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Call the view
        response = project(request, project_obj.id)
        
        # Check that the response is a redirect
        assert response.status_code == 302
        assert response.url == reverse('project', args=[project_obj.id])
        
        # Check that the join request was approved
        join_request.refresh_from_db()
        assert join_request.status == 'approved'
        
        # Check that the user was added to the project members
        assert requester in project_obj.members.all()

    def test_project_approve_nonexistent_request(self, setup_5):
        """
        Test that the view handles approving a non-existent join request.
        """
        request = self.factory.post(reverse('project', kwargs={'project_id': self.project.id}), {'approve_request': '9999'})
        request.user = self.user
        with pytest.raises(Http404):
            project(request, self.project.id)

    def test_project_detail_404(self):
        """
        Test that project_detail view returns 404 for non-existent project
        """
        non_existent_pk = self.project.pk + 1
        request = self.factory.get(f'/project/{non_existent_pk}/')
        request.user = self.user

        with self.assertRaises(Exception) as context:
            project_detail(request, pk=non_existent_pk)

        self.assertTrue('Not Found' in str(context.exception))

    def test_project_detail_exists(self):
        """
        Test that project_detail view returns the correct template with existing project
        """
        request = self.factory.get(f'/project/{self.project.pk}/')
        request.user = self.user

        response = project_detail(request, pk=self.project.pk)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertEqual(response.context_data['project'], self.project)

    def test_project_detail_float_pk(self, factory):
        """
        Test project_detail with a float pk.
        """
        request = factory.get('/project/1.5/')
        with pytest.raises(Http404):
            project_detail(request, pk=1.5)

    def test_project_detail_incorrect_pk_type(self, factory):
        """
        Test project_detail with an incorrect pk type.
        """
        request = factory.get('/project/abc/')  # 'abc' is not a valid integer pk
        with pytest.raises(Http404):
            project_detail(request, pk='abc')

    def test_project_detail_invalid_pk(self, factory):
        """
        Test project_detail with an invalid primary key (pk).
        """
        request = factory.get('/project/999/')  # Assuming 999 is an invalid pk
        with pytest.raises(Http404):
            project_detail(request, pk=999)

    def test_project_detail_negative_pk(self, factory):
        """
        Test project_detail with a negative pk.
        """
        request = factory.get('/project/-1/')
        with pytest.raises(Http404):
            project_detail(request, pk=-1)

    def test_project_detail_non_existent_project(self, factory):
        """
        Test project_detail with a non-existent project.
        """
        request = factory.get('/project/9999/')  # Assuming 9999 is a non-existent project
        with pytest.raises(Http404):
            project_detail(request, pk=9999)

    def test_project_detail_sql_injection_attempt(self, factory):
        """
        Test project_detail with a potential SQL injection attempt.
        """
        request = factory.get("/project/1 OR '1'='1/")
        with pytest.raises(Http404):
            project_detail(request, pk="1 OR '1'='1")

    def test_project_detail_very_large_pk(self, factory):
        """
        Test project_detail with a very large pk.
        """
        request = factory.get(f'/project/{2**63}/')  # A very large number
        with pytest.raises(Http404):
            project_detail(request, pk=2**63)

    def test_project_detail_zero_pk(self, factory):
        """
        Test project_detail with a zero pk.
        """
        request = factory.get('/project/0/')
        with pytest.raises(Http404):
            project_detail(request, pk=0)

    def test_project_empty_comment(self, setup_5):
        """
        Test that the view handles empty comment submission.
        """
        request = self.factory.post(reverse('project', kwargs={'project_id': self.project.id}), {'comment': ''})
        request.user = self.user
        response = project(request, self.project.id)
        assert response.status_code == 200  # Renders the page without creating a comment
        assert Comment.objects.count() == 0

    def test_project_invalid_rating(self, setup_5):
        """
        Test that the view handles invalid rating input.
        """
        request = self.factory.post(reverse('project', kwargs={'project_id': self.project.id}), {'rating': 'invalid'})
        request.user = self.user
        response = project(request, self.project.id)
        assert response.status_code == 302

    def test_project_join_completed_project(self, setup_5):
        """
        Test that the view handles join request for a completed project.
        """
        self.project.completed = True
        self.project.save()
        request = self.factory.post(reverse('project', kwargs={'project_id': self.project.id}), {'join_project': 'true'})
        request.user = self.user
        request._messages = messages.storage.default_storage(request)
        response = project(request, self.project.id)
        assert response.status_code == 302  # Redirects back to the project page
        assert 'This project is completed and no longer accepting join requests.' in [m.message for m in messages.get_messages(request)]

    def test_project_not_found(self, setup_5):
        """
        Test that the view raises Http404 when the project does not exist.
        """
        request = self.factory.get(reverse('project', kwargs={'project_id': 9999}))
        request.user = self.user
        with pytest.raises(Http404):
            project(request, 9999)

    def test_project_rating_submission(self):
        """
        Test that a valid rating submission updates the project rating and redirects.
        """
        # Create a user
        user = User.objects.create_user(username='testuser', password='12345')

        # Create a project
        project_obj = Project.objects.create(
            title='Test Project',
            description='Test Description',
            owner=user,
            rating=3.0
        )

        # Create a request
        factory = RequestFactory()
        request = factory.post(reverse('project', kwargs={'project_id': project_obj.id}), data={
            'rating': '4',
        })
        request.user = user

        # Create a valid form
        form = RatingForm(data={'rating': 4})
        assert form.is_valid()

        # Call the view
        response = project(request, project_obj.id)

        # Check that the response is a redirect
        assert response.status_code == 302
        assert response.url == reverse('project', kwargs={'project_id': project_obj.id})

        # Refresh the project from the database
        project_obj.refresh_from_db()

        # Check that the project rating has been updated
        assert project_obj.rating == 3.5

    def test_project_reject_nonexistent_request(self, setup_5):
        """
        Test that the view handles rejecting a non-existent join request.
        """
        request = self.factory.post(reverse('project', kwargs={'project_id': self.project.id}), {'reject_request': '9999'})
        request.user = self.user
        with pytest.raises(Http404):
            project(request, self.project.id)

    def test_register_2(self):
        """
        Test that authenticated users are redirected to home page when accessing register page
        """
        # Create a user and log them in
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Try to access the register page
        response = self.client.get(self.register_url)

        # Check if the user is redirected to the home page
        self.assertRedirects(response, self.home_url)

    def test_register_3(self):
        """
        Test that authenticated users are redirected to home when accessing the register page.
        """
        # Create and log in a user
        user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Access the register page
        response = self.client.get(self.register_url)

        # Check if the user is redirected to the home page
        self.assertRedirects(response, self.home_url)

    def test_register_4(self):
        """
        Test that authenticated users are redirected to home page when accessing register page.
        """
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Attempt to access the register page
        response = self.client.get(self.register_url)

        # Check if the user is redirected to the home page
        self.assertRedirects(response, self.home_url)

    def test_register_5(self):
        """
        Test that authenticated users are redirected to home page when accessing register.
        """
        # Create a user
        user = User.objects.create_user(username='testuser', password='12345')

        # Create a GET request
        request = self.factory.get(reverse('register'))

        # Simulate a logged-in user
        request.user = user

        # Add session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

        # Add messages middleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Call the view
        response = register(request)

        # Check that we got a redirect response
        assert response.status_code == 302

        # Check it's redirecting to the home page
        assert response.url == reverse('home')

    def test_register_7(self):
        """
        Test that authenticated users are redirected to home page when accessing register view
        """
        request = self.factory.get(reverse('register'))
        request.user = self.user

        response = register(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_register_9(self):
        """
        Test that authenticated users are redirected to home page when accessing register view.
        """
        # Create a request factory
        factory = RequestFactory()

        # Create a user
        user = User.objects.create_user(username='testuser', password='12345')

        # Create a GET request to the register view
        request = factory.get(reverse('register'))

        # Simulate an authenticated user
        request.user = user
        request.user.is_authenticated = True

        # Call the register view
        response = register(request)

        # Check if the response is a redirect
        assert isinstance(response, type(redirect('home')))
        assert response.url == reverse('home')

    def test_register_authenticated_user(self):
        """
        Test that an authenticated user is redirected to home page when accessing the register view.
        """
        request = self.factory.get(reverse('register'))
        request.user = self.user
        response = register(request)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_register_authenticated_user_2(self, factory):
        """Test registration attempt by an already authenticated user"""
        request = factory.post(reverse('register'))
        request.user = MagicMock(is_authenticated=True)

        response = register(request)
        assert response.status_code == 302
        assert response.url == reverse('home')

    def test_register_authenticated_user_redirect(self):
        """
        Test that an authenticated user is redirected to home when accessing the register page.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('home'))

    def test_register_authenticated_user_redirects_to_home(self, request_factory, authenticated_user):
        """
        Test that an authenticated user is redirected to home when accessing the register page.
        """
        request = request_factory.get('/register/')
        request.user = authenticated_user

        response = register(request)

        assert response.status_code == 302
        assert response.url == reverse('home')

    @patch('projects.views.upload')
    def test_register_cloudinary_exception(self, mock_upload, factory):
        """Test registration when Cloudinary upload fails"""
        mock_upload.side_effect = Exception("Cloudinary upload failed")

        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'profile_picture': MagicMock(name='profile.jpg'),
        }
        request = factory.post(reverse('register'), data=data)
        request.user = MagicMock(is_authenticated=False)
        request.FILES = {'profile_picture': MagicMock(name='profile.jpg')}
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = register(request)
        assert response.status_code == 200
        assert 'form' in response.context
        assert any(message.message == "Issue uploading the profile picture." for message in messages.get_messages(request))

    @patch('projects.views.messages')
    @patch('projects.views.upload')
    def test_register_cloudinary_upload_error(self, mock_upload, mock_messages):
        mock_upload.side_effect = Exception("Cloudinary upload failed")
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'grade_level': 'Junior',
            'concentration': 'Artificial Intelligence',
            'linkedin': 'https://linkedin.com/newuser',
            'github': 'https://github.com/newuser',
            'bio': 'This is a test bio',
            'current_step': '3'
        }
        
        profile_picture = SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg")
        
        response = self.client.post(reverse('register'), data=data, files={'profile_picture': profile_picture})
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        mock_messages.error.assert_called_once_with(response.wsgi_request, "Issue uploading the profile picture.")

    def test_register_empty_input(self, factory):
        """Test registration with empty input"""
        request = factory.post(reverse('register'), data={})
        request.user = MagicMock(is_authenticated=False)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = register(request)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

    def test_register_existing_username(self, factory):
        """Test registration with an existing username"""
        User.objects.create_user(username='existinguser', email='existing@example.com', password='testpass123')
        
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        request = factory.post(reverse('register'), data=data)
        request.user = MagicMock(is_authenticated=False)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = register(request)
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'username' in response.context['form'].errors

    def test_register_form_error_handling(self):
        data = {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'Existing',
            'last_name': 'User',
            'current_step': '1'
        }
        
        # Create a user with the same username and email
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        
        response = self.client.post(reverse('register'), data=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/register.html')
        self.assertEqual(response.context['current_step'], 1)
        self.assertFalse(User.objects.filter(first_name='Existing').exists())

    def test_register_get_request(self):
        response = self.client.get(reverse('register'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
        self.assertEqual(response.context['current_step'], 1)

    def test_register_invalid_email(self, factory):
        """Test registration with invalid email format"""
        data = {
            'username': 'testuser',
            'email': 'invalid_email',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        request = factory.post(reverse('register'), data=data)
        request.user = MagicMock(is_authenticated=False)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = register(request)
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'email' in response.context['form'].errors

    def test_register_invalid_form_submission(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'short',
            'password2': 'nomatch',
            'current_step': '1'
        }
        
        response = self.client.post(reverse('register'), data=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/register.html')
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_multi_step_form(self):
        # Step 1
        step1_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'current_step': '1'
        }
        response = self.client.post(reverse('register'), data=step1_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_step'], 2)

        # Step 2
        step2_data = {
            **step1_data,
            'grade_level': 'Sophomore',
            'concentration': 'Data Science',
            'current_step': '2'
        }
        response = self.client.post(reverse('register'), data=step2_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_step'], 3)

        # Step 3 (final step)
        step3_data = {
            **step2_data,
            'linkedin': 'https://linkedin.com/newuser',
            'github': 'https://github.com/newuser',
            'bio': 'Final step bio',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'current_step': '3'
        }
        response = self.client.post(reverse('register'), data=step3_data)
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self, factory):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'mismatchedpassword',
        }
        request = factory.post(reverse('register'), data=data)
        request.user = MagicMock(is_authenticated=False)
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = register(request)
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'password2' in response.context['form'].errors

    @patch('projects.views.upload')
    def test_register_valid_form_submission(self, mock_upload):
        mock_upload.return_value = {'url': 'http://test-url.com/image.jpg'}
        
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'first_name': 'New',
            'last_name': 'User',
            'grade_level': 'Freshman',
            'concentration': 'Computer Science',
            'linkedin': 'https://linkedin.com/newuser',
            'github': 'https://github.com/newuser',
            'bio': 'This is a test bio',
            'current_step': '3'
        }
        
        profile_picture = SimpleUploadedFile("profile.jpg", b"file_content", content_type="image/jpeg")
        
        response = self.client.post(reverse('register'), data=data, files={'profile_picture': profile_picture})
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Check if user and profile were created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(UserProfile.objects.filter(user__username='newuser').exists())

    @pytest.mark.django_db
    def test_search_users_database_error(self, factory, users, monkeypatch):
        """
        Test search_users with simulated database error
        """
        def mock_filter(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(User.objects, 'filter', mock_filter)

        request = factory.get('/search_users/?q=test')
        with pytest.raises(Exception):
            search_users(request)

    def test_search_users_empty_input(self, factory, users):
        """
        Test search_users with empty input
        """
        request = factory.get('/search_users/?q=')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_long_input(self, factory, users):
        """
        Test search_users with extremely long input
        """
        long_query = 'a' * 1000
        request = factory.get(f'/search_users/?q={long_query}')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_no_query_parameter(self, factory, users):
        """
        Test search_users with no query parameter
        """
        request = factory.get('/search_users/')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_non_ascii_characters(self, factory, users):
        """
        Test search_users with non-ASCII characters
        """
        request = factory.get('/search_users/?q=테스트')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_special_characters(self, factory, users):
        """
        Test search_users with special characters
        """
        request = factory.get('/search_users/?q=!@#$%^&*()')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_sql_injection_attempt(self, factory, users):
        """
        Test search_users with potential SQL injection attempt
        """
        request = factory.get('/search_users/?q=1\' OR \'1\'=\'1')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_whitespace_input(self, factory, users):
        """
        Test search_users with whitespace input
        """
        request = factory.get('/search_users/?q=   ')
        response = search_users(request)
        assert isinstance(response, JsonResponse)
        assert response.content == b'[]'

    def test_search_users_with_valid_query(self):
        """
        Test search_users function with a valid query string.
        Expects to return matching users as a JsonResponse.
        """
        # Create test users
        User.objects.create_user(username='john_doe', first_name='John', last_name='Doe')
        User.objects.create_user(username='jane_doe', first_name='Jane', last_name='Doe')
        User.objects.create_user(username='alice_smith', first_name='Alice', last_name='Smith')

        # Create a request with a query
        factory = RequestFactory()
        request = factory.get('/search_users/', {'q': 'doe'})

        # Call the search_users function
        response = search_users(request)

        # Check if the response is a JsonResponse
        assert isinstance(response, JsonResponse)

        # Parse the JSON content
        content = json.loads(response.content)

        # Check if the correct number of users are returned
        assert len(content) == 2

        # Check if the returned users are correct
        assert any(user['username'] == 'john_doe' for user in content)
        assert any(user['username'] == 'jane_doe' for user in content)
        assert not any(user['username'] == 'alice_smith' for user in content)

        # Check the structure of the returned data
        for user in content:
            assert 'username' in user
            assert 'full_name' in user

        # Check if the full names are correct
        assert any(user['full_name'] == 'John Doe' for user in content)
        assert any(user['full_name'] == 'Jane Doe' for user in content)

    def test_settings_page_1(self):
        """
        Test settings page when POST request is made with valid form data for updating settings.
        """
        url = reverse('settings')
        request = self.factory.post(url, data={
            'update_settings': True,
            'bio': 'New bio',
            'linkedin': 'https://linkedin.com/testuser',
            'github': 'https://github.com/testuser'
        })
        request.user = self.user

        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with patch.object(UserSettingsForm, 'is_valid', return_value=True):
            with patch.object(UserSettingsForm, 'save') as mock_save:
                response = settings_page(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('settings'))
        mock_save.assert_called_once()

    def test_settings_page_2(self, setup_2):
        """
        Test changing password successfully in settings page
        """
        request = self.factory.post('/settings/', {
            'change_password': True,
            'old_password': '12345',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        })
        request.user = self.user
        
        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        assert response.status_code == 302
        assert response.url == reverse('settings')

        # Verify that the password was changed
        self.user.refresh_from_db()
        assert self.user.check_password('newpassword123')

    def test_settings_page_3(self, setup, mocker):
        """
        Test settings_page when POST request is made with invalid form data for update_settings.
        """
        request = self.factory.post('/settings/', data={'update_settings': True})
        request.user = self.user

        # Mock UserSettingsForm
        mock_form = mocker.Mock(spec=UserSettingsForm)
        mock_form.is_valid.return_value = False
        mocker.patch('projects.views.UserSettingsForm', return_value=mock_form)

        # Mock PasswordChangeForm
        mock_password_form = mocker.Mock(spec=PasswordChangeForm)
        mocker.patch('projects.views.PasswordChangeForm', return_value=mock_password_form)

        # Mock render function
        mock_render = mocker.patch('projects.views.render')

        response = settings_page(request)

        # Assert that render was called with correct arguments
        mock_render.assert_called_once_with(
            request, 
            'projects/settings.html', 
            {'form': mock_form, 'password_form': mock_password_form}
        )

        # Assert that form.save() was not called
        mock_form.save.assert_not_called()

        # Assert that no success message was added
        assert not messages.success.called

    def test_settings_page_4(self):
        """
        Test settings_page view when POST request is made without 'update_settings' or 'change_password' in POST data.
        """
        request = self.factory.post('/settings/')
        request.user = self.user

        # Add messages middleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/settings.html')
        
        # Check if the correct forms are in the context
        self.assertIsInstance(response.context['form'], UserSettingsForm)
        self.assertIsInstance(response.context['password_form'], PasswordChangeForm)

        # Verify that no success messages were added
        self.assertEqual(len(list(messages.get_messages(request))), 0)

        # Verify that the user profile wasn't changed
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile, UserProfile.objects.get(user=self.user))

        # Verify that the user's password wasn't changed
        self.assertTrue(self.user.check_password('testpass123'))

    def test_settings_page_5(self):
        """
        Test settings_page view when request method is GET.
        Ensures that the correct template is used and appropriate forms are passed to the context.
        """
        response = self.client.get(reverse('settings'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/settings.html')
        
        self.assertIsInstance(response.context['form'], UserSettingsForm)
        self.assertIsInstance(response.context['password_form'], PasswordChangeForm)
        
        self.assertEqual(response.context['form'].instance, self.user_profile)
        self.assertEqual(response.context['password_form'].user, self.user)

        # Verify that no messages were added (as this is a GET request)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)

    def test_settings_page_empty_password_change(self, setup_2):
        """
        Test settings_page with empty password change form
        """
        request = self.factory.post('/settings/', {'change_password': True})
        request.user = self.user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        assert response.status_code == 200
        assert 'password_form' in response.context_data
        assert response.context_data['password_form'].is_valid() == False

    def test_settings_page_incorrect_password_format(self, setup_2):
        """
        Test settings_page with incorrect password format
        """
        request = self.factory.post('/settings/', {
            'change_password': True,
            'old_password': '12345',
            'new_password1': 'short',
            'new_password2': 'short'
        })
        request.user = self.user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        assert response.status_code == 200
        assert 'password_form' in response.context_data
        assert response.context_data['password_form'].is_valid() == False

    def test_settings_page_invalid_form_data(self, setup_2):
        """
        Test settings_page with invalid form data
        """
        request = self.factory.post('/settings/', {'update_settings': True, 'email': 'invalid_email'})
        request.user = self.user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        assert response.status_code == 200
        assert 'form' in response.context_data
        assert response.context_data['form'].is_valid() == False

    def test_settings_page_mismatched_passwords(self, setup_2):
        """
        Test settings_page with mismatched new passwords
        """
        request = self.factory.post('/settings/', {
            'change_password': True,
            'old_password': '12345',
            'new_password1': 'newpassword123',
            'new_password2': 'differentpassword123'
        })
        request.user = self.user
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = settings_page(request)

        assert response.status_code == 200
        assert 'password_form' in response.context_data
        assert response.context_data['password_form'].is_valid() == False

    def test_settings_page_non_existent_user(self, setup_2):
        """
        Test settings_page with a non-existent user
        """
        non_existent_user = User(username='nonexistent')
        request = self.factory.get('/settings/')
        request.user = non_existent_user
        
        with pytest.raises(UserProfile.DoesNotExist):
            settings_page(request)

    def test_toggle_project_status_1(self, setup_6):
        """
        Test toggle_project_status when request method is POST
        """
        request = self.factory.post(reverse('toggle_project_status', args=[self.project.id]))
        request.user = self.user

        response = toggle_project_status(request, self.project.id)

        assert isinstance(response, type(redirect()))
        assert response.url == reverse('project', kwargs={'project_id': self.project.id})

        # Refresh the project from the database
        self.project.refresh_from_db()
        assert self.project.completed == True

    def test_toggle_project_status_get_request(self, setup_7):
        """
        Test toggle_project_status with a GET request instead of POST.
        """
        project = Project.objects.create(title="Test Project", owner=self.user)
        request = self.factory.get(f'/toggle_project_status/{project.id}/')
        request.user = self.user
        response = toggle_project_status(request, project_id=project.id)
        assert response is None

    def test_toggle_project_status_invalid_project_id(self, setup_7):
        """
        Test toggle_project_status with an invalid project ID.
        """
        request = self.factory.post('/toggle_project_status/999/')
        request.user = self.user
        with pytest.raises(Http404):
            toggle_project_status(request, project_id=999)

    def test_toggle_project_status_non_existent_project(self, setup_7):
        """
        Test toggle_project_status with a non-existent project ID.
        """
        request = self.factory.post('/toggle_project_status/9999/')
        request.user = self.user
        with pytest.raises(Http404):
            toggle_project_status(request, project_id=9999)

    def test_toggle_project_status_string_project_id(self, setup_7):
        """
        Test toggle_project_status with a string project ID.
        """
        request = self.factory.post('/toggle_project_status/abc/')
        request.user = self.user
        with pytest.raises(ValueError):
            toggle_project_status(request, project_id='abc')

    def test_toggle_project_status_unauthorized_user(self, setup_7):
        """
        Test toggle_project_status with a user who doesn't own the project.
        """
        project = Project.objects.create(title="Test Project", owner=User.objects.create_user(username='otheruser'))
        request = self.factory.post(f'/toggle_project_status/{project.id}/')
        request.user = self.user
        with pytest.raises(Http404):
            toggle_project_status(request, project_id=project.id)

    def test_unfollow_user_2(self):
        """
        Test case for unfollow_user when the user tries to unfollow themselves.
        """
        request = self.factory.get(reverse('unfollow_user', args=['testuser']))
        request.user = self.user

        response = unfollow_user(request, 'testuser')

        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)

        # Check if the redirect URL is correct
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'testuser'}))

        # Ensure no Follow object was deleted (since user can't unfollow themselves)
        self.assertEqual(Follow.objects.count(), 0)

    def test_unfollow_user_exception_handling(self, setup_users_4, mocker):
        """
        Test exception handling in unfollow_user
        """
        request = self.factory.get(reverse('unfollow_user', kwargs={'username': self.user_to_unfollow.username}))
        request.user = self.user
        
        # Mock the Follow.objects.filter().delete() to raise an exception
        mocker.patch('projects.models.Follow.objects.filter', side_effect=Exception('Database error'))
        
        with pytest.raises(Exception):
            unfollow_user(request, self.user_to_unfollow.username)

    def test_unfollow_user_invalid_username(self, setup_users_4):
        """
        Test unfollow_user with an invalid username
        """
        request = self.factory.get(reverse('unfollow_user', kwargs={'username': 'nonexistentuser'}))
        request.user = self.user
        
        with pytest.raises(Exception):  # Expecting a 404 error
            unfollow_user(request, 'nonexistentuser')

    def test_unfollow_user_non_existent(self):
        """
        Test unfollow_user with a non-existent user.
        It should raise a 404 error.
        """
        # Create a request
        request = self.factory.post(reverse('unfollow_user', kwargs={'username': 'nonexistent'}))
        request.user = self.user

        # Call the view and expect a 404 error
        with self.assertRaises(ValueError):
            unfollow_user(request, username='nonexistent')

    def test_unfollow_user_not_following(self):
        """
        Test unfollow_user when the user is not following another user.
        It should not raise any error and redirect to the profile page.
        """
        # Create a request
        request = self.factory.post(reverse('unfollow_user', kwargs={'username': 'userunfollow'}))
        request.user = self.user

        # Call the view
        response = unfollow_user(request, username='userunfollow')

        # Check if it redirects to the profile page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'userunfollow'}))

    def test_unfollow_user_not_following_2(self, setup_users_4):
        """
        Test unfollowing a user that is not being followed
        """
        request = self.factory.get(reverse('unfollow_user', kwargs={'username': self.user_to_unfollow.username}))
        request.user = self.user
        
        response = unfollow_user(request, self.user_to_unfollow.username)
        assert response.status_code == 302

    def test_unfollow_user_own_account(self, setup_users_4):
        """
        Test attempting to unfollow own account
        """
        request = self.factory.get(reverse('unfollow_user', kwargs={'username': self.user.username}))
        request.user = self.user
        
        response = unfollow_user(request, self.user.username)
        assert response.status_code == 302

    def test_unfollow_user_self(self):
        """
        Test unfollow_user when trying to unfollow oneself.
        It should not delete any relationship and redirect to the profile page.
        """
        # Create a request
        request = self.factory.post(reverse('unfollow_user', kwargs={'username': 'testuser'}))
        request.user = self.user

        # Call the view
        response = unfollow_user(request, username='testuser')

        # Check if it redirects to the profile page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'testuser'}))

    def test_unfollow_user_success(self):
        """
        Test unfollow_user when the user is following another user.
        It should delete the Follow relationship and redirect to the profile page.
        """
        # Create a follow relationship
        Follow.objects.create(follower=self.user, following=self.user_to_unfollow)

        # Create a request
        request = self.factory.post(reverse('unfollow_user', kwargs={'username': 'userunfollow'}))
        request.user = self.user

        # Call the view
        response = unfollow_user(request, username='userunfollow')

        # Check if the follow relationship is deleted
        self.assertFalse(Follow.objects.filter(follower=self.user, following=self.user_to_unfollow).exists())

        # Check if it redirects to the profile page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profile', kwargs={'username': 'userunfollow'}))

    def test_unfollow_user_unauthenticated(self, setup_users_4):
        """
        Test unfollow_user with an unauthenticated user
        """
        request = self.factory.get(reverse('unfollow_user', kwargs={'username': self.user_to_unfollow.username}))
        request.user = None
        
        with pytest.raises(Exception):  # Expecting an authentication error
            unfollow_user(request, self.user_to_unfollow.username)

    @pytest.mark.django_db
    @patch('projects.views.upload')
    def test_upload_banner_1(self, mock_upload):
        """
        Test successful banner upload for a user's profile.
        """
        # Set up test data
        user = User.objects.create_user(username='testuser', password='12345')
        user_profile = UserProfile.objects.create(user=user)
        
        # Mock the Cloudinary upload function
        mock_upload.return_value = {'secure_url': 'https://example.com/banner.jpg'}
        
        # Create a request
        factory = RequestFactory()
        request = factory.post(reverse('upload_banner', kwargs={'username': 'testuser'}))
        request.user = user
        
        # Add messages middleware to the request
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        # Create a mock file
        mock_file = MagicMock()
        mock_file.name = 'test_banner.jpg'
        request.FILES = {'banner_picture': mock_file}
        
        # Call the view function
        response = upload_banner(request, 'testuser')
        
        # Check if the redirect is correct
        assert response.status_code == 302
        assert response.url == reverse('profile', kwargs={'username': 'testuser'})
        
        # Check if the UserProfile was updated
        user_profile.refresh_from_db()
        assert user_profile.banner_picture_url == 'https://example.com/banner.jpg'
        
        # Verify that Cloudinary upload was called
        mock_upload.assert_called_once_with(mock_file, folder="banner_pics/", overwrite=True)

    @pytest.mark.django_db
    def test_upload_banner_2(self):
        """
        Test upload_banner view when POST request is made without a banner picture.
        """
        # Create a test user and user profile
        user = User.objects.create_user(username='testuser', password='12345')
        UserProfile.objects.create(user=user)

        # Create a POST request
        factory = RequestFactory()
        request = factory.post(reverse('upload_banner', kwargs={'username': 'testuser'}))
        request.user = user

        # Add messages middleware
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        # Call the view
        response = upload_banner(request, 'testuser')

        # Check that the response is a redirect to the profile page
        assert response.status_code == 302
        assert response.url == reverse('profile', kwargs={'username': 'testuser'})

        # Verify that no changes were made to the user profile
        user_profile = UserProfile.objects.get(user=user)
        assert user_profile.banner_picture_url is None

    def test_upload_banner_3(self, setup_3):
        """
        Test upload_banner view when the request method is not POST.
        """
        url = reverse('upload_banner', kwargs={'username': self.user.username})
        request = self.factory.get(url)
        request.user = self.user

        response = upload_banner(request, self.user.username)

        assert response.status_code == 302
        assert response.url == reverse('profile', kwargs={'username': self.user.username})

    def test_upload_banner_cloudinary_error(self, setup_3):
        """
        Test handling of Cloudinary upload errors.
        """
        request = self.factory.post('/upload_banner/testuser/', {'banner_picture': SimpleUploadedFile("banner.jpg", b"valid content")})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with patch('projects.views.upload') as mock_upload:
            mock_upload.side_effect = Exception("Cloudinary error")
            response = upload_banner(request, 'testuser')

        assert isinstance(response, HttpResponseRedirect)
        assert len(messages._queued_messages) == 1
        assert "There was an issue uploading your banner." in str(messages._queued_messages[0])

    def test_upload_banner_empty_file(self, setup_3):
        """
        Test uploading an empty file for the banner picture.
        """
        request = self.factory.post('/upload_banner/testuser/', {'banner_picture': SimpleUploadedFile("banner.jpg", b"")})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = upload_banner(request, 'testuser')
        assert isinstance(response, HttpResponseRedirect)
        assert len(messages._queued_messages) == 0

    def test_upload_banner_file_too_large(self, setup_3):
        """
        Test uploading a file that exceeds the size limit for the banner picture.
        """
        large_file = SimpleUploadedFile("large_banner.jpg", b"a" * (10 * 1024 * 1024))  # 10MB file
        request = self.factory.post('/upload_banner/testuser/', {'banner_picture': large_file})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with patch('projects.views.upload') as mock_upload:
            mock_upload.side_effect = Exception("File too large")
            response = upload_banner(request, 'testuser')

        assert isinstance(response, HttpResponseRedirect)
        assert len(messages._queued_messages) == 1
        assert "There was an issue uploading your banner." in str(messages._queued_messages[0])

    def test_upload_banner_invalid_file_type(self, setup_3):
        """
        Test uploading a file with an invalid type for the banner picture.
        """
        request = self.factory.post('/upload_banner/testuser/', {'banner_picture': SimpleUploadedFile("banner.txt", b"invalid content")})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with patch('projects.views.upload') as mock_upload:
            mock_upload.side_effect = Exception("Invalid file type")
            response = upload_banner(request, 'testuser')

        assert isinstance(response, HttpResponseRedirect)
        assert len(messages._queued_messages) == 1
        assert "There was an issue uploading your banner." in str(messages._queued_messages[0])

    def test_upload_banner_non_existent_user(self, setup_3):
        """
        Test uploading a banner for a non-existent user.
        """
        request = self.factory.post('/upload_banner/nonexistentuser/', {'banner_picture': SimpleUploadedFile("banner.jpg", b"valid content")})
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        with pytest.raises(Exception):  # Expecting a 404 error
            upload_banner(request, 'nonexistentuser')

    def test_upload_banner_unauthorized_user(self, setup_3):
        """
        Test uploading a banner for a user that is not the logged-in user.
        """
        other_user = User.objects.create_user(username='otheruser', password='12345')
        UserProfile.objects.create(user=other_user)

        request = self.factory.post('/upload_banner/otheruser/', {'banner_picture': SimpleUploadedFile("banner.jpg", b"valid content")})
        request.user = self.user  # Logged in as 'testuser'
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = upload_banner(request, 'otheruser')
        assert isinstance(response, HttpResponseRedirect)
        # Expecting no changes or error messages as the action should be silently ignored for unauthorized users
        assert len(messages._queued_messages) == 0

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='12345')

    @pytest.fixture
    def users(self):
        User.objects.create_user(username='testuser1', first_name='Test', last_name='User1')
        User.objects.create_user(username='testuser2', first_name='Test', last_name='User2')