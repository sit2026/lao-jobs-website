/**
 * Lao Job Website - Main JavaScript
 */

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initMobileMenu();
    initToast();
    initModal();
    initJobCardSave();
    initFormValidation();
    initInfiniteScroll();
    initServiceWorker();
});

/**
 * Theme Toggle (Dark/Light Mode)
 */
function initTheme() {
    const themeToggle = document.querySelector('[data-theme-toggle]');
    const savedTheme = localStorage.getItem('theme') || 'light';

    document.documentElement.setAttribute('data-theme', savedTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

/**
 * Mobile Menu
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('[data-menu-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');

    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('open');
            document.body.classList.toggle('menu-open');
        });
    }
}

/**
 * Toast Notifications
 */
let toastContainer = null;

function initToast() {
    toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
}

function showToast(message, type = 'default', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
        <span class="toast-message">${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Modal
 */
function initModal() {
    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this);
            }
        });
    });

    // Close modal on close button click
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            closeModal(modal);
        });
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal-overlay.open');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modal) {
    if (typeof modal === 'string') {
        modal = document.getElementById(modal);
    }
    if (modal) {
        modal.classList.remove('open');
        document.body.style.overflow = '';
    }
}

/**
 * Job Card Save/Bookmark
 */
function initJobCardSave() {
    document.querySelectorAll('.job-card-save').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const jobId = this.dataset.jobId;
            const isSaved = this.classList.contains('saved');

            if (isSaved) {
                this.classList.remove('saved');
                showToast('ຍົກເລີກບັນທຶກແລ້ວ', 'default');
            } else {
                this.classList.add('saved');
                showToast('ບັນທຶກວຽກແລ້ວ', 'success');
            }

            // Send to server
            toggleSaveJob(jobId, !isSaved);
        });
    });
}

async function toggleSaveJob(jobId, save) {
    try {
        const response = await fetch(`/api/jobs/${jobId}/save/`, {
            method: save ? 'POST' : 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
        });

        if (!response.ok) {
            throw new Error('Failed to save job');
        }
    } catch (error) {
        console.error('Error saving job:', error);
    }
}

/**
 * Form Validation
 */
function initFormValidation() {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;

    // Clear previous errors
    form.querySelectorAll('.form-error').forEach(el => el.remove());
    form.querySelectorAll('.form-input-error').forEach(el => {
        el.classList.remove('form-input-error');
    });

    // Validate required fields
    form.querySelectorAll('[required]').forEach(input => {
        if (!input.value.trim()) {
            showFieldError(input, 'ກະລຸນາປ້ອນຂໍ້ມູນ');
            isValid = false;
        }
    });

    // Validate email fields
    form.querySelectorAll('[type="email"]').forEach(input => {
        if (input.value && !isValidEmail(input.value)) {
            showFieldError(input, 'ອີເມວບໍ່ຖືກຕ້ອງ');
            isValid = false;
        }
    });

    // Validate phone fields
    form.querySelectorAll('[data-validate-phone]').forEach(input => {
        if (input.value && !isValidPhone(input.value)) {
            showFieldError(input, 'ເບີໂທບໍ່ຖືກຕ້ອງ');
            isValid = false;
        }
    });

    return isValid;
}

function showFieldError(input, message) {
    input.classList.add('form-input-error');

    const error = document.createElement('div');
    error.className = 'form-error';
    error.textContent = message;

    input.parentNode.appendChild(error);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    // Lao phone number format: 020 XXXX XXXX
    return /^(\+856|0)?20\s?\d{4}\s?\d{4}$/.test(phone.replace(/\s/g, ''));
}

/**
 * Infinite Scroll for Job List
 */
function initInfiniteScroll() {
    const jobList = document.querySelector('[data-infinite-scroll]');
    if (!jobList) return;

    let loading = false;
    let page = 1;
    const sentinel = document.querySelector('[data-scroll-sentinel]');

    if (!sentinel) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !loading) {
                loadMoreJobs();
            }
        });
    }, { rootMargin: '100px' });

    observer.observe(sentinel);

    async function loadMoreJobs() {
        loading = true;
        page++;

        // Show loading spinner
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        spinner.innerHTML = '<div class="spinner"></div>';
        jobList.appendChild(spinner);

        try {
            const response = await fetch(`/api/jobs/?page=${page}`);
            const data = await response.json();

            spinner.remove();

            if (data.results && data.results.length > 0) {
                data.results.forEach(job => {
                    jobList.insertAdjacentHTML('beforeend', renderJobCard(job));
                });

                // Re-init save buttons
                initJobCardSave();
            }

            if (!data.next) {
                observer.disconnect();
                sentinel.remove();
            }
        } catch (error) {
            console.error('Error loading more jobs:', error);
            spinner.remove();
        }

        loading = false;
    }
}

function renderJobCard(job) {
    return `
        <article class="job-card" onclick="location.href='/jobs/${job.id}/'">
            <div class="job-card-header">
                <div class="job-card-logo">
                    ${job.company.logo ? `<img src="${job.company.logo}" alt="${job.company.name}">` : job.company.name.charAt(0)}
                </div>
                <div class="job-card-info">
                    <h3 class="job-card-title">${job.title}</h3>
                    <p class="job-card-company">${job.company.name}</p>
                </div>
                <button class="job-card-save" data-job-id="${job.id}">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                    </svg>
                </button>
            </div>
            <div class="job-card-tags">
                <span class="tag tag-location">${job.province.name}</span>
                ${job.salary_display ? `<span class="tag tag-salary">${job.salary_display}</span>` : ''}
                <span class="tag tag-type">${job.job_type_display}</span>
            </div>
            <div class="job-card-footer">
                <span>${job.time_ago}</span>
                <span>${job.expires_in}</span>
            </div>
        </article>
    `;
}

/**
 * Service Worker Registration
 */
function initServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered:', registration.scope);
            })
            .catch(error => {
                console.error('SW registration failed:', error);
            });
    }
}

/**
 * Utility Functions
 */
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('lo-LA', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount) + ' ກີບ';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('lo-LA', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    }).format(date);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for use in other scripts
window.LaoJobs = {
    showToast,
    openModal,
    closeModal,
    formatCurrency,
    formatDate,
    debounce,
};
