// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//                 getCookie
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function getCookie (name) {
  const cookies = document.cookie.split('; ');  //transform cookie string into an array

  // itter the array 
  for (const cookie of cookies) {
    // transform string like "token=abc" into : -key = "token"
    //                                          -value = "abc"
    const [key, value] = cookie.split('=');

    if (key === name) {
      return value;
    }
  }

  return null;
}
// #######################################

// ⣿⣿⣿⡿⠿⠿⠿⠟⠛⠛⠛⠋⠉⠉⠉⠉⠙⠛⠛⠛⠻⠿⠿⠿⢿⣿⣿⣿
//             getPlaceIdFromURL
// ⣿⣿⣿⣷⣶⣶⣶⣦⣤⣤⣤⣄⣀⣀⣀⣀⣠⣤⣤⣤⣴⣶⣶⣶⣾⣿⣿⣿

export function getPlaceIdFromURL () {
  const params = new URLSearchParams(window.location.search); //transform url param into a dict object
  const id = params.get('id'); //get id from the converted dict
  return id;
}
// #######################################
