(() => {
  const trigger = document.querySelector('[data-interview-open]');
  const dialog = document.querySelector('.interview-dialog');
  if (!trigger || !dialog || typeof dialog.showModal !== 'function') return;
  const video = dialog.querySelector('video');
  trigger.addEventListener('click', (event) => {
    event.preventDefault();
    dialog.showModal();
    document.documentElement.classList.add('interview-is-open');
    video.play().catch(() => {});
  });
  dialog.querySelector('[data-interview-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('close', () => {
    video.pause();
    video.currentTime = 0;
    document.documentElement.classList.remove('interview-is-open');
    trigger.focus();
  });
})();
