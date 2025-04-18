document.getElementById("registerForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let formData = new FormData(this);
    
    let response = await fetch("/register", {
        method: "POST",
        body: formData
    });

    let result = await response.json();
    alert(result.message);

    if (result.status === "success") {
        fetchUsers(); // Refresh user list
    }
});

// Fetch registered users
async function fetchUsers() {
    let response = await fetch("/users");
    let users = await response.json();
    let userList = document.getElementById("userList");
    
    userList.innerHTML = "";
    for (let name in users) {
        let li = document.createElement("li");
        li.textContent = `${name} - ${users[name]}`;
        userList.appendChild(li);
    }
}

// Load users on page load
fetchUsers();
