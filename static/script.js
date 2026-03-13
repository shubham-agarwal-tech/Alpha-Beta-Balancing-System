let alphaChart = null;
let betaChart = null;

async function fetchData() {
    try {
        const [marketData, economics, strategies, news] = await Promise.all([
            fetch('/api/market-data').then(res => res.json()),
            fetch('/api/economic-indicators').then(res => res.json()),
            fetch('/api/strategies').then(res => res.json()),
            fetch('/api/news').then(res => res.json())
        ]);

        updatePrices(marketData);
        updateEconomics(economics);
        updateNews(news);
        
        // Update Strategies
        const alpha = strategies.find(s => s.type === 'alpha');
        const beta = strategies.find(s => s.type === 'beta');

        if (alpha) {
            updateStrategyDisplay('alpha', alpha, alphaChart, (chart) => alphaChart = chart);
        }
        if (beta) {
            updateStrategyDisplay('beta', beta, betaChart, (chart) => betaChart = chart);
        }
        
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updatePrices(data) {
    const list = document.getElementById('price-list');
    list.innerHTML = data.map(item => `
        <div class="price-item">
            <span class="price-symbol">${item.symbol}</span>
            <span class="price-value">$${item.price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
        </div>
    `).join('');
}

function updateEconomics(data) {
    const list = document.getElementById('indicators-list');
    list.innerHTML = Object.entries(data).map(([key, val]) => `
        <div class="indicator-item">
            <span class="indicator-val">${val}%</span>
            <span class="indicator-label">${key.replace('_', ' ')}</span>
        </div>
    `).join('');
}

function updateStrategyDisplay(prefix, strategy, chartObj, setChart) {
    // Update Metrics
    const metricsEl = document.getElementById(`${prefix}-metrics`);
    metricsEl.innerHTML = `
        <div class="metric-row">
            <span>Sharpe Ratio:</span>
            <span class="metric-val ${strategy.metrics.sharpe > 1 ? 'positive' : ''}">${strategy.metrics.sharpe.toFixed(2)}</span>
        </div>
        <div class="metric-row">
            <span>Sortino:</span>
            <span>${strategy.metrics.sortino.toFixed(2)}</span>
        </div>
        <div class="metric-row">
            <span>Max DD:</span>
            <span class="negative">${(strategy.metrics.max_drawdown * 100).toFixed(1)}%</span>
        </div>
    `;

    // Update Chart
    const ctx = document.getElementById(`${prefix}Chart`).getContext('2d');
    const labels = strategy.allocation.map(a => a.symbol);
    const weights = strategy.allocation.map(a => a.weight * 100);

    if (chartObj) {
        chartObj.data.labels = labels;
        chartObj.data.datasets[0].data = weights;
        chartObj.update('none');
    } else {
        const newChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: weights,
                    backgroundColor: [
                        '#6366f1', '#a855f7', '#22d3ee', '#f43f5e'
                    ],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Outfit', size: 10 } }
                    }
                }
            }
        });
        setChart(newChart);
    }
}

function updateNews(news) {
    const feed = document.getElementById('news-feed');
    feed.innerHTML = news.map(item => `
        <div class="news-item ${item.sentiment}">
            <span class="news-headline">${item.headline}</span>
            <span class="news-meta">Impact: ${item.impact_score} | ${item.sentiment.toUpperCase()}</span>
        </div>
    `).join('');
}

// Initial fetch and set interval
fetchData();
setInterval(fetchData, 3000);
