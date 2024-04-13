from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q

from delivery.models import Delivery


class ObservationView(TemplateView):
    template_name = 'observation/index.html'

    def get_context_data(self, **kwargs):
        delivering_couriers_qs = Delivery.objects.filter(Q(status=3) | Q(status=3)).values('courier')
        context = super().get_context_data(**kwargs)
        context['couriers'] = delivering_couriers_qs
        print(context)
        return context
