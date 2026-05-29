// static/sw.js

self.addEventListener('push', event => {

    let data = {};

    try {
        data = event.data.json();
    } catch {
        data = {};
    }

    const options = {
        body: data.body || '',
        icon: data.icon || '/static/img/icon-192.png',
        badge: data.badge || '/static/img/badge-72.png',

        vibrate: [200, 100, 200],

        data: {
            url: data.url || '/'
        },

        requireInteraction: false,
        renotify: true,
        tag: data.tag || 'default'
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || 'Nova notificação',
            options
        )
    );
});


self.addEventListener('notificationclick', event => {

    event.notification.close();

    const url = event.notification.data.url;

    event.waitUntil(

        clients.matchAll({
            type: 'window',
            includeUncontrolled: true
        }).then(clientList => {

            for (const client of clientList) {

                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});