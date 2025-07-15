from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User,Profile,Notification, Message
from django.contrib.auth.decorators import login_required
from .forms import PostForm, ProfileForm
from .models import Post, Like, Comment,Follow,FriendRequest
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        profile_pic = request.FILES.get('profile_pic')
        cover_pic = request.FILES.get('cover_pic')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        if profile_pic:
            profile = user.profile
            profile.profile_pic = profile_pic
            profile.save()
        if cover_pic:
            profile = user.profile
            profile.cover_pic = cover_pic
            profile.save()
        return redirect('login')
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print("👤 Username:", username)
        print("🔒 Password:", password)

        user = authenticate(request, username=username, password=password)
        print("✅ User found:", user)
        if user:
            login(request, user)
            print("🎉 Logged in:", user.username)
            return redirect('newsfeed')  
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')
    


def redirect_to_login(request):
    print("➡️ Redirecting to /accounts/login/")
    return redirect('login')  # 'login' is the name used in accounts/urls.py


def logout_view(request):
    logout(request)
    return redirect('login')


def get_friends(user):
    sent = FriendRequest.objects.filter(sender=user, status='accepted').values_list('receiver_id', flat=True)
    received = FriendRequest.objects.filter(receiver=user, status='accepted').values_list('sender_id', flat=True)
    return User.objects.filter(id__in=list(sent) + list(received))


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    posts = Post.objects.filter(user=request.user).order_by('-created_at')

    # Get all users except the current one
    users = User.objects.exclude(id=request.user.id)

    # Build follow status dictionary
    follow_status = {
        u.id: Follow.objects.filter(follower=request.user, following=u).exists()
        for u in users
    }
    friends = get_friends(request.user)
  

    return render(request, 'profile.html',   {
        'user_profile': request.user,
        'profile': profile,
        'posts': posts,
        'users': users,
        'follow_status': follow_status,
        'friends_count': friends.count(),
        'is_own_profile': True,
        'is_friend': True,  # They are their own friend
        'friend_request_sent': False,
        'current_page': 'profile'
    })


@login_required
def edit_profile(request):
    profile = request.user.profile  # assuming OneToOneField between User and Profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('profile')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()  # Unlike if already liked
    return redirect('profile')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST['content']
        Comment.objects.create(user=request.user, post=post, content=content)
    return redirect('profile')


@login_required
def people_you_may_know(request):
    current_user = request.user

    # Get users excluding self and already connected or requested
    sent = FriendRequest.objects.filter(sender=current_user).values_list('receiver_id', flat=True)
    received = FriendRequest.objects.filter(receiver=current_user).values_list('sender_id', flat=True)
    friends = list(sent) + list(received)

    suggestions = User.objects.exclude(id=current_user.id).exclude(id__in=friends)

    return render(request, 'people_you_may_know.html', {
        'suggestions': suggestions,
        'current_page': 'suggestions' 
    })


# @login_required
# def newsfeed(request):
#     # Get all posts (you can filter by following if needed)
#     # posts = Post.objects.all().order_by('-created_at')
#     user = request.user
#     friends = get_friends(request.user)
#     posts = Post.objects.filter(user__in=list(friends) + [request.user]).order_by('-created_at')

#     # Build list of friends with unread message counts
#     friends_with_unread = []
#     for friend in friends:
#         unread_count = Message.objects.filter(sender=friend, recipient=user, is_read=False).count()
#         friends_with_unread.append({
#             'friend': friend,
#             'unread_count': unread_count,
#         })

#     # Get message notification count
#     message_notifications_count = Notification.objects.filter(
#         recipient=user,
#         is_read=False,
#         type='message'
#     ).count()


#     # Get accepted friends
#     sent_friends = FriendRequest.objects.filter(sender=request.user, status='accepted').values_list('receiver', flat=True)
#     received_friends = FriendRequest.objects.filter(receiver=request.user, status='accepted').values_list('sender', flat=True)

#     friend_ids = list(sent_friends) + list(received_friends)
#     friends = User.objects.filter(id__in=friend_ids)

#     message_notifications_count = Notification.objects.filter(
#         recipient=request.user,
#         is_read=False,
#         type='message'
#     ).count()

#     pending_count = FriendRequest.objects.filter(receiver=request.user, status='pending').count()

#     unread_notifications_count = Notification.objects.filter(
#         recipient=request.user,
#         is_read=False
#     ).exclude(verb="sent you a message").count()

#     return render(request, 'newsfeed.html', {
#         'posts': posts,
#         'friends': friends,
#         'current_page': 'newsfeed',
#         'message_notifications_count': message_notifications_count,
#         'pending_count': pending_count,
#         'unread_notifications_count': unread_notifications_count,
#         'friends_with_unread': friends_with_unread,
        
#     })

@login_required
def newsfeed(request):
    user = request.user
    friends = get_friends(user)
    posts = Post.objects.filter(user__in=list(friends) + [user]).order_by('-created_at')

    # Build list of friends with unread message counts
    friends_with_unread = []
    for friend in friends:
        unread_count = Message.objects.filter(sender=friend, recipient=user, is_read=False).count()
        friends_with_unread.append({
            'friend': friend,
            'unread_count': unread_count,
        })

    # Get accepted friends separately for another use
    sent_friends = FriendRequest.objects.filter(sender=user, status='accepted').values_list('receiver', flat=True)
    received_friends = FriendRequest.objects.filter(receiver=user, status='accepted').values_list('sender', flat=True)
    accepted_friends = User.objects.filter(id__in=list(sent_friends) + list(received_friends))

    # Notifications
    message_notifications_count = Notification.objects.filter(
        recipient=user,
        is_read=False,
        type='message'
    ).count()

    unread_notifications_count = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).exclude(verb="sent you a message").count()

    pending_count = FriendRequest.objects.filter(receiver=user, status='pending').count()

    return render(request, 'newsfeed.html', {
        'posts': posts,
        'friends': accepted_friends,  # These can be used elsewhere
        'friends_with_unread': friends_with_unread,  # For chat box
        'current_page': 'newsfeed',
        'message_notifications_count': message_notifications_count,
        'pending_count': pending_count,
        'unread_notifications_count': unread_notifications_count,
    })




@login_required
def send_friend_request(request, user_id):
    receiver = User.objects.get(id=user_id)
    FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    print("📩 Creating notification for:", receiver.username)

    Notification.objects.create(
        recipient=receiver,
        sender=request.user,
        verb="sent you a friend request",
        url='/accounts/friend-requests/'  # or use reverse()
    )
    return redirect('people_you_may_know')


@login_required
def accept_friend_request(request, request_id):
    fr = FriendRequest.objects.get(id=request_id, receiver=request.user)
    fr.status = 'accepted'
    fr.save()
    # Optionally, add both users to each other's friend list
    Notification.objects.filter(
        sender=fr.sender,
        recipient=request.user,
        verb="sent you a friend request"
    ).update(
        verb="You and {} are now friends".format(fr.sender.username)
    )
    Notification.objects.create(
    recipient=fr.sender,
    sender=request.user,
    verb="accepted your friend request",
    url='/accounts/profile/'  # or wherever you want to redirect
    )

    return redirect('view_friend_requests')


@login_required
def decline_friend_request(request, request_id):
    fr = FriendRequest.objects.get(id=request_id, receiver=request.user)
    fr.status = 'declined'
    fr.save()
    return redirect('view_friend_requests')


@login_required
def view_friend_requests(request):
    incoming_requests = FriendRequest.objects.filter(receiver=request.user, status='pending')
    return render(request, 'friend_requests.html', {'incoming_requests': incoming_requests})


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-timestamp').exclude(type='message')
    print(f"🔔 Checking notifications for: {request.user}")
    print(Notification.objects.filter(recipient=request.user))


    return render(request, 'notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect(notification.url or 'notifications')


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = User.objects.filter(Q(username__icontains=query)).exclude(id=request.user.id)
    return render(request, 'search_results.html', {'query': query, 'results': results})



@login_required
def ajax_search_users(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id).distinct()[:10]

        for user in users:
            # Check if they are friends
            is_friend = FriendRequest.objects.filter(
                (
                    Q(sender=request.user, receiver=user) |
                    Q(sender=user, receiver=request.user)
                ),
                status='accepted'
            ).exists()

            # Check if a friend request was sent (but not accepted)
            request_sent = FriendRequest.objects.filter(
                sender=request.user,
                receiver=user,
                status='pending'
            ).exists()

            try:
                profile_pic = user.profile.profile_pic.url
            except:
                profile_pic = '/media/default.jpg'

            results.append({
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}",
                'profile_pic': profile_pic,
                'is_friend': is_friend,
                'request_sent': request_sent,
            })

    return JsonResponse(results, safe=False)



def base(request):
    pending_count = 0
    if request.user.is_authenticated:
        pending_count = request.user.received_requests.filter(status='pending').count()
    return render(request, 'login.html', {'pending_count': pending_count})


@login_required
def message_user(request, user_id):
    recipient = get_object_or_404(User, id=user_id)

    # Only allow messaging if users are friends
    if recipient not in get_friends(request.user):
        return HttpResponseForbidden("You can only message friends.")

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(sender=request.user, recipient=recipient, content=content)

            # Create notification
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                verb="sent you a message",
                url=reverse('message_user', args=[recipient.id]),
                type='message'
            )

            return redirect('message_user', user_id=recipient.id)
    Message.objects.filter(sender=recipient, recipient=request.user, is_read=False).update(is_read=True)

    Notification.objects.filter(
        sender=recipient,
        recipient=request.user,
        type='message',
        is_read=False
    ).update(is_read=True)

    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by('timestamp')

    return render(request, 'messaging/chat.html', {
        'recipient': recipient,
        'messages': messages
    })


@login_required
def friends_list_for_messaging(request):
    user = request.user
    friends = get_friends(user)

    inbox_data = []
    for friend in friends:
        last_message = Message.objects.filter(
            Q(sender=user, recipient=friend) | Q(sender=friend, recipient=user)
        ).order_by('-timestamp').first()

        unread_count = Message.objects.filter(
            sender=friend,
            recipient=user,
            is_read=False
        ).count()

        inbox_data.append({
            'friend': friend,
            'last_message': last_message,
            'unread_count': unread_count
        })

    return render(request, 'friends_list.html', {
        'inbox_data': inbox_data,
        'friends': friends
    })



@login_required
def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'profile.html', {'user': user})


@login_required
def user_profile_view(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user_profile)

    is_own_profile = request.user == user_profile
    is_friend = user_profile in get_friends(request.user)
    friend_request_sent = FriendRequest.objects.filter(
        sender=request.user,
        receiver=user_profile,
        status='pending'
    ).exists()

    posts = Post.objects.filter(user=user_profile).order_by('-created_at') if is_own_profile or is_friend else []

    context = {
        'user_profile': user_profile,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'is_friend': is_friend,
        'friend_request_sent': friend_request_sent,
        'posts': posts,
        'friends_count': get_friends(user_profile).count(),
    }

    return render(request, 'profile.html', context)


