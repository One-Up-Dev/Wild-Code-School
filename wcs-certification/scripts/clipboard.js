// =========================================================
// CLIPBOARD — Copier le code d'un bloc au clic
// =========================================================
(function () {
  const COPY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
  const COPIED_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';

  function highlightAll() {
    if (window.hljs) {
      document.querySelectorAll('.code-block pre code:not(.hljs)').forEach((block) => {
        window.hljs.highlightElement(block);
      });
    }
  }

  function setupCopyButtons() {
    document.querySelectorAll('.code-block').forEach((block) => {
      const btn = block.querySelector('.code-copy');
      if (!btn || btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';

      if (!btn.innerHTML.trim()) {
        btn.innerHTML = COPY_ICON + '<span>Copier</span>';
      }

      btn.addEventListener('click', async () => {
        const code = block.querySelector('pre code');
        if (!code) return;
        try {
          await navigator.clipboard.writeText(code.innerText);
          btn.classList.add('copied');
          btn.innerHTML = COPIED_ICON + '<span>Copié !</span>';
          setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = COPY_ICON + '<span>Copier</span>';
          }, 2000);
        } catch (err) {
          console.error('Copy failed', err);
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    highlightAll();
    setupCopyButtons();
  });

  document.addEventListener('module:changed', () => {
    highlightAll();
    setupCopyButtons();
  });
})();
