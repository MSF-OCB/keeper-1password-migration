{
  const userName = document.querySelector("#usernameInput");
  const password = document.querySelector("#passwordInput");
  const form = document.querySelector("#form");
  const dots = document.querySelectorAll(".dot");
  const migrationButton = document.querySelector(".migrate-button");
  const scrollContainer = document.querySelector(".scroll-container");
  const doneMsg = document.querySelector(".done-msg");
  const url = "";

  function throw_nok(response) {
    if( ! response.ok) throw Error(response.text())
    return response;
  }

  const login = async (e, endpoint) => {
    if (endpoint === "migrate") migrationButton.setAttribute("id", "hidden");
    let counter = endpoint === "login" ? 1 : 2;
    e.preventDefault();

    let urlencoded = new URLSearchParams();
    let myHeaders = new Headers();

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
    await fetch(`${url}/${endpoint}`, requestOptions)
      .then(throw_nok)
      .then((response) => response.text())
      .then((hash) => {
        dots[counter].setAttribute("id", "in-progress");
        return getConsole(hash, "");
      })
      .catch((error) =>
        alert("Please recheck username and password, then try again")
      );
  };

  const getConsole = async (token, endToken) => {
    form.setAttribute("id", "hidden");
    scrollContainer.removeAttribute("id", "hidden");
    // Auto scroll
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
    if (endToken.includes("***CLEAR***")) {
      return migrationButton.removeAttribute("id", "hidden");
    } else if (endToken.includes("***DONE***")) {
      return doneMsg.removeAttribute("id", "hidden");
    } else {
      return fetch(`${url}/console/${token}`, { method: "GET" })
        .then(throw_nok)
        .then((response) => response.text())
        .then((result) => {
          let newLine = document.createElement("pre");
          newLine.innerHTML = result;
          scrollContainer.removeChild(scrollContainer.lastChild);
          scrollContainer.appendChild(newLine);
          setTimeout(() => getConsole(token, result), 1000);
          //return getConsole(token, result);
        })
        .catch((error) => console.log("error", error));
    }
  };

  const loginInit = () =>
    form.addEventListener(`submit`, (e) => login(e, "login"));
  const migrateInit = () =>
    migrationButton.addEventListener(`click`, (e) => login(e, "migrate"));
  loginInit();
  migrateInit();
}
