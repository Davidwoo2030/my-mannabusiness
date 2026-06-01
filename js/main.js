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

})();
