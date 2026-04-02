import { checkAuthentication, logout, setupLoginForm } from './auth.js';
import { placeFilter, fetchPlacesDetails } from './places.js';
import { fetchPlacesReviews, reviewAdd, reviewBtn, setupStarRating  } from './reviews.js';

document.addEventListener('DOMContentLoaded', () => {
  const reviewForm = document.getElementById('review-form');
  const path = window.location.pathname;

  setupLoginForm();

  checkAuthentication();

  if (reviewForm) {
    reviewAdd();
    setupStarRating();
  }

  const logoutBtn = document.getElementById('logout');

  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }

  placeFilter();

  if (path.includes('place.html')) {
    fetchPlacesDetails();
    fetchPlacesReviews();
    reviewBtn();
  }
});
