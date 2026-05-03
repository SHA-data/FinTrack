document.addEventListener('DOMContentLoaded', () => {

    /* ==========================================================================
       Flash Messages Auto-hide & Dismiss
       ========================================================================== */
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        // Auto-dismiss after 4 seconds
        const timeout = setTimeout(() => {
            if(flash.parentElement) {
                flash.remove();
            }
        }, 4000);

        // Manual dismiss
        const dismissBtn = flash.querySelector('.flash__dismiss');
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                clearTimeout(timeout);
                flash.remove();
            });
        }
    });

    /* ==========================================================================
       Navbar Hamburger Toggle
       ========================================================================== */
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('is-open');
        });
    }

    /* ==========================================================================
       Password Show/Hide Toggle
       ========================================================================== */
    const pwToggles = document.querySelectorAll('.password-toggle');
    pwToggles.forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const input = toggle.previousElementSibling;
            if (input && input.tagName === 'INPUT') {
                if (input.type === 'password') {
                    input.type = 'text';
                    toggle.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22"/></svg>'; // Eye-off
                } else {
                    input.type = 'password';
                    toggle.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>'; // Eye
                }
            }
        });
    });

    /* ==========================================================================
       Password Strength Indicator
       ========================================================================== */
    const pwInput = document.getElementById('register-password');
    const pwBar = document.getElementById('pw-strength-bar');
    if (pwInput && pwBar) {
        pwInput.addEventListener('input', () => {
            const val = pwInput.value;
            let strength = 0;
            if (val.length > 0) strength += 25;
            if (val.length >= 8) strength += 25;
            if (/[A-Z]/.test(val) && /[a-z]/.test(val)) strength += 25;
            if (/[0-9!@#$%^&*]/.test(val)) strength += 25;

            pwBar.style.width = strength + '%';

            if (strength <= 25) {
                pwBar.style.backgroundColor = '#DC2626'; // Red
            } else if (strength <= 75) {
                pwBar.style.backgroundColor = '#F59E0B'; // Amber
            } else {
                pwBar.style.backgroundColor = '#16A34A'; // Green
            }
        });
    }

    /* ==========================================================================
       Transaction Category Filtering
       ========================================================================== */
    const txTypeSelect = document.getElementById('tx_type');
    const txCatSelect = document.getElementById('category_id');
    if (txTypeSelect && txCatSelect) {
        const filterCategories = () => {
            const selectedType = txTypeSelect.value.toLowerCase();
            const options = txCatSelect.querySelectorAll('option');
            let firstVisible = null;
            
            options.forEach(opt => {
                if (opt.value === "") return; // Skip placeholder if any
                const type = opt.getAttribute('data-type');
                if (type === selectedType) {
                    opt.style.display = '';
                    if (!firstVisible) firstVisible = opt;
                } else {
                    opt.style.display = 'none';
                }
            });

            // Automatically select first visible valid option
            if (firstVisible) {
                txCatSelect.value = firstVisible.value;
            }
        };

        txTypeSelect.addEventListener('change', filterCategories);
        // Initial run
        filterCategories();
    }

    /* ==========================================================================
       Submit Button Loading State
       ========================================================================== */
    const formsWithLoading = document.querySelectorAll('form[data-loading]');
    formsWithLoading.forEach(form => {
        form.addEventListener('submit', () => {
            const btn = form.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.textContent = form.getAttribute('data-loading-text') || 'Loading...';
                btn.style.opacity = '0.7';
            }
        });
    });

    /* ==========================================================================
       Chart.js Initialization
       ========================================================================== */
    // Helper to extract JSON from script tag
    const getJSON = (id) => {
        const el = document.getElementById(id);
        if (el) {
            try {
                return JSON.parse(el.textContent);
            } catch(e) {
                console.error("Failed to parse JSON for chart", e);
                return null;
            }
        }
        return null;
    };

    // Chart colors palette
    const chartColors = [
        '#4F46E5', '#16A34A', '#F59E0B', '#DC2626', 
        '#06B6D4', '#8B5CF6', '#EC4899', '#64748B'
    ];

    // Donut Chart - Category Breakdown
    const catCanvas = document.getElementById('categoryChart');
    const catData = getJSON('categoryBreakdownData');
    if (catCanvas && catData && catData.length > 0) {
        const labels = catData.map(d => d.category);
        const values = catData.map(d => d.total);
        const bgColors = labels.map((_, i) => chartColors[i % chartColors.length]);

        new Chart(catCanvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: bgColors,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: '70%',
                plugins: {
                    legend: { display: false }, // Custom legend used
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) label += ': ';
                                if (context.parsed !== null) {
                                    // Basic formatting, real currency filter is on backend
                                    label += 'Rs. ' + context.parsed.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });

        // Render custom legend
        const legendContainer = document.getElementById('categoryLegend');
        if (legendContainer) {
            let legendHTML = '';
            catData.forEach((d, i) => {
                const color = chartColors[i % chartColors.length];
                legendHTML += `
                    <div class="legend-item">
                        <span class="legend-color" style="background-color: ${color}"></span>
                        <span>${d.category}: <strong>Rs. ${d.total.toFixed(2)}</strong></span>
                    </div>
                `;
            });
            legendContainer.innerHTML = legendHTML;
        }
    }

    // Bar Chart - Monthly Trend
    const monthlyCanvas = document.getElementById('monthlyChart');
    const monthlyData = getJSON('monthlySummaryData');
    if (monthlyCanvas && monthlyData && monthlyData.length > 0) {
        // Reverse if data comes newest first, to show chronological order left-to-right
        const chronologicalData = [...monthlyData].reverse();
        
        const labels = chronologicalData.map(d => d.month);
        const incomes = chronologicalData.map(d => d.income);
        const expenses = chronologicalData.map(d => d.expense);

        new Chart(monthlyCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Income',
                        data: incomes,
                        backgroundColor: '#16A34A',
                        borderRadius: 4
                    },
                    {
                        label: 'Expense',
                        data: expenses,
                        backgroundColor: '#DC2626',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#E2DFD8' }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            boxWidth: 8
                        }
                    }
                }
            }
        });
    }

});
