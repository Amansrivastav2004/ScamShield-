/* ScamShield Analytics Dashboard Script */

let riskChartInstance = null;
let categoryChartInstance = null;

function initDashboardCharts(stats) {
    // 1. Risk Level Distribution Doughnut Chart
    const riskCtx = document.getElementById('riskDistributionChart');
    if (riskCtx && stats.risk_counts) {
        if (riskChartInstance) riskChartInstance.destroy();

        riskChartInstance = new Chart(riskCtx, {
            type: 'doughnut',
            data: {
                labels: ['Likely Safe', 'Needs Verification', 'Suspicious', 'High Risk'],
                datasets: [{
                    data: [
                        stats.risk_counts['LIKELY SAFE'] || 0,
                        stats.risk_counts['NEEDS VERIFICATION'] || 0,
                        stats.risk_counts['SUSPICIOUS'] || 0,
                        stats.risk_counts['HIGH RISK'] || 0
                    ],
                    backgroundColor: ['#10b981', '#f59e0b', '#f97316', '#ef4444'],
                    borderColor: '#111827',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#9ca3af', font: { family: 'Inter', size: 12 } }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Scam Category Breakdown Bar Chart
    const catCtx = document.getElementById('scamCategoryChart');
    if (catCtx && stats.categories) {
        if (categoryChartInstance) categoryChartInstance.destroy();

        const labels = stats.categories.map(c => c.category);
        const counts = stats.categories.map(c => c.count);

        categoryChartInstance = new Chart(catCtx, {
            type: 'bar',
            data: {
                labels: labels.length ? labels : ['No Data'],
                datasets: [{
                    label: 'Scams Analyzed',
                    data: counts.length ? counts : [0],
                    backgroundColor: 'rgba(6, 182, 212, 0.65)',
                    borderColor: '#06b6d4',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#9ca3af', font: { family: 'Inter', size: 11 } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y: {
                        ticks: { color: '#9ca3af', stepSize: 1 },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                }
            }
        });
    }
}

// History Delete API Handler
function deleteScanHistoryItem(scanId) {
    if (!confirm("Are you sure you want to delete this scan from your history?")) return;

    fetch(`/api/history/${scanId}`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast("Scan deleted from history", "success");
            const row = document.getElementById(`scan-row-${scanId}`);
            if (row) row.remove();
            
            // Reload page if empty or update dashboard stats
            if (window.location.pathname === '/history') {
                setTimeout(() => window.location.reload(), 500);
            }
        } else {
            showToast(data.error || "Failed to delete scan", "error");
        }
    })
    .catch(err => showToast("Server error during deletion", "error"));
}
