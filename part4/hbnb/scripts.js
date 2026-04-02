function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout');
  const addReviewSection = document.getElementById('add-review');

  if (loginLink || logoutLink) {
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

function logout() {
  document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
  window.location.href = "index.html";
}

function getCookie(name) {
  const cookies = document.cookie.split('; ');

  for (const cookie of cookies) {
    const [key, value] = cookie.split('=');

    if (key === name) {
      return value;
    }
  }

  return null;
}

async function fetchPlaces(token) {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
  try {
    console.log("test")
    const response = await fetch("http://127.0.0.1:5000/api/v1/places/", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    if (!response.ok) {
      console.error("Erreur HTTP :", response.status);
      return;
    }

    const data = await response.json();
    console.log(data);
    displayPlaces(data)

  } catch (error) {
    console.error("Erreur réseau :", error);
  }
}

async function fetchPlacesDetails() {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
  const id = getPlaceIdFromURL();
  const token = getCookie('token');

  try {
    console.log("test")
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${id}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    if (!response.ok) {
      console.error("Erreur HTTP :", response.status);
      return;
    }

    const data = await response.json();
    console.log(data);
    displayPlacesDetails(data)

  } catch (error) {
    console.error("Erreur réseau :", error);
  }
}

async function fetchPlacesReviews() {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
  const id = getPlaceIdFromURL();
  const token = getCookie('token');
  try {
    console.log("test")
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${id}/reviews`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    if (!response.ok) {
      console.error("Erreur HTTP :", response.status);
      return;
    }

    const data = await response.json();
    console.log(data);
    displayPlacesReviews(data);

  } catch (error) {
    console.error("Erreur réseau :", error);
  }
}

async function displayPlacesReviews(reviews) {
  // Clear the current content of the places list
  // Iterate over the places data
  // For each place, create a div element and set its content
  // Append the created element to the places list
  const reviewsList = document.getElementById("reviews");

  if (reviewsList) {
    reviewsList.innerHTML = "";

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
          console.error("Erreur user:", error);
          return {
            ...review,
            userName: "Unknown"
          };
        }
      })
    );


    reviewsWithUsers.forEach(review => {
      const card = document.createElement("article");
      card.classList.add("review-card", "col-lg-6");

      card.innerHTML = `
        <div class="card h-100 border-0 shadow-sm">
          <div class="card-body">
            <p class="mb-2"><strong>User:</strong> ${review.userName}</p>
            <p class="mb-2"><strong>Rating:</strong> ${review.rating}/5</p>
            <p class="mb-0 text-secondary">${review.text}</p>
          </div>
        </div>
      `;

      reviewsList.appendChild(card);
    });
  }
}

function displayPlacesDetails(place) {
  // Clear the current content of the places list
  // Iterate over the places data
  // For each place, create a div element and set its content
  // Append the created element to the places list
  const placesDetails = document.getElementById("place-details");
  console.log(placesDetails)

  if (placesDetails) {
    placesDetails.innerHTML = "";

    const details = document.createElement("section");
    details.classList.add("place-details");

    const amenitiesList = place.amenities
      .map(a => a.name)
      .join(", ");

    details.innerHTML = `
            <h1 class="display-6 fw-bold mb-4">${place.title}</h1>
            <div class="place-info row g-3">
              <div class="col-md-6">
                <div class="info-chip"><strong>Host:</strong> ${place.owner.first_name}</div>
              </div>
              <div class="col-md-6">
                <div class="info-chip"><strong>Price per night:</strong> ${place.price}€</div>
              </div>
              <div class="col-12">
                <div class="info-chip"><strong>Description:</strong> ${place.description}</div>
              </div>
              <div class="col-12">
                <div class="info-chip"><strong>Amenities:</strong> ${amenitiesList}</div>
              </div>
            </div>
        `;

    placesDetails.appendChild(details);
  }
}

function displayPlaces(places) {
  // Clear the current content of the places list
  // Iterate over the places data
  // For each place, create a div element and set its content
  // Append the created element to the places list
  const placesList = document.getElementById("places-list");

  if (placesList) {
    placesList.innerHTML = "";

    places.forEach(place => {
      const card = document.createElement("article");
      card.classList.add("place-card", "col-md-6", "col-xl-4");

      card.innerHTML = `
            <div class="card h-100 border-0 shadow-sm">
              <img src="${place.image || 'images/placeholder.jpg'}"
                  class="card-img-top"
                  alt="Place image">

              <div class="card-body d-flex flex-column">
                <h3 class="h5 card-title">${place.title}</h3>
                <p class="card-text text-secondary mb-4">Price: $${place.price}</p>
                <a class="btn btn-warning details-button mt-auto align-self-start" href="place.html?id=${place.id}">View Details</a>
              </div>
            </div>
        `;
      card.dataset.price = place.price

      placesList.appendChild(card);
    });
  }
}

function placeFilter() {
  const priceFilter = document.getElementById('price-filter');

  if (priceFilter) {
    const prices = [10, 50, 100];

    const allOption = document.createElement("option");
    allOption.value = "All";
    allOption.textContent = "All";
    priceFilter.appendChild(allOption);

    prices.forEach(price => {
      const option = document.createElement("option");
      option.value = price;
      option.textContent = price;
      priceFilter.appendChild(option);
    });

    priceFilter.addEventListener('change', (event) => {
      const selectedPrice = event.target.value;
      const placeCards = document.querySelectorAll('.place-card');

      placeCards.forEach((card) => {
        const cardPrice = Number(card.dataset.price);
        if (selectedPrice === "All") {
          card.style.display = "block";
        } else {
          const maxPrice = Number(selectedPrice);

          if (cardPrice <= maxPrice) {
            card.style.display = "block";
          } else {
            card.style.display = "none";
          }
        }
      });

    });
  }
}

function getPlaceIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  return id;
}

// ########################################################################
//  Reviews form
// ########################################################################

function reviewAdd() {
  const reviewForm = document.getElementById('review-form');
  const token = getCookie('token');
  const placeId = getPlaceIdFromURL();

  if (reviewForm) {
    reviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      // Get review text from form
      // Make AJAX request to submit review
      // Handle the response
      const reviewText = document.getElementById('review-text').value;
      submitReview(token, placeId, reviewText, reviewForm);
    });
  }
}

async function submitReview(token, placeId, reviewText, reviewForm) {
  // Make a POST request to submit review data
  // Include the token in the Authorization header
  // Send placeId and reviewText in the request body
  // Handle the response

  try {
    const rating = Number(document.getElementById("rating").value);
    const response = await fetch('http://127.0.0.1:5000/api/v1/reviews/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        text: reviewText,
        rating: rating,
        place_id: placeId,
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log(data);

      reviewForm.reset();

      window.location.reload();

    } else {
      reviewForm.reset();
    }
  } catch (error) {
    console.error(error);
  }
}

// ========================================================================

// ########################################################################
//  main
// ########################################################################

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const reviewForm = document.getElementById('review-form');
  const path = window.location.pathname;

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

  checkAuthentication();

  if (reviewForm) {
    reviewAdd()
  }

  const logoutBtn = document.getElementById("logout");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
  }

  placeFilter();

  if (path.includes("place.html")) {
    fetchPlacesDetails();
    fetchPlacesReviews();


  }

});
