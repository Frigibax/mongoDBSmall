const chartInstances = {};

// Color palette for each index for a vibrant UI
const indexColors = {
    "S&P 500": "#38bdf8",     // Sky Blue
    "Dow Jones": "#818cf8",   // Indigo
    "NASDAQ": "#c084fc",      // Purple
    "FTSE 100": "#f472b6",    // Pink
    "Nikkei 225": "#fb7185",  // Rose
    "BSE SENSEX": "#facc15",  // Yellow
    "NIFTY 50": "#4ade80"     // Green
};

// Fetch latest history from Flask backend
async function fetchHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Error fetching data:", error);
        return null;
    }
}

// Create HTML scaffold for a new Chart card
function createCard(indexName, latestPrice) {
    const container = document.getElementById('charts-container');
    const safeId = indexName.replace(/[\s&]+/g, '-');
    
    const card = document.createElement('div');
    card.className = 'chart-card';
    
    // Header section with Title and Live Price
    const header = document.createElement('div');
    header.className = 'chart-header';
    header.innerHTML = `
        <div class="chart-title">${indexName}</div>
        <div class="current-price" id="price-${safeId}">
            ${parseFloat(latestPrice).toFixed(2)}
        </div>
    `;
    
    // Chart Canvas Container
    const canvasContainer = document.createElement('div');
    canvasContainer.className = 'canvas-container';
    
    const canvas = document.createElement('canvas');
    canvas.id = `chart-${safeId}`;
    
    canvasContainer.appendChild(canvas);
    card.appendChild(header);
    card.appendChild(canvasContainer);
    container.appendChild(card);
    
    return canvas;
}

// Initialize a new Chart.js instance with gradient and settings
function initChart(canvas, indexName, historicalData) {
    const ctx = canvas.getContext('2d');
    const color = indexColors[indexName] || "#ffffff";
    
    const labels = historicalData.map(d => d.time);
    const prices = historicalData.map(d => d.price);
    
    // Beautiful transparent gradient fill under the line
    const gradient = ctx.createLinearGradient(0, 0, 0, 220);
    gradient.addColorStop(0, `${color}66`); // 40% opacity
    gradient.addColorStop(1, `${color}00`); // 0% opacity
    
    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: indexName,
                data: prices,
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 2.5,
                pointRadius: 0,           // Hide points by default for sleekness
                pointHoverRadius: 6,      // Show glowing point on hover
                tension: 0.4,             // Smooth curves
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#fff',
                    bodyColor: color,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            },
            scales: {
                x: {
                    display: false // Hide x-axis labels for a cleaner look
                },
                y: {
                    display: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: { family: 'Inter', size: 11 }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Main logic loop
async function updateDashboard() {
    const data = await fetchHistory();
    if (!data) return;
    
    for (const [indexName, history] of Object.entries(data)) {
        if (history.length === 0) continue;
        
        const safeId = indexName.replace(/[\s&]+/g, '-');
        const latestPrice = history[history.length - 1].price;
        
        // 1. Create the chart if it doesn't exist yet
        if (!chartInstances[indexName]) {
            const canvas = createCard(indexName, latestPrice);
            chartInstances[indexName] = initChart(canvas, indexName, history);
        } else {
            // 2. Update existing chart with new data array
            const chart = chartInstances[indexName];
            chart.data.labels = history.map(d => d.time);
            chart.data.datasets[0].data = history.map(d => d.price);
            chart.update('none'); // Update without full layout animation to prevent flickering
            
            // 3. Update the price text safely, with visual flash
            const priceEl = document.getElementById(`price-${safeId}`);
            if (priceEl) {
                const oldPrice = parseFloat(priceEl.innerText);
                const newPrice = parseFloat(latestPrice);
                priceEl.innerText = newPrice.toFixed(2);
                
                // Add flash effect based on direction
                if(newPrice > oldPrice) {
                    priceEl.style.color = '#4ade80'; // flash green for up
                } else if(newPrice < oldPrice) {
                    priceEl.style.color = '#fb7185'; // flash red for down
                }
                
                // Return to default accent color after flash
                setTimeout(() => {
                    priceEl.style.color = 'var(--accent)'; 
                }, 1200);
            }
        }
    }
}

// Initial load
updateDashboard();

// Poll backend every 3 seconds
setInterval(updateDashboard, 3000);
