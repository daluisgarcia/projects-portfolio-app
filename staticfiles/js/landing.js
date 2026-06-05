"use strict";
document.addEventListener('DOMContentLoaded', () => {
    const runBtn = document.getElementById('run-hero');
    const heroOutput = document.getElementById('hero-output');
    
    if (runBtn && heroOutput) {
        runBtn.addEventListener('click', () => {
            runBtn.classList.add('scale-95', 'opacity-70');
            setTimeout(() => {
                runBtn.classList.remove('scale-95', 'opacity-70');
                heroOutput.classList.remove('opacity-0', 'translate-y-4');
                heroOutput.classList.add('opacity-100', 'translate-y-0');
            }, 300);
        });
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('opacity-100', 'translate-x-0');
                entry.target.classList.remove('opacity-0', '-translate-x-4');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.flex.group').forEach(el => {
        el.classList.add('transition-all', 'duration-700', 'opacity-0', '-translate-x-4');
        observer.observe(el);
    });
});