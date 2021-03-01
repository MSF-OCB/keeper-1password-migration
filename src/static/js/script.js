{
  const userName = document.querySelector("#usernameInput");
  const password = document.querySelector("#passwordInput");
  const form = document.querySelector("#form");
  const dots = document.querySelectorAll(".dot");
  const migrationButton = document.querySelector(".migrate-button");
  const finishButton = document.querySelector(".finish-button");
  const scrollContainer = document.querySelector(".scroll-container");
  const doneMsg = document.querySelector(".done-msg");
  const loginErrorMsg = document.querySelector(".login-error-msg");
  const userCreatedMsg = document.querySelector(".user-created-msg");
  const accountMigratedMsg = document.querySelector(".account-migrated-msg");
  const url = "";

  function throw_nok(response) {
    if( ! response.ok) throw Error(response.text())
    return response;
  }

  const login = async (e, endpoint) => {
    if (endpoint === "migrate") migrationButton.classList.add("hidden");
    if (endpoint === "confirm") confirmButton.classList.add("hidden");
    let counter = ["dummy", "login", "migrate", "finish"].indexOf(endpoint);
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
    form.classList.add("hidden");
    scrollContainer.classList.remove("hidden");
    // Auto scroll
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
    if (endToken.includes("***ALL_CLEAR***")) {

      return migrationButton.classList.remove("hidden");

    } else if (endToken.includes("***NO_LOGIN***")) {

      return loginErrorMsg.classList.remove("hidden");

    } else if (endToken.includes("***ACCOUNT_MIGRATED***")) {

      userCreatedMsg.classList.add("hidden");

      return accountMigratedMsg.classList.remove("hidden");

    } else if (endToken.includes("***DONE***")) {

      accountMigratedMsg.classList.add("hidden");

      return doneMsg.classList.remove("hidden");

    } else {

      /* this message appears during the migration, not at the end of it */
      if (endToken.includes("***USER_CREATED***")) {
          userCreatedMsg.classList.remove("hidden");
      }

      return fetch(`${url}/console/${token}`, { method: "GET" })
        .then(throw_nok)
        .then((response) => response.text())
        .then((result) => {
          let newLine = document.createElement("pre");
          newLine.innerHTML = result;
          scrollContainer.removeChild(scrollContainer.lastChild);
          scrollContainer.appendChild(newLine);
          setTimeout(() => getConsole(token, result), 1000);
        })
        .catch((error) => console.log("error", error));
    }
  };

  const loginInit = () =>
    form.addEventListener(`submit`, (e) => login(e, "login"));
  const migrateInit = () =>
    migrationButton.addEventListener(`click`, (e) => login(e, "migrate"));
  const finishInit = () =>
    finishButton.addEventListener(`click`, (e) => login(e, "finish"));
  loginInit();
  migrateInit();
  finishInit();
}
