document.addEventListener('DOMContentLoaded', () => {
    const btnShowRegister = document.getElementById('show-register');
    const btnShowLogin = document.getElementById('show-login');
    const loginContainer = document.getElementById('login-container');
    const registerContainer = document.getElementById('register-container');

    if (btnShowRegister && btnShowLogin) {
        // Alternar a Registro
        btnShowRegister.addEventListener('click', (e) => {
            e.preventDefault();
            loginContainer.classList.add('hidden');
            registerContainer.classList.remove('hidden');
        });

        // Alternar a Login
        btnShowLogin.addEventListener('click', (e) => {
            e.preventDefault();
            registerContainer.classList.add('hidden');
            loginContainer.classList.remove('hidden');
        });
    }
});
