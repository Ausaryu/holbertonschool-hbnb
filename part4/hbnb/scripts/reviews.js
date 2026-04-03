import { getCookie, getIdFromURL } from './utils.js';

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             fetchPlacesReviews
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function fetchPlacesReviews() {
  const id = getIdFromURL();
  const token = getCookie('token');
  try {
    console.log('test');
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${id}/reviews`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    if (!response.ok) {
      console.error('Erreur HTTP :', response.status);
      return;
    }

    const data = await response.json();
    console.log(data);
    reviewBtn(data);
    displayPlacesReviews(data);
  } catch (error) {
    console.error('Erreur réseau :', error);
    reviewBtn([]);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//            displayPlacesReviews
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function displayPlacesReviews(reviews) {
  const reviewsList = document.getElementById('reviews');

  if (reviewsList) {
    reviewsList.innerHTML = '';

    if (!reviews || reviews.length === 0) {
      reviewsList.innerHTML = '<p class="text-muted">No reviews yet for this place.</p>';
      return;
    }

    const reviewsWithUsers = await Promise.all(
      reviews.map(async (review) => {
        try {
          const res = await fetch(`http://127.0.0.1:5000/api/v1/users/${review.user_id}`);
          const user = await res.json();

          return {
            ...review,
            userName: user.first_name
          };
        } catch (error) {
          console.error('Erreur user:', error);
          return {
            ...review,
            userName: 'Unknown'
          };
        }
      })
    );

    reviewsWithUsers.forEach(review => {
      const card = document.createElement('article');
      card.classList.add('review-card');

      card.innerHTML = `
        <div class="card">
          <div class="card-content">
            <p><strong>User:</strong> ${review.userName}</p>
            <p><strong>Rating:</strong> ${review.rating}/5</p>
            <p class="text-muted">${review.text}</p>
            <div class="edit-review-btn"></div>
          </div>
        </div>
      `;

      console.log(review)
      if (review.is_admin || review.can_edit) {
        const BtnContainer = card.querySelector('.edit-review-btn')
        editReviewBtn(BtnContainer, review)
      }

      reviewsList.appendChild(card);
    });
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  reviewBtn
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function reviewBtn(reviews = []) {
  const btn = document.getElementById('review-btn');
  const placeId = getIdFromURL();
  const token = getCookie('token');

  if (!btn) {
    return;
  }

  if (!token) {
    btn.innerHTML = '';
    return;
  }

  const hasEditableReview = reviews.some((review) => review.can_edit);

  if (hasEditableReview) {
    btn.innerHTML = '';
    return;
  }

  btn.innerHTML = `
    <a class="button button--primary button--large" href="add_review.html?id=${placeId}">
      Add a review
    </a>
  `;
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  reviewBtn
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function editReviewBtn(btn, review) {
  if (btn) {
    btn.innerHTML = `
      <a class="button button--primary button--large" href="edit_review.html?id=${review.id}">
        edit
      </a>
    `;
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//           fetchReviewDetails
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function fetchReviewDetails() {
  const reviewId = getIdFromURL();

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/reviews/${reviewId}`);
    
    if (!response.ok) {
      console.error("Erreur fetch review");
      return;
    }

    const review = await response.json();
    fillReviewForm(review);
    return review;

  } catch (error) {
    console.error(error);
  }
}
// #######################################


// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             fillReviewForm
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

function fillReviewForm(review) {
  const reviewText = document.getElementById('review-text');
  const rating = document.getElementById('rating');

  if (!reviewText || !rating) return;

  reviewText.value = review.text;
  rating.value = review.rating;

  const stars = document.querySelectorAll('#rating-stars span');

  stars.forEach((star, index) => {
    star.classList.toggle('active', index < review.rating);
  });
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             updateReview
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

async function updateReview(token, reviewId, placeId) {
  const reviewText = document.getElementById('review-text');
  const ratingInput = document.getElementById('rating');

  if (!reviewText || !ratingInput) return;

  const text = reviewText.value.trim();
  const rating = Number(ratingInput.value);

  if (!text || !rating) {
    console.error('Review text or rating is missing');
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/reviews/${reviewId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ text, rating })
    });

    if (response.ok) {
      window.location.href = `place.html?id=${placeId}`;
    }

  } catch (error) {
    console.error(error);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             deleteReview
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿
async function deleteReview(token, reviewId, placeId) {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/v1/reviews/${reviewId}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (response.ok) {
      window.location.href = `place.html?id=${placeId}`;
    }

  } catch (error) {
    console.error(error);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//            setupEditReviewForm
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function setupEditReviewForm() {
  const token = getCookie('token');
  const reviewId = getIdFromURL();
  const form = document.getElementById('review-form');
  const deleteBtn = document.getElementById('delete-review');

  if (!token) {
    window.location.href = 'login.html';
    return;
  }

  if (!reviewId) {
    console.error('Review id missing in URL');
    return;
  }

  const review = await fetchReviewDetails();

  if (!review || !review.place_id) {
    console.error('Associated place id missing for review');
    return;
  }

  setupStarRating();

  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      updateReview(token, reviewId, review.place_id);
    });
  }

  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => {
      deleteReview(token, reviewId, review.place_id);
    });
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//               setupStarRating
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function setupStarRating() {
  const container = document.getElementById('rating-stars');
  const ratingInput = document.getElementById('rating');

  if (!container || !ratingInput) return;

  const stars = Array.from(container.querySelectorAll('span'));
  let selectedRating = Number(ratingInput.value) || 0;

  // ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
  //                 updateStars
  // ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

  function updateStars(value) {
    stars.forEach((star, index) => {
      star.classList.toggle('active', index < value);
    });
  }
  // #######################################

  stars.forEach((star, index) => {
    const starValue = index + 1;

    star.addEventListener('mouseenter', () => {
      updateStars(starValue);
    });

    star.addEventListener('click', () => {
      selectedRating = starValue;
      ratingInput.value = starValue;
      updateStars(selectedRating);
    });
  });

  container.addEventListener('mouseleave', () => {
    updateStars(selectedRating);
  });

  updateStars(selectedRating);
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                 updateStars
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

function updateStars(stars, value) {
  stars.forEach((star, index) => {
    if (index < value) {
      star.classList.add('active');
    } else {
      star.classList.remove('active');
    }
  });
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  reviewAdd
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function reviewAdd() {
  const reviewForm = document.getElementById('review-form');
  const token = getCookie('token');
  const placeId = getIdFromURL();

  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = document.getElementById('review-text').value;
      submitReview(token, placeId, reviewText, reviewForm);
    });
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                submitReview
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function submitReview(token, placeId, reviewText, reviewForm) {
  try {
    const rating = Number(document.getElementById('rating').value);
    
    if (!rating) {
      alert("Please select a rating");
      return;
    }

    const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        text: reviewText,
        rating,
        place_id: placeId
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log(data);
      console.log('tets');

      reviewForm.reset();

      window.location.href = `place.html?id=${placeId}`;
    } else {
      reviewForm.reset();
      console.log('tets');
      window.location.href = `place.html?id=${placeId}`;
    }
  } catch (error) {
    console.error(error);
  }
}
// #######################################
