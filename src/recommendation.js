"use strict";

async function requestRecommendation(payload, signal) {
  let response = await fetch("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
  // This operation only calculates a plan; it never places an order or saves data.
  // Some preview servers reject POST before it reaches the Python API.
  if (response.status === 405) {
    response = await fetch(`/api/recommend?${new URLSearchParams(payload)}`, {
      headers: { "Accept": "application/json" },
      cache: "no-store",
      signal,
    });
    if (response.status === 404 || response.status === 405) {
      throw new Error("Error.");
    }
  }
  return readRecommendationResponse(response);
}

async function readRecommendationResponse(response) {
  const body = await response.text();
  if (!body.trim()) {
    throw new Error(`Error.`);
  }
  let result;
  try {
    result = JSON.parse(body);
  } catch {
    throw new Error(`The server returned an invalid response (HTTP ${response.status}). `);
  }
  if (!response.ok) {
    const message = Array.isArray(result?.detail)
      ? result.detail.map(error => error.msg).join("; ") : result?.detail;
    throw new Error(typeof message === "string" ? message : `Recommendation failed (HTTP ${response.status}).`);
  }
  if (!result || !Array.isArray(result.recommended_orders) || !result.recommended_orders.length
      || !Number.isFinite(result.total_cost_nok)
      || result.recommended_orders.some(order => !order || typeof order.week !== "string"
        || !Number.isFinite(order.price_nok_kg) || !Number.isFinite(order.quantity_kg))) {
    throw new Error("The server returned incomplete recommendation data. Restart the backend to load the latest code.");
  }
  return result;
}

async function generateRecommendation() {
  const button = document.querySelector("button[onclick='generateRecommendation()']");
  const status = document.getElementById("result-status");
  const results = document.getElementById("recommendation-results");
  const rows = document.getElementById("recommendation-rows");
  results.hidden = true;
  rows.replaceChildren();
  const raw = ["budget", "quantity", "deadline"].map(id => document.getElementById(id).value.trim());
  const [budget, quantity, deadline] = raw.map(Number);
  if (raw.some(value => !value) || ![budget, quantity, deadline].every(Number.isFinite)
      || budget < 0 || quantity <= 0 || !Number.isInteger(deadline) || deadline < 1 || deadline > 52) {
    status.textContent = "Enter a budget in NOK (zero or greater), a positive quantity in kg, and a deadline of 1-52 weeks.";
    return;
  }
  if (window.location.protocol === "file:") {
    status.textContent = "Start the backend, then open http://127.0.0.1:8000/reccom_eng.html.";
    return;
  }
  button.disabled = true;
  status.textContent = "Calculating recommendation...";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30000);
  try {
    const result = await requestRecommendation(
      { maximum_budget: budget, buyer_demand_kg: quantity, deadline_weeks: deadline },
      controller.signal,
    );
    for (const order of result.recommended_orders) {
      const row = document.createElement("tr");
      for (const value of [order.week, order.price_nok_kg.toFixed(2), order.quantity_kg.toFixed(2)]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      }
      rows.appendChild(row);
    }
    document.getElementById("recommendation-total").textContent = `Total cost: NOK ${result.total_cost_nok.toFixed(2)}`;
    document.getElementById("recommendation-note").textContent = result.simulated_supplier_data
      ? "Simulated supplier quotes and stock. Each row is a purchase allocation; delivery and storage costs are excluded." : "";
    status.textContent = "Recommendation calculated.";
    results.hidden = false;
  } catch (error) {
    status.textContent = error.name === "AbortError" ? "The request timed out. Please try again."
      : error instanceof TypeError ? "Cannot reach the backend. Start it with python -m uvicorn backend:app --reload, then open http://127.0.0.1:8000/reccom_eng.html."
      : error.message;
  } finally {
    clearTimeout(timeout);
    button.disabled = false;
  }
}
