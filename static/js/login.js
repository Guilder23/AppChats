(() => {
  document.querySelectorAll('[data-password-toggle]').forEach(button => {
    button.addEventListener('click', () => {
      const input = button.closest('.input-wrap')?.querySelector('input');
      const icon = button.querySelector('i');
      if (!input || !icon) return;
      const visible = input.type === 'text';
      input.type = visible ? 'password' : 'text';
      icon.className = visible ? 'bi bi-eye' : 'bi bi-eye-slash';
      button.setAttribute('aria-label', visible ? 'Mostrar contraseña' : 'Ocultar contraseña');
    });
  });
})();
