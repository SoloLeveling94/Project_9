from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .forms import ReviewForm
from .views import (
    TicketListView,
    TicketDetailView,
    TicketCreateView,
    TicketUpdateView,
    TicketDeleteView,
    ReviewListView,
    ReviewDetailView,
    ReviewCreateView,
    ReviewUpdateView,
    ReviewDeleteView,
    FollowerListView,
    FollowerDeleteView,
    PostView,
    ReviewTicketCreateView,
)


urlpatterns = [
    path('ticket/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),
    path('ticket/<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_edit'),
    path('ticket/new/', TicketCreateView.as_view(), name='ticket_new'),
    path('ticket/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    # path('', TicketListView.as_view(), name='home'),
    path('', ReviewListView.as_view(), name='home'),
    path('review/<int:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    path('review/new/', ReviewCreateView.as_view(), name='review_new'),
    path('review/<int:pk>/edit/', ReviewUpdateView.as_view(), name='review_edit'),
    path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
    path('follower/', FollowerListView.as_view(), name='follower_list'),
    path('follower/<int:pk>/delete', FollowerDeleteView.as_view(), name='follower_delete'),
    path('post/', PostView.as_view(), name='post'),
    path('review/answer/<int:pk>', ReviewTicketCreateView.as_view(), name='reviewticket_new'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
