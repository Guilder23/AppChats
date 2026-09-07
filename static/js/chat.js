(() => {
  const app = document.querySelector('.chat-app');
  const area = document.querySelector('#message-area');
  const form = document.querySelector('#message-form');
  const input = document.querySelector('#message-input');
  if (app && location.pathname.includes('/conversacion/')) app.classList.add('chat-open');
  const csrf = () => document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  const scroll = () => { if (area) area.scrollTop = area.scrollHeight; };
  const addMessage = (data) => {
    if (!area) return;
    const mine = data.sender_id === Number(area.dataset.userId);
    const row = document.createElement('div');
    row.className = `message-row ${mine ? 'mine' : ''}`;
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (data.attachment) {
      const link = document.createElement('a');
      link.className = 'attachment-link';
      link.href = data.attachment;
      link.target = '_blank';
      link.innerHTML = '<i class="bi bi-file-earmark"></i> ';
      link.append(document.createTextNode(data.body));
      bubble.append(link);
    } else {
      bubble.append(document.createTextNode(data.body));
    }
    const time = document.createElement('time');
    time.innerHTML = `${data.time || ''} ${mine ? '<i class="bi bi-check2-all"></i>' : ''}`;
    bubble.append(time);
    row.append(bubble);
    area.append(row);
    scroll();
  };
  if (area) {
    const id = area.dataset.conversationId;
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${location.host}/ws/chat/${id}/`);
    socket.onopen = () => {
      const presence = document.querySelector('#presence');
      if (presence) presence.innerHTML = '<span class="online-dot"></span> En línea';
    };
    socket.onmessage = event => {
      const data = JSON.parse(event.data);
      if (data.type === 'read') {
        area.querySelectorAll('.message-row.mine .message-status').forEach(status => { status.textContent = '✓✓'; status.classList.add('read'); });
        return;
      }
      addMessage(data);
      if (data.sender_id !== Number(area.dataset.userId) && document.visibilityState !== 'visible' && 'Notification' in window && Notification.permission === 'granted') new Notification(data.sender, { body: data.body });
    };
    socket.onclose = () => {
      const presence = document.querySelector('#presence');
      if (presence) {
        const lastSeen = presence.dataset.lastSeen;
        presence.textContent = lastSeen ? `Última vez ${new Date(lastSeen).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}` : 'Última vez recientemente';
      }
    };
    form?.addEventListener('submit', event => {
      event.preventDefault();
      const body = input.value.trim();
      if (body && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ body }));
        input.value = '';
        input.focus();
      }
    });
    scroll();
  }
  document.querySelector('#back-to-list')?.addEventListener('click', () => {
    if (app) app.classList.remove('chat-open');
    history.pushState({}, '', '/chat/');
  });
  document.querySelector('#search-chats')?.addEventListener('input', event => {
    const query = event.target.value.toLowerCase();
    document.querySelectorAll('.conversation-item').forEach(item => { item.hidden = !item.dataset.name.includes(query); });
  });
  document.querySelector('#search-messages')?.addEventListener('click', () => {
    const query = window.prompt('Buscar en esta conversación');
    if (!query || !area) return;
    area.querySelectorAll('.message-bubble').forEach(message => { message.classList.toggle('message-highlight', message.textContent.toLowerCase().includes(query.toLowerCase())); });
  });
  document.querySelector('#chat-menu')?.addEventListener('click', () => window.alert('Menú del chat: puedes buscar mensajes, revisar archivos o volver a la lista.'));
  document.querySelector('#attach-file')?.addEventListener('click', () => document.querySelector('#attachment-input')?.click());
  document.querySelector('#attachment-input')?.addEventListener('change', event => { const file = event.target.files[0]; if (file && input) input.value = `📎 ${file.name}`; });
    document.querySelector('#attachment-input')?.addEventListener('change', async event => {
      const file = event.target.files[0];
      if (!file || !area) return;
      const data = new FormData();
      data.append('attachment', file);
      const response = await fetch(`/chat/api/conversacion/${area.dataset.conversationId}/archivo/`, { method: 'POST', headers: { 'X-CSRFToken': csrf() }, body: data });
      if (!response.ok) window.alert('No se pudo enviar el archivo.');
      event.target.value = '';
    });
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
  const modal = document.querySelector('#new-chat-modal');
  document.querySelector('#new-chat')?.addEventListener('click', () => { modal.hidden = false; loadUsers(); });
  document.querySelector('#close-modal')?.addEventListener('click', () => { modal.hidden = true; });
  async function loadUsers() {
    const results = document.querySelector('#user-results');
    results.innerHTML = '<p class="muted">Cargando usuarios...</p>';
    const data = await fetch('/chat/usuarios/').then(response => response.json());
    results.innerHTML = data.users.map(user => `<div class="user-result" data-id="${user.id}"><span class="avatar">${user.username[0].toUpperCase()}</span><strong>${user.username}</strong><small>Abrir chat</small></div>`).join('') || '<p class="muted">No hay otros usuarios todavía.</p>';
    results.querySelectorAll('.user-result').forEach(item => item.addEventListener('click', async () => {
      const body = new URLSearchParams({ user_id: item.dataset.id });
      const response = await fetch('/chat/api/conversacion/', { method: 'POST', headers: { 'X-CSRFToken': csrf(), 'Content-Type': 'application/x-www-form-urlencoded' }, body });
      const result = await response.json();
      location.href = result.url;
    }));
  }
  document.querySelector('#user-search')?.addEventListener('input', event => {
    const query = event.target.value.toLowerCase();
    document.querySelectorAll('.user-result').forEach(item => { item.hidden = !item.textContent.toLowerCase().includes(query); });
  });
})();
