document.addEventListener('DOMContentLoaded', () => {
    const navbar = document.querySelector('.navbar');
    const menuToggle = document.querySelector('[data-menu-toggle]');
    const navMenu = document.querySelector('[data-nav-menu]');
    const navLinks = navMenu ? navMenu.querySelectorAll('a') : [];
    const messages = document.querySelector('.messages');
    const sortSelect = document.getElementById('sort');
    const contactForm = document.querySelector('.contact-form form');
    const animatedItems = document.querySelectorAll('.route-card, .feature-card');

    const closeMenu = () => {
        if (!menuToggle || !navMenu) {
            return;
        }
        navMenu.classList.remove('is-open');
        menuToggle.setAttribute('aria-expanded', 'false');
    };

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            const isOpen = navMenu.classList.toggle('is-open');
            menuToggle.setAttribute('aria-expanded', String(isOpen));
        });

        navLinks.forEach((link) => {
            link.addEventListener('click', closeMenu);
        });

        document.addEventListener('click', (event) => {
            const clickedInsideNavbar = event.target.closest('.navbar');
            if (!clickedInsideNavbar) {
                closeMenu();
            }
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                closeMenu();
            }
        });
    }

    if (navbar) {
        const updateNavbarState = () => {
            navbar.classList.toggle('is-scrolled', window.scrollY > 20);
        };

        updateNavbarState();
        window.addEventListener('scroll', updateNavbarState);
    }

    if (messages) {
        setTimeout(() => {
            messages.classList.add('is-hidden');
            setTimeout(() => messages.remove(), 500);
        }, 5000);
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            const url = new URL(window.location.href);

            if (sortSelect.value) {
                url.searchParams.set('sort', sortSelect.value);
            } else {
                url.searchParams.delete('sort');
            }

            window.location.href = url.toString();
        });
    }

    if (contactForm) {
        contactForm.addEventListener('submit', (event) => {
            event.preventDefault();
            alert("Дякуємо за ваше повідомлення! Ми зв'яжемося з вами найближчим часом.");
            event.target.reset();
        });
    }

    if (animatedItems.length) {
        const observer = new IntersectionObserver((entries, cardsObserver) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    cardsObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: '0px 0px -80px 0px'
        });

        animatedItems.forEach((item) => {
            item.classList.add('animate-on-scroll');
            observer.observe(item);
        });
    }
});

function toggleFavorite(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        }
    })
        .then((response) => response.json())
        .then((data) => {
            const btn = document.querySelector('.action-btn.favorite');
            if (!btn) {
                return;
            }

            btn.classList.toggle('active', data.is_favorite);
            btn.innerHTML = data.is_favorite
                ? '<i class="fa-solid fa-heart-crack"></i> Видалити з улюблених'
                : '<i class="fa-solid fa-heart"></i> Додати в улюблені';
        });
}

function toggleCompleted(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
        }
    })
        .then((response) => response.json())
        .then((data) => {
            const btn = document.querySelector('.action-btn.completed');
            if (!btn) {
                return;
            }

            btn.classList.toggle('active', data.is_completed);
            btn.innerHTML = data.is_completed
                ? '<i class="fa-solid fa-xmark"></i> Позначити як не пройдено'
                : '<i class="fa-solid fa-check"></i> Позначити як пройдено';
        });
}
