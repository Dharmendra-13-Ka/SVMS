function login() {

    let username = document.getElementById("username").value.trim();
    let password = document.getElementById("password").value.trim();

    if (username === "" || password === "") {
        document.getElementById("message").innerHTML =
            "Please enter Username and Password";
        return;
    }

    fetch("https://svms-zgsx.onrender.com/login", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            username: username,
            password: password
        })

    })

    .then(response => response.json())

    .then(data => {

     if (data.status === "success") {

    // Login status save
    localStorage.setItem("svms_logged_in", "true");
    localStorage.setItem("svms_username", username);

    // Show success popup
    document.getElementById("successPopup").style.display = "flex";

    // Open dashboard after 1.5 seconds
    setTimeout(function () {

        window.location.href = "index.html";

    }, 1500);

} else {

            document.getElementById("message").innerHTML =
                "Invalid Username or Password";

        }

    })

    .catch(error => {

        console.log(error);

        document.getElementById("message").innerHTML =
            "Server connection error";

    });

}