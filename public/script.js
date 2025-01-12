document.addEventListener('DOMContentLoaded', function() {
    const closeButton = document.querySelector('.close-banner');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            const banner = this.closest('.announcement-banner');
            if (banner) {
                banner.style.display = 'none';
            }
        });
    }
}); 