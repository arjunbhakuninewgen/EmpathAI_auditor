// ISSUE 15: Auto-updating content without aria-live
setInterval(() => {
    const price = (100 + Math.random() * 10).toFixed(2);
    // Updates DOM but no screen reader announcement because parent lacks aria-live
    document.getElementById('price').innerText = price;
}, 3000);

// ISSUE 13: Modal Logic (No focus trapping)
const modal = document.getElementById('modal-overlay');
document.getElementById('open-modal').addEventListener('click', () => {
    modal.classList.remove('hidden');
    // Violation: Does not move focus to modal
    // Violation: Does not trap focus inside modal
});

document.getElementById('close-modal').addEventListener('click', () => {
    modal.classList.add('hidden');
    // Violation: Does not return focus to trigger
});

// ISSUE 16: Keyboard Trap Logic
const trap = document.getElementById('keyboard-trap');
const trapInput = trap.querySelector('input');

trapInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault(); // Prevents user from tabbing out
        console.log('Trapped!');
        // Just cycles focus back to the div, trapping the user
        trap.focus();
    }
});

// Dynamic Content Injection (To test scanner's wait capability)
setTimeout(() => {
    const dynamicDiv = document.createElement('div');
    dynamicDiv.id = 'dynamic-content';
    dynamicDiv.innerHTML = '<p>I appeared after 2 seconds.</p>';
    // ISSUE 10 (Variant): Tabindex on non-interactive in dynamic content
    dynamicDiv.setAttribute('tabindex', '0'); 
    document.body.appendChild(dynamicDiv);
}, 2000);