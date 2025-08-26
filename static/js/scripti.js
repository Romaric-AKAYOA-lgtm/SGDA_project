
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('main-wrapper');
    sidebar.classList.toggle('show');
    mainWrapper.classList.toggle('sidebar-visible');
  }

  document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');

    links.forEach(link => {
      const linkPath = new URL(link.href).pathname;
      if (currentPath === linkPath || currentPath.startsWith(linkPath)) {
        link.classList.add('active');
      }
    });
  });

  
  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainWrapper = document.getElementById('main-wrapper');
    sidebar.classList.toggle('show');
    mainWrapper.classList.toggle('sidebar-visible');
  }

  document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.nav-link');

    links.forEach(link => {
      const linkPath = new URL(link.href).pathname;
      if (currentPath === linkPath || currentPath.startsWith(linkPath)) {
        link.classList.add('active');
      }
    });
  });

  
document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.visiteur-checkbox');
    const generateBtn = document.getElementById('generate-word');
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const resetSearchButton = document.getElementById('reset-search');

    // Fonction pour activer/désactiver le bouton
    function updateButtonState() {
        const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
        generateBtn.disabled = !anyChecked;
    }

    updateButtonState();

    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateButtonState);
    });

    // Soumission personnalisée du formulaire de recherche
    searchForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const query = encodeURIComponent(searchInput.value);
        window.location.href = searchForm.action + "?q=" + query;
    });

    resetSearchButton.addEventListener('click', function () {
        searchInput.value = '';
        searchForm.submit();
    });
});

window.addEventListener('scroll', () => {
  if (window.scrollY > 50) { // seuil pour faire disparaître le header
    document.body.classList.add('scrolled');
  } else {
    document.body.classList.remove('scrolled');
  }
});
