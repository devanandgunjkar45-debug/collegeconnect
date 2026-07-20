from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        login_url = reverse('core:login')
        register_url = reverse('core:register')
        exempt_paths = [login_url, register_url, '/admin/login/', '/admin/logout/']

        if settings.DEBUG:
            if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
                return self.get_response(request)

        public_paths = [
            '/',
            '/about/',
            '/contact/',
            '/faq/',
            '/announcements/',
            '/register/',
            '/login/',
            '/events/',
        ]

        if path in exempt_paths or path.startswith('/admin/'):
            return self.get_response(request)

        # allow public pages and event browsing without login
        if path == '/' or path in public_paths or any(path.startswith(prefix) for prefix in ['/events/', '/announcements/']):
            return self.get_response(request)

        if request.user.is_authenticated:
            return self.get_response(request)

        return redirect(f'{login_url}?next={path}')
