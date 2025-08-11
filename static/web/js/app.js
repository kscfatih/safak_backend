// Mobil Web App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Messages otomatik kapanma
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Çocuk sayısı değiştiğinde form alanları
    const hasChildrenCheckbox = document.getElementById('has_children');
    const childrenCountSelect = document.getElementById('children_count');
    const childrenContainer = document.getElementById('children_container');

    if (hasChildrenCheckbox && childrenCountSelect && childrenContainer) {
        hasChildrenCheckbox.addEventListener('change', function() {
            if (this.checked) {
                childrenCountSelect.parentElement.style.display = 'block';
            } else {
                childrenCountSelect.parentElement.style.display = 'none';
                childrenContainer.innerHTML = '';
                childrenCountSelect.value = '0';
            }
        });

        childrenCountSelect.addEventListener('change', function() {
            const count = parseInt(this.value);
            updateChildrenFields(count);
        });
    }

    // Barkod animasyonu
    const barcodeCard = document.querySelector('.barcode-card');
    if (barcodeCard) {
        barcodeCard.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    }

    // Smooth scroll için navigation
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            // Aktif nav item'ı güncelle
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Form validasyonu
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--error)';
                    field.addEventListener('input', function() {
                        this.style.borderColor = 'var(--gray-300)';
                    });
                }
            });

            if (!isValid) {
                e.preventDefault();
                showMessage('Lütfen tüm gerekli alanları doldurun!', 'error');
            }
        });
    });

    // Touch feedback için button'lar
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });

});

// Çocuk form alanları güncelleme
function updateChildrenFields(count) {
    const container = document.getElementById('children_container');
    if (!container) {
        console.error('children_container bulunamadı!');
        return;
    }

    console.log('updateChildrenFields çağrıldı, count:', count);

    // AJAX ile sunucudan form HTML'i al
    fetch('/ajax/children-count/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            children_count: count
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        if (data.html) {
            container.innerHTML = data.html;
            container.style.display = count > 0 ? 'block' : 'none';
            console.log('HTML güncellendi, yeni içerik:', container.innerHTML);
        } else if (data.error) {
            console.error('Server error:', data.error);
            showMessage('Çocuk form alanları yüklenemedi: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        showMessage('Çocuk form alanları yüklenemedi!', 'error');
    });
}

// CSRF Token alma
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Mesaj gösterme
function showMessage(text, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type} fade-in`;
    messageDiv.textContent = text;
    
    messagesContainer.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 5000);
}

// Messages container oluşturma
function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

// Barkod görüntü oluşturma (Pure JavaScript)
function generateBarcode(value, container) {
    if (!value || !container) return;

    // Pattern algoritması
    const patterns = [];
    const seed = value.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    
    for (let i = 0; i < 40; i++) {
        const width = ((seed + i) % 4) + 1;
        patterns.push(width);
    }

    // HTML oluştur
    const barcodeHTML = `
        <div class="barcode-stripes">
            ${patterns.map((width, index) => 
                `<div class="barcode-line" style="width: ${width}px; background-color: ${index % 2 === 0 ? '#000' : 'transparent'};"></div>`
            ).join('')}
        </div>
        <div class="barcode-code">${value}</div>
    `;

    container.innerHTML = barcodeHTML;
}

// Sayfa yüklendiğinde barkod oluştur
document.addEventListener('DOMContentLoaded', function() {
    const barcodeContainer = document.querySelector('.barcode-display');
    const barcodeCode = document.querySelector('[data-barcode-code]');
    
    if (barcodeContainer && barcodeCode) {
        const code = barcodeCode.getAttribute('data-barcode-code');
        generateBarcode(code, barcodeContainer);
    }
});

// PWA Support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/web/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}