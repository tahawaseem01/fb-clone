from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('newsfeed/', views.newsfeed, name='newsfeed'),
    path('search/', views.search_users, name='search_users'),
    path('send-friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('people-you-may-know/', views.people_you_may_know, name='people_you_may_know'),
    path('friend-requests/', views.view_friend_requests, name='view_friend_requests'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_request'),
    path('decline-request/<int:request_id>/', views.decline_friend_request, name='decline_request'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notification/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('messages/<int:user_id>/', views.message_user, name='message_user'),
    path('friends/messaging/', views.friends_list_for_messaging, name='friends_list_for_messaging'),
    path('search/', views.search_users, name='search_users'),
    path('ajax/search-users/', views.ajax_search_users, name='ajax_search_users'),
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),


]

