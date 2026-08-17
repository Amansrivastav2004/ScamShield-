/* ScamShield Global UI & Interaction Manager */

// Toast Notifications System
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'error') iconClass = 'fa-exclamation-triangle';
    if (type === 'warning') iconClass = 'fa-exclamation-circle';

    toast.innerHTML = `
        <i class="fas ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Modal Controllers
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Interactive Tab Switcher Helper
function initTabSwitcher(navSelector, panelSelector) {
    const navButtons = document.querySelectorAll(navSelector);
    const panels = document.querySelectorAll(panelSelector);

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            
            navButtons.forEach(b => b.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// Initialize Global Components on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Drawer Toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('show');
        });
    }

    // 2. Language Dropdown Toggle
    const langBtn = document.getElementById('langBtn');
    const langDropdown = document.getElementById('langDropdown');
    
    if (langBtn && langDropdown) {
        langBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            langDropdown.classList.toggle('show');
        });

        document.addEventListener('click', () => {
            langDropdown.classList.remove('show');
        });
    }

    // 3. Initialize Approach Section Tabs
    initTabSwitcher('.approach-tab-btn', '.approach-panel');

    // 4. Initialize Platform Spotlight Tabs
    initTabSwitcher('.spotlight-tab-btn', '.spotlight-panel');

    // 5. Close Modals on Overlay Click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    });
});
