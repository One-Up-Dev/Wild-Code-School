// =========================================================
// SEARCH — Filtre temps réel sur les cards du module actif
// =========================================================
(function () {
  const input = document.getElementById('search-input');
  const empty = document.getElementById('empty-search');
  if (!input) return;

  function activeModule() {
    return Array.from(document.querySelectorAll('.module')).find((m) => !m.hidden);
  }

  function filter() {
    const term = input.value.trim().toLowerCase();
    const module = activeModule();
    if (!module) return;

    const cards = module.querySelectorAll('.card');
    let visible = 0;

    cards.forEach((card) => {
      if (!term) {
        card.style.display = '';
        visible++;
        return;
      }
      const match = card.textContent.toLowerCase().includes(term);
      card.style.display = match ? '' : 'none';
      if (match) visible++;
    });

    if (empty) empty.hidden = !(term && visible === 0);
  }

  input.addEventListener('input', filter);
  document.addEventListener('module:changed', () => {
    input.value = '';
    if (empty) empty.hidden = true;
    filter();
  });
})();
