
from django.http import HttpResponse
import traceback

class FriendlyErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log full traceback in the console
            print("ERROR:", e)
            traceback.print_exc()

            # Return user-friendly response
            return HttpResponse("An error occurred", status=500)

        return response
