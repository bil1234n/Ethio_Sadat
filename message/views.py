from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required # SECURES ADMIN VIEWS
from django.contrib import messages
from .models import Feedback
from .forms import FeedbackForm, AdminReplyForm


# ==========================================
# ADMIN DASHBOARD VIEWS
# ==========================================

@staff_member_required
def admin_feedback_list(request):
    # Fetch all feedbacks. Order by 'is_replied' so unread/unanswered ones show up at the very top.
    feedbacks = Feedback.objects.all().order_by('is_replied', '-created_at')
    return render(request, 'message/admin_feedback_list.html', {'feedbacks': feedbacks})

@staff_member_required
def admin_reply_feedback(request, pk):
    # Fetch the specific message
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        form = AdminReplyForm(request.POST, instance=feedback)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.is_replied = True # Mark as replied automatically
            reply.save()
            messages.success(request, f"Reply sent to {feedback.user.username} successfully!")
            return redirect('admin_feedback_list')
    else:
        form = AdminReplyForm(instance=feedback)

    return render(request, 'message/admin_reply.html', {'feedback': feedback, 'form': form})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Save but don't commit to DB yet
            feedback = form.save(commit=False)
            # Attach the currently logged-in user
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Your message has been sent to the admin successfully!")
            return redirect('my_feedback')
    else:
        form = FeedbackForm()

    return render(request, 'message/contact.html', {'form': form})

@login_required
def my_feedback(request):
    # Fetch only the feedbacks belonging to the logged-in user
    feedbacks = Feedback.objects.filter(user=request.user)
    return render(request, 'message/my_feedback.html', {'feedbacks': feedbacks})