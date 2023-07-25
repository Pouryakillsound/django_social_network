from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('',views.HomeView.as_view(),name='home'),
    path('detail/<int:post_id>/<slug:post_slug>/', views.DetailView.as_view(), name = 'detail'),
    path('delete/<int:post_id>/', views.PostDeleteView.as_view(), name = 'delete'),
    path('update/<int:post_id>', views.PostUpdateView.as_view(), name='update'),
    path('create/', views.PostCreateView.as_view(), name = 'create'),
    path('comment/delete/<int:comment_id>/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('comment/reply/<int:post_id>/<int:comment_id>/', views.CommentReplyCreateView.as_view(), name='reply'),
    path('like/<int:post_id>/', views.LikeCreateView.as_view(), name='like'),
    path('unlike/<int:post_id>/', views.LikeDeleteView.as_view(), name='unlike'),
    path('test/', views.Test.as_view())
]