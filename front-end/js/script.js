{
  const userName = document.querySelector("#usernameInput");
  const password = document.querySelector("#passwordInput");
  const form = document.querySelector("#form");
  const dots = document.querySelectorAll(".dot");
  const migrationButton = document.querySelector(".migrate-button");
  const scrollContainer = document.querySelector(".scroll-container");
  const doneMsg = document.querySelector(".done-msg");
  const url = "https://keeper1pmigration.free.beeceptor.com";
  let myHeaders = new Headers();
  let urlencoded = new URLSearchParams();

  const login = async (e, endpoint) => {
    if (endpoint === "migrate") migrationButton.setAttribute("id", "hidden");
    let counter = endpoint === "login" ? 1 : 2;
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
    await fetch(`${url}/${endpoint}`, requestOptions)
      .then((response) => response.text())
      .then((hash) => {
        dots[counter].setAttribute("id", "in-progress");
        return getConsole(hash, "");
      })
      .catch((error) =>
        alert("Please recheck username and password, then try again")
      );
  };

  const sleep = (milliseconds) => {
    const date = Date.now();
    let currentDate = null;
    do {
      currentDate = Date.now();
    } while (currentDate - date < milliseconds);
  };

  const getConsole = async (token, endToken) => {
    form.setAttribute("id", "hidden");
    scrollContainer.removeAttribute("id", "hidden");
    // Auto scroll
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
    if (endToken.includes("CLEAR")) {
      return migrationButton.removeAttribute("id", "hidden");
    } else if (endToken.includes("DONE")) {
      return doneMsg.removeAttribute("id", "hidden");
    } else {
      return fetch(`${url}/console/${token}`, { method: "GET" })
        .then((response) => response.text())
        .then((result) => {
          let newLine = document.createElement("p");
          newLine.innerHTML = result;
          scrollContainer.appendChild(newLine);
          sleep(1000);
          return getConsole(token, result);
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
