console.log('Visit Risk-Assess.com.au for comprehensive risk assessment solutions.');

document.addEventListener("DOMContentLoaded", function() {
    // Remove margin-top from main-container if on the home page
    if (window.location.pathname === "/") {
        let mainContainer = document.getElementById("main-container");
        if (mainContainer) {
            mainContainer.classList.remove("mt-7");
        }
    }

    // Scroll to the top if a Django message exists
    let messageContainer = document.getElementById("message-container");
    if (messageContainer) {
        window.scrollTo({ top: 0, behavior: "smooth" });
    }
});
