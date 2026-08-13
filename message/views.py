# message/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse            
from accounts.models import Notification   

from .models import Feedback
from .forms import FeedbackForm, AdminReplyForm

# ==========================================
# ADMIN DASHBOARD VIEWS
# ==========================================

@staff_member_required
def admin_feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('is_replied', '-created_at')
    return render(request, 'message/admin_feedback_list.html', {'feedbacks': feedbacks})

@staff_member_required
def admin_reply_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        form = AdminReplyForm(request.POST, instance=feedback)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.is_replied = True
            reply.save()

            # --- NOTIFY THE USER THAT ADMIN REPLIED ---
            Notification.objects.create(
                recipient=feedback.user,
                title="Admin Replied",
                message=f"An admin replied to your message: '{feedback.subject}'.",
                notification_type='Message',
                link=reverse('my_feedback') 
            )

            messages.success(request, f"Reply sent to {feedback.user.username} successfully!")
            return redirect('admin_feedback_list')
    else:
        form = AdminReplyForm(instance=feedback)

    return render(request, 'message/admin_reply.html', {'feedback': feedback, 'form': form})

# ==========================================
# USER VIEWS
# ==========================================

# REMOVED @login_required so anyone can see the page
def submit_feedback(request):
    if request.method == 'POST':
        # --- NEW: Check if user is logged in before processing ---
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to send a message.")
            return redirect(f"/accounts/login/?next={request.path}")

        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()

            # --- NOTIFY ALL ADMINS ABOUT THE NEW MESSAGE ---
            staff_users = User.objects.filter(is_staff=True)
            for admin in staff_users:
                Notification.objects.create(
                    recipient=admin,
                    title="New Feedback Received",
                    message=f"User {request.user.username} sent a new message: '{feedback.subject}'.",
                    notification_type='Message',
                    link=reverse('admin_feedback_list') 
                )

            messages.success(request, "Your message has been sent to the admin successfully!")
            return redirect('my_feedback')
    else:
        form = FeedbackForm()

    return render(request, 'message/contact.html', {'form': form})

@login_required
def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'message/my_feedback.html', {'feedbacks': feedbacks})