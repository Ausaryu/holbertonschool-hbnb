function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');

  if (loginLink) {
    if (!token) {
      loginLink.style.display = 'block';
      fetchPlaces();
    } else {
      loginLink.style.display = 'none';
      fetchPlaces(token);
    }
  }

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

async function fetchPlacesDetails(token, id) {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
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
    return (data);

  } catch (error) {
    console.error("Erreur réseau :", error);
  }
}

async function fetchPlacesReviews(token, id) {
  // Make a GET request to fetch places data
  // Include the token in the Authorization header
  // Handle the response and pass the data to displayPlaces function
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
    return (data);

  } catch (error) {
    console.error("Erreur réseau :", error);
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

    details.innerHTML = `
            <h1>${place.title}</h1>
            <div class="place-info">
              <p><strong>Host:</strong> ${place.owner.first_name}</p>
              <p><strong>Price per night:</strong> ${place.price}€</p>
              <p><strong>Description:</strong> ${place.description}</p>
              <p><strong>Amenities:</strong> Wi-Fi, Kitchen, Air conditioning</p>
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
      card.classList.add("place-card");

      card.innerHTML = `
            <h3>${place.title}</h3>
            <p>Price: $${place.price}</p>
            <button class="details-button"><a href="place.html?id=${place.id}">View Details</a></button>
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

function getPlaceId() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  return id;
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const path = window.location.pathname;

  if (form) {
    form.addEventListener('submit', async function (event) {
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

  placeFilter();

  if (path.includes("place.html")) {
    const id = getPlaceId();
    const token = getCookie('token');
    const place = fetchPlacesDetails(token, id);


  }

});
