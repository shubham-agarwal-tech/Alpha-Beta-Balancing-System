async function fetchAPI(endpoint) {
    const response = await fetch(`/api/${endpoint}`);
    return await response.json();
}

let allocationChart, marketChart;

async function initCharts() {
    const marketCtx = document.getElementById('marketDataChart').getContext('2d');
    marketChart = new Chart(marketCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Market Prices',
                data: [],
                borderColor: '#38bdf8',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(56, 189, 248, 0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }
            }
        }
    });

    const allocCtx = document.getElementById('allocationChart').getContext('2d');
    allocationChart = new Chart(allocCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#38bdf8', '#818cf8', '#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Outfit' } } }
            },
            cutout: '70%'
        }
    });
}

async function updateDashboard() {
    try {
        // 1. Market Data & Allocation
        const marketData = await fetchAPI('market-data');
        const regimeBadge = document.getElementById('market_regime'); // Check if ID matches
        const regimeEl = document.getElementById('market-regime');
        if (regimeEl) {
            regimeEl.innerText = marketData.regime.replace('_', ' ');
            regimeEl.style.borderColor = marketData.regime === 'bear' ? '#ef4444' : '#38bdf8';
        }

        // Update Allocation Chart
        const labels = marketData.final_allocation.map(a => a.symbol);
        const weights = marketData.final_allocation.map(a => a.weight * 100);
        allocationChart.data.labels = labels;
        allocationChart.data.datasets[0].data = weights;
        allocationChart.update();

        // 2. Correlation Matrix
        const corrData = await fetchAPI('analytics/correlation');
        renderHeatmap(corrData);

        // 3. Performance Report
        const perfData = await fetchAPI('analytics/performance');
        const perfBody = document.getElementById('performance-body');
        perfBody.innerHTML = perfData.map(p => `
            <tr>
                <td style="font-weight: 600">${p.type === 'alpha' ? 'Alpha Strategy' : 'Beta Strategy'}</td>
                <td><span class="regime-badge" style="font-size: 10px">${p.type}</span></td>
                <td class="${p.return >= 0 ? 'trend-up' : 'trend-down'}">${(p.return * 100).toFixed(2)}%</td>
                <td>${p.sharpe.toFixed(2)}</td>
            </tr>
        `).join('');

        // 4. Update Market Chart (just first symbol for demo)
        const firstAsset = marketData.market_data[0];
        if (firstAsset) {
            const time = new Date().toLocaleTimeString();
            marketChart.data.labels.push(time);
            marketChart.data.datasets[0].data.push(firstAsset.price);
            marketChart.data.datasets[0].label = firstAsset.symbol;
            if (marketChart.data.labels.length > 10) {
                marketChart.data.labels.shift();
                marketChart.data.datasets[0].data.shift();
            }
            marketChart.update();
        }

    } catch (error) {
        console.error("Dashboard update failed:", error);
    }
}

function renderHeatmap(data) {
    const symbols = Object.keys(data);
    const container = document.getElementById('correlation-heatmap');
    const labelContainer = document.getElementById('correlation-labels');
    
    container.style.gridTemplateColumns = `repeat(${symbols.length}, 1fr)`;
    container.innerHTML = '';
    labelContainer.innerHTML = symbols.map(s => `<span>${s}</span>`).join('');

    symbols.forEach(rowSym => {
        symbols.forEach(colSym => {
            const val = data[rowSym][colSym];
            const opacity = Math.abs(val);
            const color = val >= 0 ? `rgba(56, 189, 248, ${opacity})` : `rgba(239, 68, 68, ${opacity})`;
            
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            cell.style.backgroundColor = color;
            cell.innerText = val.toFixed(2);
            cell.title = `${rowSym} vs ${colSym}: ${val.toFixed(4)}`;
            container.appendChild(cell);
        });
    });
}

// Initialize
initCharts();
updateDashboard();
setInterval(updateDashboard, 5000); // Update every 5 seconds
