// =========================================================
// ROUTER — Hash-based navigation between modules
// =========================================================
(function () {
  const DEFAULT_MODULE = 'accueil';

  function getModuleFromHash() {
    const hash = window.location.hash.replace(/^#/, '');
    return hash || DEFAULT_MODULE;
  }

  function showModule(moduleId) {
    document.querySelectorAll('.module').forEach((section) => {
      section.hidden = true;
    });

    const target = document.getElementById('module-' + moduleId);
    if (target) {
      target.hidden = false;
    } else {
      const fallback = document.getElementById('module-' + DEFAULT_MODULE);
      if (fallback) fallback.hidden = false;
    }

    document.querySelectorAll('.nav-link').forEach((link) => {
      link.classList.toggle('active', link.dataset.module === moduleId);
    });

    document.dispatchEvent(new CustomEvent('module:changed', { detail: { moduleId } }));

    window.scrollTo({ top: 0, behavior: 'instant' });
  }

  window.addEventListener('hashchange', () => showModule(getModuleFromHash()));
  document.addEventListener('DOMContentLoaded', () => showModule(getModuleFromHash()));
})();
