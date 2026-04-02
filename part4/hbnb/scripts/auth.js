import { getCookie } from './utils.js';
import { fetchPlaces } from './places.js';

export function checkAuthentication () {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout');
  const addReviewSection = document.getElementById('review-btn');

  if (loginLink && logoutLink) {
    if (!token) {
      loginLink.style.display = 'block';
      logoutLink.style.display = 'none';
    } else {
      loginLink.style.display = 'none';
      logoutLink.style.display = 'block';
    }
    fetchPlaces(token);
  }

  if (addReviewSection) {
    if (!token) {
      addReviewSection.style.display = 'none';
    } else {
      addReviewSection.style.display = 'block';
    }
  }
}

export function logout () {
  document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
  window.location.href = 'index.html';
}

export function setupLoginForm () {
  const loginForm = document.getElementById('login-form');

  if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
      event.preventDefault();

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const errorMessage = document.getElementById('error-login');

      console.log(email, password);

      errorMessage.textContent = '';

      try {
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email,
            password
          })
        });

        if (response.ok) {
          const data = await response.json();
          console.log(data);

          document.cookie = `token=${data.access_token}; path=/`;
          window.location.href = 'index.html';

          console.log('Token stocké !');
        } else {
          if (response.status === 401) {
            errorMessage.textContent = 'Invalid email or password.';
          } else {
            errorMessage.textContent = ('Login failed: ' + response.statusText);
          }
        }
      } catch (error) {
        errorMessage.textContent = 'Server unreachable.';
        console.error(error);
      }
    });
  }
}
