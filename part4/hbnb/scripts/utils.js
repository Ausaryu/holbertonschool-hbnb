export function getCookie (name) {
  const cookies = document.cookie.split('; ');

  for (const cookie of cookies) {
    const [key, value] = cookie.split('=');

    if (key === name) {
      return value;
    }
  }

  return null;
}

export function getPlaceIdFromURL () {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  return id;
}
