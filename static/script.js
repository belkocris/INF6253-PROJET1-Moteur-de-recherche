async function sendQuery() {

    const engine = document.querySelector('input[name="engine"]:checked').value;
    const query = document.getElementById("query").value;

    const resultsDiv = document.getElementById("results");
    const outputDiv = document.getElementById("output");
    const timeDiv = document.getElementById("time");
    const loader = document.getElementById("loader");

    // Reset propre
    resultsDiv.classList.remove("visible");
    resultsDiv.style.display = "none";
    outputDiv.innerHTML = "";
    timeDiv.innerHTML = "";

    // Loader ON
    loader.style.display = "block";

    const response = await fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ engine, query })
    });

    const data = await response.json();

    // Loader OFF
    loader.style.display = "none";

    // Résultat HTML
    outputDiv.innerHTML = data.result;

    // Temps
    timeDiv.innerHTML = `<p><strong>Temps :</strong> ${data.time} ms</p>`;

    // Affichage + animation
    resultsDiv.style.display = "block";
    setTimeout(() => {
        resultsDiv.classList.add("visible");
    }, 10);
}

// === TRI DES TABLEAUX SPARQL ===
document.addEventListener("click", function (e) {
    if (e.target.tagName !== "TH") return;

    const th = e.target;
    const table = th.closest("table");
    const colIndex = Array.from(th.parentNode.children).indexOf(th);
    const rows = Array.from(table.querySelectorAll("tr:nth-child(n+2)"));

    const isAsc = th.classList.contains("sorted-asc");

    // Reset des icônes
    table.querySelectorAll("th").forEach(h => h.classList.remove("sorted-asc", "sorted-desc"));

    // Appliquer la nouvelle direction
    th.classList.add(isAsc ? "sorted-desc" : "sorted-asc");

    rows.sort((a, b) => {
        const A = a.children[colIndex].innerText.toLowerCase();
        const B = b.children[colIndex].innerText.toLowerCase();

        if (!isNaN(A) && !isNaN(B)) {
            return isAsc ? B - A : A - B;
        }
        return isAsc ? B.localeCompare(A) : A.localeCompare(B);
    });

    rows.forEach(r => table.appendChild(r));
});
