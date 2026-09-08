from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from apps.accounts.models import Profile
from .models import Conversation, Message


def touch_profile(user):
	profile, _ = Profile.objects.get_or_create(user=user)
	profile.last_seen = timezone.now()
	profile.save(update_fields=['last_seen'])
    


def conversation_rows(user):
	rows = []
	conversations = user.conversations.annotate(
		unread_count=Count('messages', filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=user))
	).prefetch_related('participants', 'messages')
	for item in conversations:
		other = item.participants.exclude(id=user.id).first()
		if other:
			Profile.objects.get_or_create(user=other)
		rows.append({'item': item, 'other': other, 'unread_count': item.unread_count})
	return rows


@login_required
def home(request):
	touch_profile(request.user)
	rows = conversation_rows(request.user)
	return render(request, 'chat/home.html', {'conversation_rows': rows, 'unread_total': sum(row['unread_count'] for row in rows), 'selected': rows[0]['item'] if rows else None, 'selected_other': rows[0]['other'] if rows else None})


@login_required
def conversation(request, conversation_id):
	item = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
	item.messages.filter(read_at__isnull=True).exclude(sender=request.user).update(read_at=timezone.now())
	touch_profile(request.user)
	rows = conversation_rows(request.user)
	return render(request, 'chat/home.html', {
		'conversation_rows': rows,
		'unread_total': sum(row['unread_count'] for row in rows),
		'selected': item,
		'selected_other': item.participants.exclude(id=request.user.id).first(),
	})


@login_required
def users(request):
	return JsonResponse({'users': list(User.objects.exclude(id=request.user.id).values('id', 'username'))})


@login_required
@require_POST
def create_conversation(request):
	user_id = request.POST.get('user_id')
	other = get_object_or_404(User, id=user_id)
	existing = Conversation.objects.filter(participants=request.user).filter(participants=other).distinct().first()
	item = existing or Conversation.objects.create()
	if not existing:
		item.participants.set([request.user, other])
	return JsonResponse({'id': item.id, 'url': f'/chat/conversacion/{item.id}/'})


@login_required
def messages(request, conversation_id):
	item = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
	data = [{'id': message.id, 'body': message.body, 'sender': message.sender.username,
			 'mine': message.sender_id == request.user.id,
				 'time': message.created_at.strftime('%H:%M'), 'read': bool(message.read_at),
				 'attachment': message.attachment.url if message.attachment else None} for message in item.messages.select_related('sender')]
	return JsonResponse({'messages': data})


@login_required
@require_POST
def upload_attachment(request, conversation_id):
	item = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
	attachment = request.FILES.get('attachment')
	if not attachment or attachment.size > 10 * 1024 * 1024:
		return JsonResponse({'error': 'El archivo es obligatorio y debe pesar menos de 10 MB.'}, status=400)
	message = Message.objects.create(conversation=item, sender=request.user, body=attachment.name, attachment=attachment)
	Conversation.objects.filter(id=item.id).update(updated_at=message.created_at)
	payload = {'id': message.id, 'body': attachment.name, 'sender': request.user.username, 'sender_id': request.user.id, 'conversation_id': item.id,
			   'time': message.created_at.strftime('%H:%M'), 'read': False, 'attachment': message.attachment.url}
	async_to_sync(get_channel_layer().group_send)(f'chat_{conversation_id}', {'type': 'chat_message', 'message': payload})
	for user_id in item.participants.exclude(id=request.user.id).values_list('id', flat=True):
		async_to_sync(get_channel_layer().group_send)(f'user_{user_id}', {'type': 'notification', 'message': payload})
	return JsonResponse(payload)
