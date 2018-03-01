from django.urls import path
from django.views.generic import TemplateView


app_name = 'masterchess'
urlpatterns = [
	path('', TemplateView.as_view(template_name="masterchess/index.html")),
]