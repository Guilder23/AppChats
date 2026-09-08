document.documentElement.classList.add('js-ready');

if ('serviceWorker' in navigator) {
	window.addEventListener('load', () => navigator.serviceWorker.register('/sw.js'));
}

let deferredInstallPrompt;
window.addEventListener('beforeinstallprompt', event => {
	event.preventDefault();
	deferredInstallPrompt = event;
	document.querySelectorAll('[data-install-app]').forEach(button => { button.hidden = false; });
});

document.addEventListener('click', async event => {
	const button = event.target.closest('[data-install-app]');
	if (!button || !deferredInstallPrompt) return;
	deferredInstallPrompt.prompt();
	await deferredInstallPrompt.userChoice;
	deferredInstallPrompt = null;
	button.hidden = true;
});

window.addEventListener('appinstalled', () => {
	document.querySelectorAll('[data-install-app]').forEach(button => { button.hidden = true; });
});
