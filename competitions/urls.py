from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'competitions'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('attend/<int:pk>', login_required(views.AttendView.post_new), name='attend'),
    path('invite/<int:pk>', login_required(views.InviteView.as_view()), name='invite'),
    path('ongoing/', views.OngoingView.as_view(), name='ongoing'),
    path('ongoing/search', views.OngoingView.as_view(), name='ongoing_search'),
    path('scheduled/', views.ScheduledView.as_view(), name='scheduled'),
    path('scheduled/search', views.ScheduledView.as_view(), name='scheduled_search'),
    path('past/current', views.CurrentPastView.as_view(), name='past_current'),
    path('past/current/search', views.CurrentPastView.as_view(), name='past_current_search'),
    path('past/last', views.LastPastView.as_view(), name='past_last'),
    path('past/last/search', views.LastPastView.as_view(), name='past_last_search'),
    path('past/lastlast', views.LastLastPastView.as_view(), name='past_last_last'),
    path('past/lastlast/search', views.LastLastPastView.as_view(), name='past_last_last_search'),
    path('create/', views.CreateView.post_new, name='create'),
    path('brackets/<int:pk>', views.BracketsView.as_view(), name='brackets'),
    path('match/<int:pk>', views.MatchView.as_view(), name='match'),
    path('match/edit/<int:pk>', views.MatchEditView.as_view(), name='matchedit'),

    path('match/<int:match_pk>/new_comment', views.MatchView.comment, name='new_comment'),
    path('match/<int:match_pk>/delete_comment/<int:comment_pk>', views.MatchView.delete, name='delete_comment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
