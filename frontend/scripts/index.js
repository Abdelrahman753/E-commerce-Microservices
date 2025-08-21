// نخلي الـ API_URL يمر عبر الـ Nginx Gateway
const API_URL = "/api/products"; // بدل localhost:5003

const productsContainer = document.getElementById("products-container");
const loadingElement = document.getElementById("loading");
const errorElement = document.getElementById("error");
const retryButton = document.getElementById("retry-btn");
const searchInput = document.getElementById("search-input");
const searchButton = document.getElementById("search-btn");
const categorySelect = document.getElementById("category-select");

async function fetchProducts(category = "", search = "") {
    loadingElement.style.display = "block";
    errorElement.style.display = "none";
    productsContainer.style.display = "none";

    try {
        let url = new URL(API_URL, window.location.origin);
        url.searchParams.set("per_page", 12);
        if (category) url.searchParams.set("category", category);

        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch products");

        const data = await res.json();
        let products = data.products || [];

        // تصفية نتائج البحث محليًا إذا فيه كلمة بحث
        if (search) {
            const term = search.toLowerCase();
            products = products.filter(p =>
                (p.name && p.name.toLowerCase().includes(term)) ||
                (p.description && p.description.toLowerCase().includes(term))
            );
        }

        displayProducts(products);
    } catch (err) {
        console.error("Error fetching products:", err);
        errorElement.style.display = "block";
    } finally {
        loadingElement.style.display = "none";
    }
}

function displayProducts(products) {
    productsContainer.innerHTML = "";

    if (!products.length) {
        productsContainer.innerHTML = `<p>No products found.</p>`;
    } else {
        products.forEach(product => {
            const productCard = document.createElement("div");
            productCard.classList.add("product-card");

            productCard.innerHTML = `
                <img src="${product.image_url || 'placeholder.jpg'}" alt="${product.name || 'Product'}">
                <h3>${product.name || 'Unnamed Product'}</h3>
                <p>${product.description || ''}</p>
                <p class="price">$${product.price ? product.price.toFixed(2) : '0.00'}</p>
                <button class="add-to-cart" data-id="${product.id || ''}">Add to Cart</button>
            `;

            productsContainer.appendChild(productCard);
        });
    }

    productsContainer.style.display = "grid";
}

// Events
retryButton.addEventListener("click", () => fetchProducts());
searchButton.addEventListener("click", () => {
    fetchProducts(categorySelect.value, searchInput.value);
});
categorySelect.addEventListener("change", () => {
    fetchProducts(categorySelect.value, searchInput.value);
});

// Initial Load
fetchProducts();

// إدارة زر تسجيل الدخول / تسجيل الخروج
document.addEventListener("DOMContentLoaded", () => {
    const authBtn = document.getElementById("auth-btn");

    function updateAuthBtn() {
        const currentUser = JSON.parse(localStorage.getItem("currentUser"));
        if (currentUser && currentUser.access_token) {
            authBtn.textContent = "Logout";
            authBtn.classList.add("logout");
        } else {
            authBtn.textContent = "Login";
            authBtn.classList.remove("logout");
        }
    }

    updateAuthBtn();

    authBtn.addEventListener("click", () => {
        const currentUser = JSON.parse(localStorage.getItem("currentUser"));
        if (currentUser && currentUser.access_token) {
            localStorage.removeItem("currentUser");
            window.location.href = "login.html";
        } else {
            window.location.href = "login.html";
        }
    });
});
