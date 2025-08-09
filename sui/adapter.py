from allauth.account.adapter import DefaultAccountAdapter


class NoSignupAccountAdapter(DefaultAccountAdapter):
    """Account adapter that disables user self-registration."""

    def is_open_for_signup(self, request):  # pragma: no cover - configuration only
        return False

