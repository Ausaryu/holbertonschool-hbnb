import { getCookie, getPlaceIdFromURL } from './utils.js';

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                 fetchPlaces
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export async function fetchPlaces(token) {
  try { // try to get places list
    const response = await fetch('http://127.0.0.1:5000/api/v1/places/', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}` // send token if the user is authentified
      }
    });
    if (!response.ok) { // if not response 200
      console.error('Erreur HTTP :', response.status);
      return;
    }
    const data = await response.json();
    displayPlaces(data); // send fetched data to diplay place for display

  } catch (error) { // si fetch echoue
    console.error('Erreur réseau :', error);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                displayPlaces
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function displayPlaces(places) {
  const placesList = document.getElementById('places-list');

  if (placesList) { // si y a une liste de place
    placesList.innerHTML = ''; // on reset la place list actuelle

    places.forEach(place => {
      const card = document.createElement('article');
      card.classList.add('place-card');
      const imagePath = `images/places/${place.id}/1.png`; // on recup la première image de la place

      card.innerHTML = `
            <div class="card">
              <img src="${imagePath || 'images/assets/placeholder.jpg'}"
                  class="card-image"
                  alt="Place image">

              <div class="card-content">
                <h3 class="card-title">${place.title}</h3>
                <p class="text-muted">Price: ${place.price}€</p>
                <a class="button button--primary card-action" href="place.html?id=${place.id}">View Details</a>
              </div>
            </div>
        `;
      card.dataset.price = place.price; // on met le price de la place en data pour le filtre

      placesList.appendChild(card); // on ajoute la place a la liste et on ré-itter
    });
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                 placeFilter
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function placeFilter() {
  const priceFilter = document.getElementById('price-filter');

  if (priceFilter) { // si il y a element pricefiltre
    const prices = [10, 50, 100]; // les filtres selectionnables

    const allOption = document.createElement('option');  // on crée un element allOption qui est l'element all 
    allOption.value = 'All';
    allOption.textContent = 'All';
    priceFilter.appendChild(allOption);

    prices.forEach(price => { // on crée toutes les autres options aka la liste prices
      const option = document.createElement('option');
      option.value = price;
      option.textContent = price;
      priceFilter.appendChild(option);
    });

    priceFilter.addEventListener('change', (event) => { // quand on change de filtre
      const selectedPrice = event.target.value; // le filtre selectioné
      const placeCards = document.querySelectorAll('.place-card'); // la liste de places

      placeCards.forEach((card) => { // on check pour chaque places si la nuit est moins chere que la value du filtre
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
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//              fetchPlacesDetails
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

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
    displayPlacesDetails(data, id);

  } catch (error) {
    console.error('Erreur réseau :', error);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             displayPlacesDetails
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function displayPlacesDetails(place, id) {
  const placesDetails = document.getElementById('place-details');
  console.log(placesDetails);

  if (placesDetails) {
    placesDetails.innerHTML = '';

    const details = document.createElement('section');
    details.classList.add('place-details');

    const amenitiesList = place.amenities
      .map(a => `<li>${a.name}</li>`)
      .join('');

    details.innerHTML = `
      <section id="place-gallery"></section>

      <div class="place-detail-content">
        <h1 class="place-title">${place.title}</h1>
        <div class="info-grid">
          <div>
            <div class="info-chip"><strong>Host:</strong> ${place.owner.first_name}</div>
          </div>
          <div>
            <div class="info-chip"><strong>Price per night:</strong> ${place.price}€</div>
          </div>
          <div>
            <div class="info-chip"><strong>Description:</strong> ${place.description}</div>
          </div>
          <div>
            <div class="info-chip">
              <strong>Amenities:</strong>
              <ul>
                ${amenitiesList}
              </ul>
            </div>
          </div>
        </div>
      </div>
    `;

    placesDetails.appendChild(details);

    displayPlaceGallery(id);
  }
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             displayPlaceGallery
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function displayPlaceGallery(placeId) {
  const gallery = document.getElementById('place-gallery');
  const lightbox = document.getElementById('placeImageModal');
  const lightboxImage = document.getElementById('lightbox-image');
  const lightboxStatus = document.getElementById('lightbox-status');
  const lightboxPrev = document.getElementById('lightbox-prev');
  const lightboxNext = document.getElementById('lightbox-next');
  const lightboxClose = document.getElementById('lightbox-close');

  if (!gallery || !lightbox || !lightboxImage) return;

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
    let currentIndex = 0;

    const renderGallery = () => {
      gallery.innerHTML = `
        <div class="gallery">
          <div class="gallery-track">
            ${existingImages.map((path, index) => `
              <figure class="gallery-slide ${index === currentIndex ? 'is-active' : ''}">
                <img
                  src="${path}"
                  class="gallery-image"
                  alt="Place image ${index + 1}"
                  data-index="${index}"
                >
              </figure>
            `).join('')}
          </div>
          ${existingImages.length > 1 ? `
            <button class="gallery-nav gallery-nav--prev" type="button" aria-label="Previous image">‹</button>
            <button class="gallery-nav gallery-nav--next" type="button" aria-label="Next image">›</button>
          ` : ''}
        </div>
      `;

      const currentImage = gallery.querySelector(`.gallery-image[data-index="${currentIndex}"]`);
      if (currentImage) {
        currentImage.addEventListener('click', () => openLightbox(currentIndex));
      }

      const prevButton = gallery.querySelector('.gallery-nav--prev');
      const nextButton = gallery.querySelector('.gallery-nav--next');

      if (prevButton) {
        prevButton.addEventListener('click', () => {
          currentIndex = (currentIndex - 1 + existingImages.length) % existingImages.length;
          renderGallery();
        });
      }

      if (nextButton) {
        nextButton.addEventListener('click', () => {
          currentIndex = (currentIndex + 1) % existingImages.length;
          renderGallery();
        });
      }
    };

    const syncLightbox = () => {
      lightboxImage.src = existingImages[currentIndex];
      lightboxImage.alt = `Place image ${currentIndex + 1}`;
      if (lightboxStatus) {
        lightboxStatus.textContent = `Image ${currentIndex + 1} of ${existingImages.length}`;
      }
    };

    const openLightbox = (index) => {
      currentIndex = index;
      syncLightbox();
      lightbox.classList.add('is-open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    };

    const closeLightbox = () => {
      lightbox.classList.remove('is-open');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    };

    if (existingImages.length === 0) {
      gallery.innerHTML = `
        <div class="card">
          <img src="images/assets/placeholder.jpg" class="gallery-image" alt="No image available">
        </div>
      `;
      return;
    }

    renderGallery();
    syncLightbox();

    lightboxPrev.onclick = () => {
      currentIndex = (currentIndex - 1 + existingImages.length) % existingImages.length;
      syncLightbox();
      renderGallery();
    };

    lightboxNext.onclick = () => {
      currentIndex = (currentIndex + 1) % existingImages.length;
      syncLightbox();
      renderGallery();
    };

    lightboxClose.onclick = closeLightbox;

    lightbox.onclick = (event) => {
      if (event.target === lightbox) {
        closeLightbox();
      }
    };

    document.onkeydown = (event) => {
      if (!lightbox.classList.contains('is-open')) return;

      if (event.key === 'Escape') closeLightbox();
      if (event.key === 'ArrowLeft') lightboxPrev.onclick();
      if (event.key === 'ArrowRight') lightboxNext.onclick();
    };
  });
}
// #######################################
