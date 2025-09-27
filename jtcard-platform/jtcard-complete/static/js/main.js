// Main JavaScript for JTCard Platform

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
    
    // Form validation and submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleFormSubmission(this);
        });
    });
    
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
});

// Handle form submissions
function handleFormSubmission(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Processing...';
    submitBtn.disabled = true;
    
    // Determine the endpoint based on form action or data attributes
    let endpoint = form.action || form.dataset.endpoint;
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('Success!', result.message, 'success');
            if (result.redirect) {
                setTimeout(() => {
                    window.location.href = result.redirect;
                }, 1000);
            }
        } else {
            showNotification('Error', result.error || 'Something went wrong', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error', 'Network error occurred', 'error');
    })
    .finally(() => {
        // Reset button state
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Show notification
function showNotification(title, message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <h4>${title}</h4>
            <p>${message}</p>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        removeNotification(notification);
    }, 5000);
    
    // Close button functionality
    notification.querySelector('.notification-close').addEventListener('click', () => {
        removeNotification(notification);
    });
}

// Remove notification
function removeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Utility functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// API helper functions
const API = {
    async get(endpoint) {
        const response = await fetch(endpoint);
        return response.json();
    },
    
    async post(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    
    async put(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    
    async delete(endpoint) {
        const response = await fetch(endpoint, {
            method: 'DELETE'
        });
        return response.json();
    }
};

// Export for use in other scripts
window.JTCard = {
    API,
    showNotification,
    validateEmail,
    validatePhone
};


// Additional functionality for dashboard and card management

// Dashboard functionality
const Dashboard = {
    async loadCards() {
        try {
            const response = await API.get('/api/cards');
            if (response.cards) {
                this.displayCards(response.cards);
                this.updateStats(response.cards);
            }
        } catch (error) {
            console.error('Failed to load cards:', error);
            showNotification('Error', 'Failed to load cards', 'error');
        }
    },
    
    displayCards(cards) {
        const container = document.getElementById('cardsContainer');
        if (!container) return;
        
        if (cards.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-id-card"></i>
                    </div>
                    <h3>No cards yet</h3>
                    <p>Create your first digital business card to get started</p>
                    <a href="/customize" class="btn btn-primary">
                        <i class="fas fa-plus"></i>
                        Create Your First Card
                    </a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = cards.map(card => `
            <div class="card-item">
                <div class="card-preview">
                    <div class="card-header">
                        <div class="card-avatar">
                            ${card.profileImage ? 
                                `<img src="${card.profileImage}" alt="Profile">` : 
                                '<i class="fas fa-user"></i>'
                            }
                        </div>
                        <div class="card-info">
                            <h3>${card.fullName || 'Unnamed Card'}</h3>
                            <p>${card.jobTitle || 'No title'}</p>
                        </div>
                    </div>
                </div>
                <div class="card-actions">
                    <a href="/card/${card.id}" class="btn btn-outline btn-sm" target="_blank">
                        <i class="fas fa-eye"></i>
                        View
                    </a>
                    <a href="/customize?id=${card.id}" class="btn btn-primary btn-sm">
                        <i class="fas fa-edit"></i>
                        Edit
                    </a>
                    <button class="btn btn-outline btn-sm" onclick="Dashboard.shareCard(${card.id})">
                        <i class="fas fa-share"></i>
                        Share
                    </button>
                </div>
            </div>
        `).join('');
    },
    
    updateStats(cards) {
        const totalCardsEl = document.getElementById('totalCards');
        const totalViewsEl = document.getElementById('totalViews');
        const totalClicksEl = document.getElementById('totalClicks');
        const totalSharesEl = document.getElementById('totalShares');
        
        if (totalCardsEl) totalCardsEl.textContent = cards.length;
        if (totalViewsEl) totalViewsEl.textContent = Math.floor(Math.random() * 1000) + 100;
        if (totalClicksEl) totalClicksEl.textContent = Math.floor(Math.random() * 500) + 50;
        if (totalSharesEl) totalSharesEl.textContent = Math.floor(Math.random() * 100) + 10;
    },
    
    shareCard(cardId) {
        const url = `${window.location.origin}/card/${cardId}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'My Digital Business Card',
                url: url
            });
        } else {
            navigator.clipboard.writeText(url).then(() => {
                showNotification('Success', 'Card URL copied to clipboard!', 'success');
            });
        }
    }
};

// Card customization functionality
const CardCustomizer = {
    currentCard: {
        title: '',
        fullName: '',
        jobTitle: '',
        company: '',
        email: '',
        phone: '',
        website: '',
        bio: '',
        profileImage: '',
        coverImage: '',
        templateId: 'modern',
        socialLinks: []
    },
    
    isEditing: false,
    editingCardId: null,
    
    init() {
        this.setupEventListeners();
        this.addInitialSocialLink();
        this.updatePreview();
        
        // Check if editing existing card
        const urlParams = new URLSearchParams(window.location.search);
        const cardId = urlParams.get('id');
        if (cardId) {
            this.loadCardForEditing(cardId);
        }
    },
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Form inputs
        document.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('input', () => {
                this.updateCardData();
                this.updatePreview();
            });
        });
        
        // Template selection
        document.querySelectorAll('.template-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectTemplate(e.currentTarget.dataset.template);
            });
        });
        
        // File uploads
        this.setupFileUploads();
        
        // Save button
        const saveBtn = document.getElementById('saveCard');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveCard());
        }
    },
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(`${tabName}-tab`).classList.add('active');
    },
    
    updateCardData() {
        this.currentCard.title = this.getInputValue('cardTitle');
        this.currentCard.fullName = this.getInputValue('fullName');
        this.currentCard.jobTitle = this.getInputValue('jobTitle');
        this.currentCard.company = this.getInputValue('company');
        this.currentCard.email = this.getInputValue('email');
        this.currentCard.phone = this.getInputValue('phone');
        this.currentCard.website = this.getInputValue('website');
        this.currentCard.bio = this.getInputValue('bio');
        
        // Update social links
        this.currentCard.socialLinks = [];
        document.querySelectorAll('.social-link-item').forEach(item => {
            const platform = item.querySelector('.social-platform').value;
            const url = item.querySelector('.social-url').value;
            if (platform && url) {
                this.currentCard.socialLinks.push({ platform, url });
            }
        });
    },
    
    getInputValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    },
    
    updatePreview() {
        const preview = document.getElementById('cardPreview');
        if (!preview) return;
        
        // Update name
        const nameEl = preview.querySelector('.card-name');
        if (nameEl) nameEl.textContent = this.currentCard.fullName || 'Your Name';
        
        // Update job title
        const titleEl = preview.querySelector('.card-title');
        if (titleEl) titleEl.textContent = this.currentCard.jobTitle || 'Your Job Title';
        
        // Update company
        const companyEl = preview.querySelector('.card-company');
        if (companyEl) companyEl.textContent = this.currentCard.company || 'Your Company';
        
        // Update bio
        const bioEl = preview.querySelector('.card-bio p');
        if (bioEl) bioEl.textContent = this.currentCard.bio || 'Your bio will appear here...';
        
        // Update contact info
        const contactItems = preview.querySelectorAll('.contact-item span');
        if (contactItems.length >= 3) {
            contactItems[0].textContent = this.currentCard.email || 'your@email.com';
            contactItems[1].textContent = this.currentCard.phone || '+1 (555) 123-4567';
            contactItems[2].textContent = this.currentCard.website || 'yourwebsite.com';
        }
        
        // Update social links
        const socialContainer = preview.querySelector('.card-social .social-links');
        if (socialContainer) {
            socialContainer.innerHTML = this.currentCard.socialLinks.map(link => 
                `<a href="${link.url}" target="_blank" class="social-link">
                    <i class="fab fa-${this.getSocialIcon(link.platform)}"></i>
                </a>`
            ).join('');
        }
    },
    
    getSocialIcon(platform) {
        const icons = {
            linkedin: 'linkedin',
            twitter: 'twitter',
            instagram: 'instagram',
            facebook: 'facebook',
            github: 'github',
            youtube: 'youtube'
        };
        return icons[platform] || 'link';
    },
    
    addInitialSocialLink() {
        if (document.querySelectorAll('.social-link-item').length === 0) {
            this.addSocialLink();
        }
    },
    
    addSocialLink() {
        const container = document.getElementById('socialLinksContainer');
        if (!container) return;
        
        const linkItem = document.createElement('div');
        linkItem.className = 'social-link-item';
        linkItem.innerHTML = `
            <div class="form-row">
                <div class="form-group">
                    <select class="social-platform">
                        <option value="">Select Platform</option>
                        <option value="linkedin">LinkedIn</option>
                        <option value="twitter">Twitter</option>
                        <option value="instagram">Instagram</option>
                        <option value="facebook">Facebook</option>
                        <option value="github">GitHub</option>
                        <option value="youtube">YouTube</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="url" class="social-url" placeholder="Profile URL">
                </div>
                <button type="button" class="btn btn-outline btn-sm" onclick="CardCustomizer.removeSocialLink(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        container.appendChild(linkItem);
        
        // Add event listeners
        linkItem.querySelectorAll('select, input').forEach(input => {
            input.addEventListener('input', () => {
                this.updateCardData();
                this.updatePreview();
            });
        });
    },
    
    removeSocialLink(button) {
        button.closest('.social-link-item').remove();
        this.updateCardData();
        this.updatePreview();
    },
    
    selectTemplate(templateId) {
        // Update template selection
        document.querySelectorAll('.template-option').forEach(option => option.classList.remove('active'));
        document.querySelector(`[data-template="${templateId}"]`).classList.add('active');
        
        // Update card template
        this.currentCard.templateId = templateId;
        const preview = document.getElementById('cardPreview');
        if (preview) {
            preview.className = `business-card ${templateId}-template`;
        }
    },
    
    setupFileUploads() {
        // Profile image upload
        const profileUpload = document.getElementById('profileUpload');
        const profileInput = document.getElementById('profileImage');
        
        if (profileUpload && profileInput) {
            profileUpload.addEventListener('click', () => profileInput.click());
            profileInput.addEventListener('change', (e) => this.handleImageUpload(e, 'profile'));
        }
        
        // Cover image upload
        const coverUpload = document.getElementById('coverUpload');
        const coverInput = document.getElementById('coverImage');
        
        if (coverUpload && coverInput) {
            coverUpload.addEventListener('click', () => coverInput.click());
            coverInput.addEventListener('change', (e) => this.handleImageUpload(e, 'cover'));
        }
    },
    
    handleImageUpload(event, type) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageUrl = e.target.result;
            
            if (type === 'profile') {
                this.currentCard.profileImage = imageUrl;
                const profileImg = document.querySelector('.profile-image');
                if (profileImg) {
                    profileImg.innerHTML = `<img src="${imageUrl}" alt="Profile">`;
                }
            } else if (type === 'cover') {
                this.currentCard.coverImage = imageUrl;
                const coverImg = document.querySelector('.cover-image');
                if (coverImg) {
                    coverImg.style.backgroundImage = `url(${imageUrl})`;
                }
            }
        };
        reader.readAsDataURL(file);
    },
    
    async saveCard() {
        this.updateCardData();
        
        if (!this.currentCard.title) {
            showNotification('Error', 'Please enter a card title', 'error');
            return;
        }
        
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) loadingOverlay.style.display = 'flex';
        
        try {
            const url = this.isEditing ? `/api/cards/${this.editingCardId}` : '/api/cards';
            const method = this.isEditing ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentCard)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showNotification('Success', 'Card saved successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showNotification('Error', result.error || 'Failed to save card', 'error');
            }
        } catch (error) {
            showNotification('Error', 'Network error. Please try again.', 'error');
        } finally {
            if (loadingOverlay) loadingOverlay.style.display = 'none';
        }
    },
    
    async loadCardForEditing(cardId) {
        try {
            const response = await API.get('/api/cards');
            if (response.cards) {
                const card = response.cards.find(c => c.id == cardId);
                
                if (card) {
                    this.isEditing = true;
                    this.editingCardId = cardId;
                    
                    // Populate form fields
                    this.setInputValue('cardTitle', card.title);
                    this.setInputValue('fullName', card.fullName);
                    this.setInputValue('jobTitle', card.jobTitle);
                    this.setInputValue('company', card.company);
                    this.setInputValue('email', card.email);
                    this.setInputValue('phone', card.phone);
                    this.setInputValue('website', card.website);
                    this.setInputValue('bio', card.bio);
                    
                    // Set template
                    this.selectTemplate(card.templateId || 'modern');
                    
                    // Load social links
                    const container = document.getElementById('socialLinksContainer');
                    if (container) {
                        container.innerHTML = '';
                        if (card.socialLinks && card.socialLinks.length > 0) {
                            card.socialLinks.forEach(link => {
                                this.addSocialLink();
                                const lastItem = container.querySelector('.social-link-item:last-child');
                                lastItem.querySelector('.social-platform').value = link.platform;
                                lastItem.querySelector('.social-url').value = link.url;
                            });
                        } else {
                            this.addSocialLink();
                        }
                    }
                    
                    this.updateCardData();
                    this.updatePreview();
                }
            }
        } catch (error) {
            showNotification('Error', 'Failed to load card data', 'error');
        }
    },
    
    setInputValue(id, value) {
        const element = document.getElementById(id);
        if (element) element.value = value || '';
    }
};

// Authentication functions
const Auth = {
    async login(email, password) {
        try {
            const response = await API.post('/api/login', { email, password });
            if (response.success) {
                window.location.href = '/dashboard';
            } else {
                showNotification('Error', response.error, 'error');
            }
        } catch (error) {
            showNotification('Error', 'Login failed', 'error');
        }
    },
    
    async register(userData) {
        try {
            const response = await API.post('/api/register', userData);
            if (response.success) {
                showNotification('Success', 'Account created successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1500);
            } else {
                showNotification('Error', response.error, 'error');
            }
        } catch (error) {
            showNotification('Error', 'Registration failed', 'error');
        }
    },
    
    async logout() {
        try {
            await API.post('/api/logout', {});
            window.location.href = '/';
        } catch (error) {
            window.location.href = '/';
        }
    }
};

// Initialize page-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    // Dashboard page
    if (document.getElementById('cardsContainer')) {
        Dashboard.loadCards();
    }
    
    // Customize page
    if (document.getElementById('cardPreview')) {
        CardCustomizer.init();
    }
    
    // Add global functions to window
    window.addSocialLink = () => CardCustomizer.addSocialLink();
    window.Dashboard = Dashboard;
    window.CardCustomizer = CardCustomizer;
    window.Auth = Auth;
});
