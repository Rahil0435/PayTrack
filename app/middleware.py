from django.utils.deprecation import MiddlewareMixin

class PreventBackAfterLogoutMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.user.is_authenticated:  # If user is logged out
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
