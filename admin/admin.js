const API_BASE = "http://localhost:8000";
let token = null;
const loginForm = document.getElementById("login-form");
const adminPanel = document.getElementById("admin-panel");
const uploadForm = document.getElementById("upload-form");
const messageDiv = document.getElementById("message");

// Show message function
function showMessage(message, type = "error") {
  messageDiv.textContent = message;
  messageDiv.className = `message ${type}`;
  messageDiv.style.display = "block";

  setTimeout(() => {
    messageDiv.style.display = "none";
  }, 5000);
}

// Image preview functionality
const coverInput = document.getElementById("cover");
const imagePreview = document.getElementById("image-preview");

coverInput.addEventListener("change", function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      imagePreview.innerHTML = `<img src="${e.target.result}" class="preview-image" alt="Preview">`;
    };
    reader.readAsDataURL(file);
  } else {
    imagePreview.innerHTML = "";
  }
});

// Login form handler
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(loginForm);

  try {
    const res = await fetch(`${API_BASE}/admin/login`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      showMessage("Login failed. Please check your credentials.");
      return;
    }

    const data = await res.json();
    token = data.access_token;
    localStorage.setItem("admin_token", token);
    loginForm.parentElement.style.display = "none";
    adminPanel.style.display = "block";
    loadAdminCatalogs();
    showMessage("Login successful!", "success");
  } catch (error) {
    showMessage("Login error. Please try again.");
    console.error("Login error:", error);
  }
});

// Upload form handler
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(uploadForm);

  try {
    const res = await fetch(`${API_BASE}/protected/catalogs/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!res.ok) {
      const errorData = await res.json();
      showMessage(`Upload failed: ${errorData.detail || "Unknown error"}`);
      return;
    }

    showMessage("Catalog uploaded successfully!", "success");
    uploadForm.reset();
    imagePreview.innerHTML = "";
    loadAdminCatalogs();
  } catch (error) {
    showMessage("Upload error. Please try again.");
    console.error("Upload error:", error);
  }
});

// Load catalogs for admin
async function loadAdminCatalogs() {
  try {
    const res = await fetch(`${API_BASE}/catalogs/`);
    if (!res.ok) {
      showMessage("Failed to load catalogs");
      return;
    }

    const items = await res.json();
    const list = document.getElementById("admin-list");
    list.innerHTML = "";

    if (items.length === 0) {
      list.innerHTML = "<p>No catalogs found. Upload one to get started.</p>";
      return;
    }

    items.forEach((it) => {
      const div = document.createElement("div");
      div.className = "catalog-item";
      div.innerHTML = `
                        <img src="${
                          it.cover_image.startsWith("http")
                            ? it.cover_image
                            : API_BASE + it.cover_image
                        }" class="catalog-image" alt="${it.title}">
                        <div>
                            <strong>${it.title}</strong> 
                            <div>${it.description || "No description"}</div>
                        </div>
                        <button data-id='${it.id}' class='del'>Delete</button>
                    `;
      list.appendChild(div);
    });

    // Add delete event listeners
    document.querySelectorAll(".del").forEach((btn) =>
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        if (!confirm("Are you sure you want to delete this catalog?")) return;

        try {
          const res = await fetch(`${API_BASE}/protected/catalogs/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` },
          });

          if (res.ok) {
            showMessage("Catalog deleted successfully!", "success");
            loadAdminCatalogs();
          } else {
            showMessage("Delete failed");
          }
        } catch (error) {
          showMessage("Delete error. Please try again.");
          console.error("Delete error:", error);
        }
      })
    );
  } catch (error) {
    showMessage("Error loading catalogs");
    console.error("Load catalogs error:", error);
  }
}

// Check for existing token on page load
const savedToken = localStorage.getItem("admin_token");
if (savedToken) {
  token = savedToken;
  document.querySelector(".login-container").style.display = "none";
  adminPanel.style.display = "block";
  loadAdminCatalogs();
}
