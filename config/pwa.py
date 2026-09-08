from django.http import HttpResponse


def service_worker(request):
    script = """
const CACHE_NAME = 'chatapp-v1';
const APP_SHELL = ['/static/css/base.css', '/static/js/base.js', '/static/manifest.webmanifest'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
  )));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  if (event.request.url.includes('/ws/')) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
"""
    response = HttpResponse(script, content_type='application/javascript')
    response['Cache-Control'] = 'no-cache'
    return response