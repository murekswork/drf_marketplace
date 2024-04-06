from rest_framework.throttling import SimpleRateThrottle


class OncePerHourThrottleForPost(SimpleRateThrottle):

    scope = "once_per_hour"

    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        return True

    # TODO: CHANGE TO 1/HOUR

    def get_rate(self):
        return "1/min"

    def get_cache_key(self, request, view):
        return f'{self.scope}_{request.user.id or request.META.get("REMOTE_ADDR")}'
