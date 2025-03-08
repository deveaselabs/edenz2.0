from django.contrib.auth.mixins import UserPassesTestMixin

class BusinessRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == 'BUSINESS' and self.request.user.approved