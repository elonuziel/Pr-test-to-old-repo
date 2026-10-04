document.addEventListener('DOMContentLoaded', () => {
    let allProducts = [];
    let currentStore = 'all';
    let currentCategory = 'all';
    let searchQuery = '';
    let currentSort = 'price-asc';
    let onlyInStock = true;

    // DOM Elements
    const productsGrid = document.getElementById('productsGrid');
    const emptyState = document.getElementById('emptyState');
    const resultsCount = document.getElementById('resultsCount');
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    const sortSelect = document.getElementById('sortSelect');
    const stockFilter = document.getElementById('stockFilter');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    const statTotalCount = document.getElementById('statTotalCount');
    const statLastUpdated = document.getElementById('statLastUpdated');

    // Fetch scraped product data
    async function fetchProducts() {
        try {
            const res = await fetch('data/products.json');
            if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            const data = await res.json();
            allProducts = data.products || [];

            if (statTotalCount) statTotalCount.textContent = data.total_count || allProducts.length;
            if (statLastUpdated) statLastUpdated.textContent = data.last_updated || 'היום';

            render();
        } catch (err) {
            console.error('Error loading products JSON:', err);
            productsGrid.innerHTML = `
                <div class="empty-state" style="grid-column: 1 / -1;">
                    <div class="empty-icon">⚠️</div>
                    <h3>שגיאה בטעינת הנתונים</h3>
                    <p>לא ניתן היה לטעון את רשימת המוצרים. אנא ודא שקובץ הנתונים קיים.</p>
                </div>
            `;
        }
    }

    // Smart category check function
    function productMatchesCategory(p, cat) {
        if (cat === 'all') return true;

        // If product has categories array from smart auto-categorization
        if (p.categories && Array.isArray(p.categories)) {
            return p.categories.includes(cat);
        }

        // Fallback matching logic
        const title = p.title.toLowerCase();
        const isMopping = p.is_mopping || ['שוטף', 'מקרצף', 'mop', 'wash', 'omni', 'combo', 'station', 'freo', 'floor3'].some(k => title.includes(k));
        const isManual = p.is_manual || p.type === 'handheld' || ['אלחוטי', 'ידני', 'מוט', 'stick', 'cordless', 'handheld', 'g10', 'g11', 'z30', 'h13', 'h14', 'h15'].some(k => title.includes(k));
        const isRobot = p.is_robot || p.type === 'robot' || ['רובוט', 'robot'].some(k => title.includes(k));

        if (cat === 'cleaners') return !isMopping;
        if (cat === 'mopping') return isMopping;
        if (cat === 'manual') return isManual;
        if (cat === 'robot') return isRobot;

        return true;
    }

    // Filter & Sort logic
    function getFilteredProducts() {
        return allProducts.filter(p => {
            // Store filter
            if (currentStore !== 'all' && p.store !== currentStore) return false;

            // Smart Category filter
            if (!productMatchesCategory(p, currentCategory)) return false;

            // Stock filter
            if (onlyInStock && !p.in_stock) return false;

            // Search query filter
            if (searchQuery.trim() !== '') {
                const q = searchQuery.trim().toLowerCase();
                const titleMatch = p.title.toLowerCase().includes(q);
                const storeMatch = p.store.toLowerCase().includes(q);
                if (!titleMatch && !storeMatch) return false;
            }

            return true;
        }).sort((a, b) => {
            if (currentSort === 'price-asc') {
                const priceA = a.price === 0 ? 999999 : a.price;
                const priceB = b.price === 0 ? 999999 : b.price;
                return priceA - priceB;
            } else if (currentSort === 'price-desc') {
                return b.price - a.price;
            } else if (currentSort === 'title-asc') {
                return a.title.localeCompare(b.title, 'he');
            }
            return 0;
        });
    }

    // Render cards
    function render() {
        const filtered = getFilteredProducts();
        
        resultsCount.textContent = `${filtered.length} מוצרים`;
        
        if (filtered.length === 0) {
            productsGrid.innerHTML = '';
            emptyState.hidden = false;
            return;
        }

        emptyState.hidden = true;
        
        productsGrid.innerHTML = filtered.map(p => {
            const storeBadgeClass = `badge-store-${p.store.toLowerCase().replace('-', '')}`;

            // Generate smart badges
            let featureBadge = '';
            if (p.is_mopping || (p.categories && p.categories.includes('mopping'))) {
                featureBadge = '<span class="badge badge-type" style="background:#0284c7;color:#fff;">🧼 שואב שוטף</span>';
            } else {
                featureBadge = '<span class="badge badge-type" style="background:#475569;color:#fff;">🧹 שואב בלבד</span>';
            }

            let typeBadge = '';
            if (p.type === 'robot' || (p.categories && p.categories.includes('robot'))) {
                typeBadge = '<span class="badge badge-type">🤖 רובוטי</span>';
            } else {
                typeBadge = '<span class="badge badge-type">🔋 אלחוטי</span>';
            }

            const defaultImg = 'https://via.placeholder.com/300x225/ffffff/cbd5e1?text=אין+תמונה';
            const imgUrl = p.image || defaultImg;
            const stockBadge = p.in_stock 
                ? '<span class="badge-stock in-stock">במלאי</span>' 
                : '<span class="badge-stock out-of-stock">אזל מהמלאי</span>';

            const priceDisplay = p.price > 0 
                ? `<div class="price-container"><span class="price-label">מחיר עודפים</span><span class="price-val">${p.price_formatted}</span></div>` 
                : `<div class="price-container"><span class="price-label">מחיר</span><span class="price-na">צפה בחנות</span></div>`;

            return `
                <article class="product-card" id="${p.id}">
                    <div class="card-image-wrapper">
                        ${stockBadge}
                        <div class="card-badges">
                            <span class="badge ${storeBadgeClass}">${p.store}</span>
                        </div>
                        <img src="${imgUrl}" alt="${p.title}" loading="lazy" onerror="this.onerror=null;this.src='${defaultImg}';">
                        <div style="position: absolute; bottom: 8px; right: 8px; display: flex; gap: 4px; flex-wrap: wrap;">
                            ${featureBadge}
                            ${typeBadge}
                        </div>
                    </div>
                    <div class="card-body">
                        <h3 class="card-title" title="${p.title}">${p.title}</h3>
                        <div class="card-footer">
                            ${priceDisplay}
                            <a href="${p.url}" target="_blank" rel="noopener noreferrer" class="btn-buy">
                                לצפייה בחנות ↗
                            </a>
                        </div>
                    </div>
                </article>
            `;
        }).join('');
    }

    // Event Listeners
    // Store Filter Pills
    const storeFiltersEl = document.getElementById('storeFilters');
    if (storeFiltersEl) {
        storeFiltersEl.addEventListener('click', (e) => {
            if (e.target.classList.contains('pill')) {
                document.querySelectorAll('#storeFilters .pill').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                currentStore = e.target.dataset.store;
                render();
            }
        });
    }

    // Category Filter Pills
    const categoryFiltersEl = document.getElementById('categoryFilters');
    if (categoryFiltersEl) {
        categoryFiltersEl.addEventListener('click', (e) => {
            if (e.target.classList.contains('pill')) {
                document.querySelectorAll('#categoryFilters .pill').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                currentCategory = e.target.dataset.cat;
                render();
            }
        });
    }

    // Search Input
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        clearSearch.hidden = searchQuery.trim() === '';
        render();
    });

    clearSearch.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        clearSearch.hidden = true;
        render();
    });

    // Sort Select
    sortSelect.addEventListener('change', (e) => {
        currentSort = e.target.value;
        render();
    });

    // Stock Filter Toggle
    stockFilter.addEventListener('change', (e) => {
        onlyInStock = e.target.checked;
        render();
    });

    // Reset Filters Button
    resetFiltersBtn.addEventListener('click', () => {
        currentStore = 'all';
        currentCategory = 'all';
        searchQuery = '';
        currentSort = 'price-asc';
        onlyInStock = true;

        searchInput.value = '';
        clearSearch.hidden = true;
        sortSelect.value = 'price-asc';
        stockFilter.checked = true;

        document.querySelectorAll('#storeFilters .pill').forEach(btn => btn.classList.toggle('active', btn.dataset.store === 'all'));
        document.querySelectorAll('#categoryFilters .pill').forEach(btn => btn.classList.toggle('active', btn.dataset.cat === 'all'));

        render();
    });

    // Initial fetch
    fetchProducts();
});
