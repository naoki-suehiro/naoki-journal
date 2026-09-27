(() => {
  'use strict';

  const article = document.querySelector('[data-bilingual-article]');
  if (!article) return;

  const controls = article.querySelector('.language-switch');
  const buttons = [...controls.querySelectorAll('button[data-language]')];
  const panels = buttons.map(button => document.getElementById(button.getAttribute('aria-controls')));
  if (panels.some(panel => !panel)) return;

  buttons.forEach((button, selectedIndex) => {
    button.addEventListener('click', () => {
      buttons.forEach((item, index) => {
        const selected = index === selectedIndex;
        item.setAttribute('aria-pressed', String(selected));
        panels[index].hidden = !selected;
      });
    });
  });

  // The server-rendered Japanese copy stays readable if this script cannot run.
  controls.hidden = false;
})();
