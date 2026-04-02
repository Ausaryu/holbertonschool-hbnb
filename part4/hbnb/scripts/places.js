import { getCookie, getPlaceIdFromURL } from './utils.js';

export async function fetchPlaces(token) {
  try {
    console.log('test');
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
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
    displayPlaces(data);
  } catch (error) {
    console.error('Erreur réseau :', error);
  }
}

export function placeFilter() {
  const priceFilter = document.getElementById('price-filter');

  if (priceFilter) {
    const prices = [10, 50, 100];

    const allOption = document.createElement('option');
    allOption.value = 'All';
    allOption.textContent = 'All';
    priceFilter.appendChild(allOption);

    prices.forEach(price => {
      const option = document.createElement('option');
      option.value = price;
      option.textContent = price;
      priceFilter.appendChild(option);
    });

    priceFilter.addEventListener('change', (event) => {
      const selectedPrice = event.target.value;
      const placeCards = document.querySelectorAll('.place-card');

      placeCards.forEach((card) => {
        const cardPrice = Number(card.dataset.price);
        if (selectedPrice === 'All') {
          card.style.display = 'block';
        } else {
          const maxPrice = Number(selectedPrice);

          if (cardPrice <= maxPrice) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        }
      });
    });
  }
}

export async function fetchPlacesDetails() {
  const id = getPlaceIdFromURL();
  const token = getCookie('token');

  try {
    console.log('test');
    const response = await fetch(`http://127.0.0.1:5000/api/v1/places/${id}`, {
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
    displayPlacesDetails(data);
    displayPlaceGallery(id);
  } catch (error) {
    console.error('Erreur réseau :', error);
  }
}

export function displayPlacesDetails(place) {
  const placesDetails = document.getElementById('place-details');
  console.log(placesDetails);

  if (placesDetails) {
    placesDetails.innerHTML = '';

    const details = document.createElement('section');
    details.classList.add('place-details');

    const amenitiesList = place.amenities
      .map(a => a.name)
      .join(', ');

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

export function displayPlaces(places) {
  const placesList = document.getElementById('places-list');

  if (placesList) {
    placesList.innerHTML = '';

    places.forEach(place => {
      const card = document.createElement('article');
      card.classList.add('place-card', 'col-md-6', 'col-xl-4');
      const imagePath = `images/places/${place.id}/1.png`;

      card.innerHTML = `
            <div class="card h-100 border-0 shadow-sm">
              <img src="${imagePath || 'images/assets/placeholder.jpg'}"
                  class="card-img-top"
                  alt="Place image">

              <div class="card-body d-flex flex-column">
                <h3 class="h5 card-title">${place.title}</h3>
                <p class="card-text text-secondary mb-4">Price: ${place.price}€</p>
                <a class="btn btn-warning details-button mt-auto align-self-start" href="place.html?id=${place.id}">View Details</a>
              </div>
            </div>
        `;
      card.dataset.price = place.price;

      placesList.appendChild(card);
    });
  }
}

export function displayPlaceGallery(placeId) {
  const gallery = document.getElementById('place-gallery');
  const modalCarouselInner = document.getElementById('placeModalCarouselInner');

  if (!gallery || !modalCarouselInner) return;

  const maxImages = 5;
  const imagePaths = [];

  for (let i = 1; i <= maxImages; i++) {
    imagePaths.push(`images/places/${placeId}/${i}.png`);
  }

  const preloadPromises = imagePaths.map(path => {
    return new Promise(resolve => {
      const img = new Image();
      img.src = path;

      img.onload = () => resolve(path);
      img.onerror = () => resolve(null);
    });
  });

  Promise.all(preloadPromises).then(validImages => {
    const existingImages = validImages.filter(path => path !== null);

    if (existingImages.length === 0) {
      gallery.innerHTML = `
        <div class="card border-0 shadow-sm">
          <img src="images/assets/placeholder.jpg" class="w-100 place-gallery-img" alt="No image available">
        </div>
      `;

      modalCarouselInner.innerHTML = `
        <div class="carousel-item active">
          <img src="images/assets/placeholder.jpg" class="d-block w-100 place-modal-img" alt="No image available">
        </div>
      `;
      return;
    }

    gallery.innerHTML = `
      <div id="placeCarousel" class="carousel slide shadow-sm rounded overflow-hidden">
        <div class="carousel-inner">
          ${existingImages.map((path, index) => `
            <div class="carousel-item ${index === 0 ? 'active' : ''}">
              <img
                src="${path}"
                class="d-block w-100 place-gallery-img gallery-clickable"
                alt="Place image ${index + 1}"
                data-index="${index}"
              >
            </div>
          `).join('')}
        </div>

        ${existingImages.length > 1 ? `
          <button class="carousel-control-prev" type="button" data-bs-target="#placeCarousel" data-bs-slide="prev">
            <span class="carousel-control-prev-icon"></span>
            <span class="visually-hidden">Previous</span>
          </button>

          <button class="carousel-control-next" type="button" data-bs-target="#placeCarousel" data-bs-slide="next">
            <span class="carousel-control-next-icon"></span>
            <span class="visually-hidden">Next</span>
          </button>
        ` : ''}
      </div>
    `;

    modalCarouselInner.innerHTML = `
      ${existingImages.map((path, index) => `
        <div class="carousel-item ${index === 0 ? 'active' : ''}">
          <div class="place-modal-slide">
            <img
              src="${path}"
              class="d-block place-modal-img"
              alt="Place image ${index + 1}"
            >
          </div>
        </div>
      `).join('')}
    `;

    if (window.bootstrap) {
      const mainCarouselElement = document.getElementById('placeCarousel');
      if (mainCarouselElement && existingImages.length > 1) {
        new bootstrap.Carousel(mainCarouselElement, {
          interval: false,
          ride: false
        });
      }

      const modalCarouselElement = document.getElementById('placeModalCarousel');
      const modalElement = document.getElementById('placeImageModal');

      let modalCarouselInstance = null;

      if (modalCarouselElement) {
        modalCarouselInstance = new bootstrap.Carousel(modalCarouselElement, {
          interval: false,
          ride: false
        });
      }

      const modalInstance = new bootstrap.Modal(modalElement);

      const clickableImages = document.querySelectorAll('.gallery-clickable');

      clickableImages.forEach((img) => {
        img.addEventListener('click', () => {
          const clickedIndex = Number(img.dataset.index);

          modalInstance.show();

          if (modalCarouselInstance) {
            modalCarouselInstance.to(clickedIndex);
          }
        });
      });
    }
  });
}
