import { getCookie, getPlaceIdFromURL } from './utils.js';

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             fetchPlacesReviews
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function fetchPlacesReviews() {
  const id = getPlaceIdFromURL();
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
    displayPlacesReviews(data);
  } catch (error) {
    console.error('Erreur réseau :', error);
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
          </div>
        </div>
      `;

      reviewsList.appendChild(card);
    });
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                  reviewBtn
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function reviewBtn() {
  const btn = document.getElementById('review-btn');
  const placeId = getPlaceIdFromURL();

  if (btn) {
    btn.innerHTML = `
      <a class="button button--primary button--large" href="add_review.html?id=${placeId}">
        Add a review
      </a>
    `;
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
  let selectedRating = 0;

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
  const placeId = getPlaceIdFromURL();

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
