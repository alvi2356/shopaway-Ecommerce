// Mobile Enhancements for ShopAway
(function() {
    'use strict';

    // Mobile Navigation Enhancements
    function initMobileNavigation() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        const body = document.body;

        if (navbarToggler && navbarCollapse) {
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(event) {
                const isClickInsideNav = navbarCollapse.contains(event.target);
                const isClickOnToggler = navbarToggler.contains(event.target);
                
                if (!isClickInsideNav && !isClickOnToggler && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });

            // Close mobile menu on escape key
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape' && navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });

            // Prevent body scroll when mobile menu is open
            navbarCollapse.addEventListener('show.bs.collapse', function() {
                body.style.overflow = 'hidden';
            });

            navbarCollapse.addEventListener('hide.bs.collapse', function() {
                body.style.overflow = '';
            });
        }
    }

    // Mobile Touch Enhancements
    function initMobileTouch() {
        // Add touch feedback to buttons
        const buttons = document.querySelectorAll('.btn, .nav-link, .card');
        buttons.forEach(button => {
            button.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.98)';
            });
            
            button.addEventListener('touchend', function() {
                this.style.transform = '';
            });
        });

        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            if (input.style.fontSize !== '16px') {
                input.style.fontSize = '16px';
            }
        });
    }

    // Mobile Search Enhancements
    function initMobileSearch() {
        const searchInputs = document.querySelectorAll('input[name="q"]');
        searchInputs.forEach(input => {
            // Add search suggestions (placeholder for future implementation)
            input.addEventListener('focus', function() {
                this.style.transform = 'scale(1.02)';
            });
            
            input.addEventListener('blur', function() {
                this.style.transform = '';
            });
        });
    }

    // Mobile Product Card Enhancements
    function initMobileProductCards() {
        const productCards = document.querySelectorAll('.product-card');
        productCards.forEach(card => {
            // Add swipe gesture support (placeholder)
            let startX = 0;
            let startY = 0;
            
            card.addEventListener('touchstart', function(e) {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            });
            
            card.addEventListener('touchmove', function(e) {
                if (!startX || !startY) return;
                
                const diffX = startX - e.touches[0].clientX;
                const diffY = startY - e.touches[0].clientY;
                
                // Horizontal swipe detection
                if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                    e.preventDefault();
                }
            });
        });
    }

    // Mobile Form Enhancements
    function initMobileForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // Add loading state to submit buttons
            form.addEventListener('submit', function() {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Loading...';
                }
            });
        });

        // Auto-resize textareas
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });
    }

    // Mobile Scroll Enhancements
    function initMobileScroll() {
        let lastScrollTop = 0;
        const navbar = document.querySelector('.navbar');
        
        if (navbar) {
            window.addEventListener('scroll', function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    navbar.style.transform = 'translateY(0)';
                }
                
                lastScrollTop = scrollTop;
            });
        }

        // Smooth scroll for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Mobile Performance Optimizations
    function initMobilePerformance() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));

        // Debounce scroll events
        let scrollTimeout;
        window.addEventListener('scroll', function() {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(function() {
                // Scroll event handling
            }, 100);
        });
    }

    // Mobile Accessibility Enhancements
    function initMobileAccessibility() {
        // Add focus indicators for keyboard navigation
        const focusableElements = document.querySelectorAll('a, button, input, select, textarea, [tabindex]');
        focusableElements.forEach(element => {
            element.addEventListener('focus', function() {
                this.style.outline = '2px solid var(--mint-dark)';
                this.style.outlineOffset = '2px';
            });
            
            element.addEventListener('blur', function() {
                this.style.outline = '';
                this.style.outlineOffset = '';
            });
        });

        // Announce page changes for screen readers
        const pageTitle = document.querySelector('title');
        if (pageTitle) {
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.setAttribute('aria-atomic', 'true');
            announcement.style.position = 'absolute';
            announcement.style.left = '-10000px';
            announcement.style.width = '1px';
            announcement.style.height = '1px';
            announcement.style.overflow = 'hidden';
            document.body.appendChild(announcement);
        }
    }

    // Mobile Viewport Fixes
    function initMobileViewport() {
        // Fix viewport height on mobile browsers
        function setViewportHeight() {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }

        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        window.addEventListener('orientationchange', setViewportHeight);

        // Prevent pull-to-refresh on mobile
        document.addEventListener('touchstart', function(e) {
            if (e.touches.length !== 1) return;
            const startY = e.touches[0].clientY;
            if (startY <= 0) e.preventDefault();
        }, { passive: false });
    }

    // Mobile Network Status
    function initMobileNetworkStatus() {
        function updateNetworkStatus() {
            const isOnline = navigator.onLine;
            const statusElement = document.querySelector('.network-status');
            
            if (statusElement) {
                statusElement.textContent = isOnline ? 'Online' : 'Offline';
                statusElement.className = `network-status badge ${isOnline ? 'bg-success' : 'bg-danger'}`;
            }
        }

        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
        updateNetworkStatus();
    }

    // Initialize all mobile enhancements
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Initialize all mobile features
        initMobileNavigation();
        initMobileTouch();
        initMobileSearch();
        initMobileProductCards();
        initMobileForms();
        initMobileScroll();
        initMobilePerformance();
        initMobileAccessibility();
        initMobileViewport();
        initMobileNetworkStatus();

        console.log('Mobile enhancements initialized');
    }

    // Start initialization
    init();

})();
