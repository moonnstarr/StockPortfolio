// Chart.js script to render portfolio overview chart
const ctx = document.getElementById('portfolioChart').getContext('2d');
const totalPortfolioValue = {{ portfolio.total_value }};
const totalGainLoss = {{ portfolio.total_gain_loss }};

const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Total Portfolio Value', 'Total Gain/Loss'],
        datasets: [{
            label: 'Amount in USD',
            data: [totalPortfolioValue, totalGainLoss],
            backgroundColor: [
                'rgba(75, 192, 192, 0.2)',
                'rgba(255, 99, 132, 0.2)'
            ],
            borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(255, 99, 132, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Amount (USD)'
                }
            }
        }
    }
});
