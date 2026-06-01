/* =========================================
   MANNATECH GLG — MAIN JAVASCRIPT
   ========================================= */

(function () {
  'use strict';

  /* ---- DOM Ready ---- */
  document.addEventListener('DOMContentLoaded', function () {
    initNav();
    initFAQ();
    initScrollEffects();
    initRevealOnScroll();
    initScrollTopBtn();
    initContactForm();
    initCatalogSlider();
    initLightbox();
  });

  /* =========================================
     NAV — sticky + mobile toggle
     ========================================= */
  function initNav() {
    var header   = document.getElementById('header');
    var toggle   = document.getElementById('navToggle');
    var menu     = document.getElementById('navMenu');
    var links    = menu.querySelectorAll('a');

    // Toggle mobile menu
    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.toggle('open');
      toggle.setAttribute('aria-label', isOpen ? '메뉴 닫기' : '메뉴 열기');
    });

    // Close menu on link click
    links.forEach(function (link) {
      link.addEventListener('click', function () {
        menu.classList.remove('open');
      });
    });

    // Sticky header shadow
    window.addEventListener('scroll', function () {
      if (window.scrollY > 40) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    }, { passive: true });

    // Active nav link on scroll
    var sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', function () {
      var scrollY = window.scrollY + 90;
      sections.forEach(function (section) {
        var top    = section.offsetTop;
        var height = section.offsetHeight;
        var id     = section.getAttribute('id');
        var link   = menu.querySelector('a[href="#' + id + '"]');
        if (link) {
          if (scrollY >= top && scrollY < top + height) {
            links.forEach(function (l) { l.classList.remove('active'); });
            link.classList.add('active');
          }
        }
      });
    }, { passive: true });
  }

  /* =========================================
     FAQ — accordion + category filter
     ========================================= */
  function initFAQ() {
    var items   = document.querySelectorAll('.faq-item');
    var catBtns = document.querySelectorAll('.faq-cat-btn');

    // Accordion
    items.forEach(function (item) {
      var btn = item.querySelector('.faq-q');
      btn.addEventListener('click', function () {
        var isOpen = item.classList.contains('open');
        // Close all
        items.forEach(function (i) { i.classList.remove('open'); });
        // Open clicked
        if (!isOpen) { item.classList.add('open'); }
      });
    });

    // Category filter
    catBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        catBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        var cat = btn.getAttribute('data-cat');
        items.forEach(function (item) {
          if (cat === 'all' || item.getAttribute('data-cat') === cat) {
            item.classList.remove('hidden');
          } else {
            item.classList.add('hidden');
            item.classList.remove('open');
          }
        });
      });
    });
  }

  /* =========================================
     SCROLL EFFECTS — smooth anchor offset
     ========================================= */
  function initScrollEffects() {
    var headerHeight = 64;

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
      anchor.addEventListener('click', function (e) {
        var target = document.querySelector(this.getAttribute('href'));
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.scrollY - headerHeight;
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
    });
  }

  /* =========================================
     REVEAL ON SCROLL — IntersectionObserver
     ========================================= */
  function initRevealOnScroll() {
    // Add data-reveal to cards/elements
    var targets = document.querySelectorAll(
      '.pillar-card, .sci-card, .bonus-card, .product-card, .tl-item, ' +
      '.distrib-card, .cf-quad, .edu-step, .faq-item, .clean-step'
    );

    targets.forEach(function (el, i) {
      el.setAttribute('data-reveal', '');
      el.style.transitionDelay = (i % 6) * 0.07 + 's';
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 });

      targets.forEach(function (el) { observer.observe(el); });
    } else {
      // Fallback: reveal all
      targets.forEach(function (el) { el.classList.add('revealed'); });
    }
  }

  /* =========================================
     SCROLL TOP BUTTON
     ========================================= */
  function initScrollTopBtn() {
    var btn = document.createElement('button');
    btn.className = 'scroll-top';
    btn.innerHTML = '↑';
    btn.setAttribute('aria-label', '맨 위로');
    document.body.appendChild(btn);

    window.addEventListener('scroll', function () {
      if (window.scrollY > 500) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    }, { passive: true });

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* =========================================
     CONTACT FORM — basic submit
     ========================================= */
  function initContactForm() {
    var form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var name     = document.getElementById('name').value.trim();
      var phone    = document.getElementById('phone').value.trim();
      var interest = document.getElementById('interest').value;

      if (!name || !phone) {
        showFormMessage('이름과 연락처를 입력해 주세요.', 'error');
        return;
      }

      // Simulate submit
      var btn = form.querySelector('.form-submit');
      btn.textContent = '전송 중...';
      btn.disabled = true;

      setTimeout(function () {
        showFormMessage('문의가 접수되었습니다! 빠른 시일 내에 연락드리겠습니다. 😊', 'success');
        form.reset();
        btn.textContent = '문의 보내기';
        btn.disabled = false;
      }, 1200);
    });
  }

  function showFormMessage(msg, type) {
    var existing = document.querySelector('.form-message');
    if (existing) existing.remove();

    var el = document.createElement('div');
    el.className = 'form-message';
    el.textContent = msg;
    el.style.cssText = [
      'padding: 14px 18px',
      'border-radius: 8px',
      'font-size: .88rem',
      'font-weight: 600',
      'margin-top: 14px',
      type === 'success'
        ? 'background: rgba(61,184,112,.25); color: #a7f3c8; border: 1px solid rgba(61,184,112,.4);'
        : 'background: rgba(239,68,68,.2); color: #fca5a5; border: 1px solid rgba(239,68,68,.35);'
    ].join(';');

    var form = document.getElementById('contactForm');
    form.appendChild(el);

    setTimeout(function () { el.remove(); }, 5000);
  }

  /* =========================================
     STATS TABLE — number counter animation
     ========================================= */
  function animateCounters() {
    // Simple presence; numbers already displayed as text
  }

  /* =========================================
     CATALOG SLIDER
     ========================================= */
  var catalogImages = [
    { src: 'https://www.genspark.ai/api/files/s/m8oGjXNd', caption: '패키지 제품 — 트루헬스 클렌즈 패키지 / 미라클17 스타트팩 / 파워팩' },
    { src: 'https://www.genspark.ai/api/files/s/qY5esp6G', caption: 'Life & Health — 점막·소화 / 혈당·장 건강 제품' },
    { src: 'https://www.genspark.ai/api/files/s/RVypFwnv', caption: 'Life & Health — 면역건강 / 에너지 / 혈액순환 / 뇌건강 제품' },
    { src: 'https://www.genspark.ai/api/files/s/mFjD5tGN', caption: 'Life & Health — 앰브로토스 / 옵티멀 / 항산화 / 호르몬 건강' },
    { src: 'https://www.genspark.ai/api/files/s/wHwfsGWX', caption: 'Beauty & Skin Care — 헤어·바디·오랄·홈 케어 제품' },
    { src: 'https://www.genspark.ai/api/files/s/oREBBlqh', caption: 'Life & Health — 눈건강 / 콜라겐 / 관절 / 남성·여성 건강' },
    { src: 'https://www.genspark.ai/api/files/s/V6Dor1kY', caption: 'Beauty & Skin Care — 루미노베이션 스킨케어 풀 라인' },
    { src: 'https://www.genspark.ai/api/files/s/ttIw5R4W', caption: 'Energy & Body — 간건강 / 식사대용 / 다이어트 / 건강 음료' }
  ];

  var currentSlide = 0;
  var totalSlides  = catalogImages.length;

  function initCatalogSlider() {
    var slides   = document.querySelectorAll('.catalog-slide');
    var dots     = document.querySelectorAll('.dot');
    var catTabs  = document.querySelectorAll('.cat-tab');
    var prevBtn  = document.getElementById('sliderPrev');
    var nextBtn  = document.getElementById('sliderNext');
    var curNum   = document.getElementById('slideCurrentNum');

    if (!prevBtn || !nextBtn) return;

    function goToSlide(n) {
      // Clamp
      if (n < 0) n = totalSlides - 1;
      if (n >= totalSlides) n = 0;
      currentSlide = n;

      // Slides
      slides.forEach(function (s) { s.classList.remove('active'); });
      if (slides[n]) slides[n].classList.add('active');

      // Dots
      dots.forEach(function (d) { d.classList.remove('active'); });
      if (dots[n]) dots[n].classList.add('active');

      // Tabs
      catTabs.forEach(function (t) { t.classList.remove('active'); });
      if (catTabs[n]) catTabs[n].classList.add('active');

      // Counter
      if (curNum) curNum.textContent = n + 1;
    }

    prevBtn.addEventListener('click', function () { goToSlide(currentSlide - 1); });
    nextBtn.addEventListener('click', function () { goToSlide(currentSlide + 1); });

    // Dot clicks
    dots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        goToSlide(parseInt(this.getAttribute('data-dot'), 10));
      });
    });

    // Tab clicks
    catTabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        goToSlide(parseInt(this.getAttribute('data-slide'), 10));
      });
    });

    // Keyboard navigation
    document.addEventListener('keydown', function (e) {
      var overlay = document.getElementById('lightboxOverlay');
      if (overlay && overlay.classList.contains('open')) return; // lightbox handles its own keys
      if (e.key === 'ArrowLeft')  goToSlide(currentSlide - 1);
      if (e.key === 'ArrowRight') goToSlide(currentSlide + 1);
    });

    // Swipe support
    var touchStartX = 0;
    var slider = document.getElementById('catalogSlider');
    if (slider) {
      slider.addEventListener('touchstart', function (e) {
        touchStartX = e.touches[0].clientX;
      }, { passive: true });
      slider.addEventListener('touchend', function (e) {
        var diff = touchStartX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) {
          if (diff > 0) goToSlide(currentSlide + 1);
          else          goToSlide(currentSlide - 1);
        }
      }, { passive: true });
    }

    // Init
    goToSlide(0);
  }

  /* =========================================
     LIGHTBOX
     ========================================= */
  var lightboxIndex = 0;

  function initLightbox() {
    var overlay    = document.getElementById('lightboxOverlay');
    var img        = document.getElementById('lightboxImg');
    var caption    = document.getElementById('lightboxCaption');
    var closeBtn   = document.getElementById('lightboxClose');
    var prevBtn    = document.getElementById('lightboxPrev');
    var nextBtn    = document.getElementById('lightboxNext');
    var imgWraps   = document.querySelectorAll('.slide-img-wrap');

    if (!overlay) return;

    function openLightbox(index) {
      lightboxIndex = index;
      var item = catalogImages[index];
      img.src        = item.src;
      img.alt        = item.caption;
      caption.textContent = item.caption;
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
      // Clear src after transition
      setTimeout(function () { img.src = ''; }, 300);
    }

    function navLightbox(dir) {
      lightboxIndex = (lightboxIndex + dir + totalSlides) % totalSlides;
      var item = catalogImages[lightboxIndex];
      img.style.opacity = '0';
      setTimeout(function () {
        img.src = item.src;
        img.alt = item.caption;
        caption.textContent = item.caption;
        img.style.opacity = '1';
      }, 150);
    }

    // Set transition on lightbox img
    img.style.transition = 'opacity .15s ease';

    // Open via image wrap click
    imgWraps.forEach(function (wrap) {
      wrap.addEventListener('click', function () {
        var idx = parseInt(this.getAttribute('data-lightbox'), 10);
        if (!isNaN(idx)) openLightbox(idx);
      });
    });

    // Close
    closeBtn.addEventListener('click', closeLightbox);
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeLightbox();
    });

    // Nav
    prevBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      navLightbox(-1);
    });
    nextBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      navLightbox(1);
    });

    // Keyboard
    document.addEventListener('keydown', function (e) {
      if (!overlay.classList.contains('open')) return;
      if (e.key === 'Escape')     closeLightbox();
      if (e.key === 'ArrowLeft')  navLightbox(-1);
      if (e.key === 'ArrowRight') navLightbox(1);
    });
  }

})();
