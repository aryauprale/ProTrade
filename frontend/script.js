
const firstNameInput = document.getElementById('first-name');
const lastNameInput = document.getElementById('last-name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const form = document.getElementById('form');
const errorElement = document.getElementById('error');

form.addEventListener ('submit', (e) => {
    let messsage = [];
    if (emailInput.value === '' || emailInput.value == null) {
    const email = emailInput.value; messsage.push('email is required')
    }
    if (passwordInput.value === '' || passwordInput.value == null) {
    const password = passwordInput.value; messsage.push('password is required')
    }

    if (messsage.length <= 6) {
        messsage.push('password must be at least 6 characters');
        e.preventDefault();

        errorElement.innerText = messsage.join(', ');
    }

    


    // Perform your login logic here
})