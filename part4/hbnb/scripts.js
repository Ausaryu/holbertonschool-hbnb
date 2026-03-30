/* 
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector("form");

  form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    console.log(email, password);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      });

      const data = await response.json();
      console.log(data);

      document.cookie = `token=${data.access_token}; path=/`;

      console.log("Token stocké !");

    } catch (error) {
      console.error("Erreur login :", error);
    }

    console.log("Formulaire envoyé !");
  });



});
