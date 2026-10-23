// Mejora progresiva: gráficos y filtro de casos. Sin JavaScript, las tablas equivalentes siguen visibles.
(function () {
  const COLORS = { PASS: "#1a7f37", FLAKY: "#9a6700", FAIL: "#cf222e", BLOCKED: "#8250df" };

  async function renderChart(canvas) {
    if (canvas.dataset.rendered || typeof Chart === "undefined") return;
    canvas.dataset.rendered = "1";
    let data;
    try {
      const response = await fetch(canvas.dataset.src);
      if (!response.ok) return;
      data = await response.json();
    } catch (error) {
      return;
    }
    if (canvas.dataset.chart === "trend") {
      new Chart(canvas, {
        type: "bar",
        data: {
          labels: data.labels,
          datasets: Object.entries(data.series).map(([label, values]) => ({
            label, data: values, backgroundColor: COLORS[label] || "#57606a", stack: "estado",
          })),
        },
        options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } },
      });
    } else if (canvas.dataset.chart === "perf") {
      new Chart(canvas, {
        type: "line",
        data: { datasets: data.series.map((s) => ({ label: s.label, data: s.points, tension: 0.2 })) },
        options: {
          responsive: true, parsing: { xAxisKey: "x", yAxisKey: "y" },
          scales: { x: { type: "category" }, y: { title: { display: true, text: "mediana (ms)" } } },
        },
      });
    }
  }

  function setupFilter(input) {
    if (input.dataset.ready) return;
    input.dataset.ready = "1";
    input.addEventListener("input", () => {
      const term = input.value.trim().toLowerCase();
      document.querySelectorAll(".md-typeset table tbody tr").forEach((row) => {
        row.style.display = !term || row.textContent.toLowerCase().includes(term) ? "" : "none";
      });
    });
  }

  function init() {
    document.querySelectorAll("canvas.qa-chart").forEach(renderChart);
    document.querySelectorAll("input.qa-filter").forEach(setupFilter);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init); // compatible con la navegación instantánea de Material
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
