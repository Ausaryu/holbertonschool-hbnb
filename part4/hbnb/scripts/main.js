import { checkAuthentication, logout, setupLoginForm } from './auth.js';
import { placeFilter, fetchPlacesDetails } from './places.js';
import { fetchPlacesReviews, reviewAdd, reviewBtn, setupStarRating, setupEditReviewForm } from './reviews.js';

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  Main
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  const logoutBtn = document.getElementById('logout');

  // ─────────── GLOBAL ───────────

  checkAuthentication();

  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }

  // ─────────── HOME ───────────
  if (path.includes('index.html')) {
    placeFilter();
  }

  // ─────────── LOGIN ───────────
  if (path.includes('login.html')) {
    setupLoginForm();
  }

  // ─────────── PLACE DETAILS ───────────
  if (path.includes('place.html')) {
    fetchPlacesDetails();
    fetchPlacesReviews();
  }

  // ─────────── ADD REVIEW ───────────
  if (path.includes('add_review.html')) {
    reviewAdd();
    setupStarRating();
  }

  if (path.includes('edit_review.html')) {
    setupEditReviewForm();
  }
});
// #######################################
