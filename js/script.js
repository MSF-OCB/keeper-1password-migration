{
  const userName = document.querySelector("#usernameInput");
  const password = document.querySelector("#passwordInput");
  const submitButton = document.querySelector("#submitButton");
  const form = document.querySelector("#form");
  const url = "https://keeper1pmigration.free.beeceptor.com";
  let myHeaders = new Headers();
  let urlencoded = new URLSearchParams();

  const login = (e) => {
    e.preventDefault();
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");
    urlencoded.append("username", userName.value);
    urlencoded.append("password", password.value);

    const requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: urlencoded,
      redirect: "follow",
    };
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");
    return fetch(`${url}/login`, requestOptions)
      .then((response) => response.text())
      .then((token) => token)
      .catch((error) =>
        alert("Please recheck username and password, then try again")
      );
  };

  const init = () => {
    form.addEventListener(`submit`, login);
  };

  init();
}
