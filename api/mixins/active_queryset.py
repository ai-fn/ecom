class ActiveQuerysetMixin:
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        if self.request.user.is_staff:
            return queryset

        return queryset.filter(is_active=True)
