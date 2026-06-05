"use strict";
document.addEventListener('DOMContentLoaded', () => {
    let executionCount = 1;
    const executeBtn = document.getElementById('execute-btn');
    const resultsWrapper = document.getElementById('results-output-wrapper');
    const inCount = document.getElementById('in-count');
    const outCount = document.getElementById('out-count');
    const categorySelect = document.getElementById('category-query');
    const projects = document.querySelectorAll('.project-card');
    const resultStatus = document.getElementById('result-status');

    if (!executeBtn) return;

    function executeQuery() {
        inCount.textContent = executionCount;
        outCount.textContent = executionCount;
        executionCount++;

        resultsWrapper.style.opacity = '0';
        resultsWrapper.style.transform = 'translateY(10px)';

        setTimeout(() => {
            const filter = categorySelect.value;
            let count = 0;

            projects.forEach(project => {
                const category = project.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    project.classList.remove('hidden');
                    count++;
                } else {
                    project.classList.add('hidden');
                }
            });

            resultStatus.textContent = `Found ${count} matching objects`;
            
            resultsWrapper.style.opacity = '1';
            resultsWrapper.style.transform = 'translateY(0)';
        }, 300);
    }

    executeBtn.addEventListener('click', executeQuery);

    if (resultsWrapper) {
        resultsWrapper.style.opacity = '1';
        resultsWrapper.style.transform = 'translateY(0)';
    }
});