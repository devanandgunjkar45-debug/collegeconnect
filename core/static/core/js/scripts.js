const themeToggle = document.getElementById('theme-toggle');
const body = document.body;

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        if (body.classList.contains('dark-mode')) {
            body.classList.replace('dark-mode', 'light-mode');
            themeToggle.textContent = 'Dark';
        } else {
            body.classList.replace('light-mode', 'dark-mode');
            themeToggle.textContent = 'Light';
        }
    });
}

// Show loading state for auth forms
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const submit = form.querySelector('button[type=submit]');
            if (submit) {
                submit.disabled = true;
                submit.textContent = 'Please wait...';
            }
        });
    });
});
