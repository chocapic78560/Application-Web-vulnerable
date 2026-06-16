// MyEduConnect — Main JS

// Auto-dismiss flash messages after 5s
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash').forEach(el => {
        setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity .5s'; setTimeout(() => el.remove(), 500); }, 5000);
    });

    // Card number formatting
    const cardInput = document.querySelector('input[name="card_number"]');
    if (cardInput) {
        cardInput.addEventListener('input', e => {
            let v = e.target.value.replace(/\D/g,'').substring(0,16);
            e.target.value = v.replace(/(\d{4})(?=\d)/g, '$1 ');
        });
    }
});
