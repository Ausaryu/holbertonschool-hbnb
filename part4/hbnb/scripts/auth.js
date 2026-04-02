import { getCookie } from './utils.js';
import { fetchPlaces } from './places.js';

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//           checkAuthentication
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function checkAuthentication () {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout');
  const addReviewSection = document.getElementById('review-btn');

  // check if loginLink & logoutLink exist
  if (loginLink && logoutLink) {
    if (!token) {
      // si non connecté affiche login
      loginLink.style.display = 'block';
      logoutLink.style.display = 'none';
    } else {
      // sinon affiche logout
      loginLink.style.display = 'none';
      logoutLink.style.display = 'block';
    }
    fetchPlaces(token); // affiche les places sur la page d'accueil
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  logout
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿
// logout btn function
export function logout () {
  document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;'; // make the cookie expire imediatelly 
  window.location.href = 'index.html';  // redirect to home
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//               setupLoginForm
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function setupLoginForm () {
  const loginForm = document.getElementById('login-form');

  // check si le formulaire de login existe (= si on est sur login.html)
  if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
      event.preventDefault(); // empeche le comportement par defaut de submit

      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const errorMessage = document.getElementById('error-login');

      errorMessage.textContent = '';

      try { // try un post du formullaire de login
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

        if (response.ok) { // si reponse 200
          const data = await response.json();

          document.cookie = `token=${data.access_token}; path=/`; // j'enregistre le token dans les cookies
          window.location.href = 'index.html'; // je redirige vers l'index

        } else {
          if (response.status === 401) { // if invalid credentials
            errorMessage.textContent = 'Invalid email or password.';
          } else { // autres problemes
            errorMessage.textContent = ('Login failed: ' + response.statusText);
          }
        }
      } catch (error) { // si le fetch n'a pas fonctionné
        errorMessage.textContent = 'Server unreachable.';
        console.error(error);
      }
    });
  }
}
// #######################################
