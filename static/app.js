// Fetches the stock list from the API and renders it as a table.
// Handles inline editing of an ingredient's quantity and par level.

const stockTableBody = document.getElementById("stock-table-body");
const menuTableBody = document.getElementById("menu-table-body");

async function loadMenu() {
  const response = await fetch("/api/menu");
  const menu = await response.json();
  renderMenu(menu);
}

function renderMenu(menu) {
  menuTableBody.innerHTML = "";
  menu.forEach((item) => {
    const row = document.createElement("tr");
    if (!item.available) {
      row.classList.add("text-muted");
    }

    const availabilityBadge = item.available
      ? '<span class="badge bg-success">Available</span>'
      : '<span class="badge bg-danger">Unavailable</span>';

    const actionCell = item.available
      ? '<button class="btn btn-sm btn-primary order-btn">Order</button>'
      : '<span class="text-muted">-</span>';

    row.innerHTML = `
      <td>${item.dish}</td>
      <td>${item.price}</td>
      <td>${availabilityBadge}</td>
      <td>${actionCell}</td>
    `;

    if (item.available) {
      row.querySelector(".order-btn").addEventListener("click", () => {
        placeOrder(item.dish);
      });
    }

    menuTableBody.appendChild(row);
  });
}

async function placeOrder(dish) {
  const response = await fetch("/api/orders", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dish }),
  });

  if (!response.ok) {
    const error = await response.json();
    alert(`Could not place order: ${formatErrorDetail(error.detail)}`);
    return;
  }

  await loadIngredients();
  await loadMenu();
}
async function loadIngredients() {
  const response = await fetch("/api/ingredients");
  const ingredients = await response.json();
  renderIngredients(ingredients);
}

function renderIngredients(ingredients) {
  stockTableBody.innerHTML = "";
  ingredients.forEach((ingredient) => {
    stockTableBody.appendChild(buildRow(ingredient));
  });
}

function buildRow(ingredient) {
  const row = document.createElement("tr");

  const belowPar = ingredient.qty < ingredient.par;
  const statusBadge = belowPar
    ? '<span class="badge bg-danger">Below par</span>'
    : '<span class="badge bg-success">OK</span>';

  row.innerHTML = `
    <td>${ingredient.name}</td>
    <td class="qty-cell">${ingredient.qty}</td>
    <td>${ingredient.unit}</td>
    <td class="par-cell">${ingredient.par}</td>
    <td class="status-cell">${statusBadge}</td>
    <td><button class="btn btn-sm btn-outline-primary edit-btn">Edit</button></td>
  `;

  row.querySelector(".edit-btn").addEventListener("click", () => {
    startEdit(row, ingredient);
  });

  return row;
}

// Swaps the qty/par cells for input boxes, and the Edit button for
// Save/Cancel, so editing happens in place instead of a separate form.
function startEdit(row, ingredient) {
  const qtyCell = row.querySelector(".qty-cell");
  const parCell = row.querySelector(".par-cell");
  const actionsCell = row.querySelector("td:last-child");

  qtyCell.innerHTML = `<input type="number" step="any" min="0" class="form-control form-control-sm" value="${ingredient.qty}">`;
  parCell.innerHTML = `<input type="number" step="any" min="0" class="form-control form-control-sm" value="${ingredient.par}">`;
  actionsCell.innerHTML = `
    <button class="btn btn-sm btn-success save-btn">Save</button>
    <button class="btn btn-sm btn-secondary cancel-btn">Cancel</button>
  `;

  const qtyInput = qtyCell.querySelector("input");
  const parInput = parCell.querySelector("input");

  actionsCell.querySelector(".save-btn").addEventListener("click", () => {
    saveEdit(ingredient.name, qtyInput.value, parInput.value);
  });

  // Cancel just reloads the real data, discarding whatever was typed.
  actionsCell.querySelector(".cancel-btn").addEventListener("click", loadIngredients);
}

async function saveEdit(name, qtyValue, parValue) {
  const payload = {
    qty: qtyValue === "" ? null : parseFloat(qtyValue),
    par: parValue === "" ? null : parseFloat(parValue),
  };

  const response = await fetch(`/api/ingredients/${encodeURIComponent(name)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json();
    alert(`Could not save: ${formatErrorDetail(error.detail)}`);
    return;
  }
  await loadIngredients();
  await loadMenu();
}


// FastAPI's own validation errors (e.g. negative numbers) come back as a
// list of objects, not a plain string, so this makes both readable.
function formatErrorDetail(detail) {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }
  return "unknown error";
}

loadIngredients();
loadMenu();