/* ========================================
   ROAD — Netflix/Spotify Interactive JS
   ======================================== */

document.addEventListener('DOMContentLoaded', () => {

    // ---- Navbar scroll ----
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    }, { passive: true });

    // ---- Mobile menu ----
    const toggle = document.getElementById('mobileToggle');
    const links = document.getElementById('navLinks');
    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
    });
    links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
        links.classList.remove('open');
        toggle.textContent = '☰';
    }));

    // ---- Smooth scroll ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                window.scrollTo({ top: target.offsetTop - 70, behavior: 'smooth' });
            }
        });
    });

    // ---- Scroll reveal ----
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

    // ---- Pipeline — Spotify-style player ----
    const nodes = document.querySelectorAll('.pipeline-node');
    const infoPanel = document.getElementById('pipelineInfo');

    const pipelineData = [
        {
            icon: '📹', title: 'Object Detection — YOLOv8',
            desc: 'The YOLOv8 nano model performs real-time inference on each frame, detecting 6 road-relevant classes: <strong>person, bicycle, car, motorcycle, bus, and truck</strong>. Each detection includes bounding box coordinates, class label, confidence score, center point, and area. A 0.5 confidence threshold filters low-quality predictions.',
            tags: ['YOLOv8 Nano', '6 Classes', '0.5 Confidence', 'COCO Dataset']
        },
        {
            icon: '🔗', title: 'Multi-Object Tracking',
            desc: 'The centroid tracker matches objects across frames using <strong>Euclidean distance</strong>. It maintains a 30-frame history of positions and bounding box areas. Motion is detected by comparing average area of first vs. second half of recent frames — <strong>growing area = approaching</strong>, shrinking = departing, &lt;2% change = stationary.',
            tags: ['Centroid Matching', '30-Frame History', 'Area Analysis', 'Motion State']
        },
        {
            icon: '🛤️', title: 'Lane Classification',
            desc: 'The frame is divided into <strong>three vertical zones</strong>: Left (0–35%), Center (35–65%), and Right (65–100%). Each tracked object is classified by its center x-coordinate. The center lane represents the ego vehicle\'s direct path and receives the highest risk weighting.',
            tags: ['3 Zones', 'Left 0-35%', 'Center 35-65%', 'Right 65-100%']
        },
        {
            icon: '⚡', title: 'Risk Assessment',
            desc: 'A composite risk score (0–100%) is computed using four weighted factors: <strong>Distance (35%)</strong> based on vertical position, <strong>Motion (30%)</strong> where approaching = 1.0, <strong>Lane (20%)</strong> where center = highest, and <strong>Object Type (15%)</strong> where pedestrians rank highest. Classified as LOW, MEDIUM, HIGH, or CRITICAL.',
            tags: ['4 Factors', 'Weighted Sum', '4 Risk Levels', '0-100%']
        },
        {
            icon: '🎨', title: 'Visualization & Output',
            desc: 'The visualizer draws <strong>color-coded bounding boxes</strong> (green→yellow→orange→red) with motion labels like [COMING→], [←GOING], [STOPPED]. Vertical lane lines divide the frame. A <strong>real-time stats dashboard</strong> shows object counts and risk distribution. A red warning banner flashes for CRITICAL detections.',
            tags: ['Color-coded Boxes', 'Motion Labels', 'Lane Lines', 'Stats Dashboard']
        }
    ];

    let currentStep = 0;
    let cycleTimer = null;

    // Slower cycle speed: 8 seconds per step
    const CYCLE_INTERVAL = 8000;

    function goToStep(index) {
        currentStep = index;
        const data = pipelineData[index];

        // Update active node
        nodes.forEach((n, i) => n.classList.toggle('active', i === index));

        // Animate info panel
        infoPanel.style.opacity = '0';
        infoPanel.style.transform = 'translateY(8px)';

        setTimeout(() => {
            infoPanel.innerHTML = `
        <h3>${data.icon} ${data.title}</h3>
        <p>${data.desc}</p>
        <div class="pipeline-tags">
          ${data.tags.map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
      `;
            infoPanel.style.opacity = '1';
            infoPanel.style.transform = 'translateY(0)';
        }, 250);
    }

    function startCycle() {
        if (cycleTimer) clearInterval(cycleTimer);
        cycleTimer = setInterval(() => {
            goToStep((currentStep + 1) % nodes.length);
        }, CYCLE_INTERVAL);
    }

    // Click handlers
    nodes.forEach(node => {
        node.addEventListener('click', () => {
            goToStep(parseInt(node.dataset.step));
            if (cycleTimer) clearInterval(cycleTimer);
            setTimeout(startCycle, 12000);
        });
    });

    // Start auto-cycle
    startCycle();

    // ---- Watch Demo button scrolls and plays video ----
    const watchBtn = document.getElementById('watchBtn');
    const mainVideo = document.getElementById('mainVideo');

    if (watchBtn && mainVideo) {
        watchBtn.addEventListener('click', e => {
            e.preventDefault();
            const showcase = document.getElementById('video-showcase');
            window.scrollTo({ top: showcase.offsetTop - 70, behavior: 'smooth' });
            setTimeout(() => {
                mainVideo.play().catch(() => {/* user interaction required */ });
            }, 600);
        });
    }

});
