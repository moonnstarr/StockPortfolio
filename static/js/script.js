// AJAX for Add Stock Form
document.getElementById('addStockForm').onsubmit = async (e) => {
    e.preventDefault();
    let formData = new FormData(e.target);
    await fetch('/add_stock', { method: 'POST', body: formData });
    location.reload();  // Reloads page to show updated stock list
};

// AJAX for Remove Stock Form
document.getElementById('deleteStockForm').onsubmit = async (e) => {
    e.preventDefault();
    let formData = new FormData(e.target);
    await fetch('/delete_stock', { method: 'POST', body: formData });
    location.reload();
};
