#!/usr/bin/env python3
"""
Build the complete standalone HTML combining:
- index.html (full marketing site)
- css/style.css (inlined)
- js/main.js (inlined, with base64 catalog images)
- images/catalog-0..7.jpg (base64)  ← 기존 매나테크 전제품 카탈로그
- images/truhealth/truhealth-0..12.jpg (base64)  ← NEW: TruHealth 클린다이어트 브로셔
- price-compare feature (CSS + JS + HTML from price-compare-standalone.html)
"""

import base64
import os
import re

WEBAPP = '/home/user/webapp'

# ── 1a. Base64-encode original catalog images (매나테크 전제품) ────
print("Encoding catalog images (매나테크 전제품)...")
catalog_b64 = {}
for i in range(8):
    path = os.path.join(WEBAPP, f'images/catalog-{i}.jpg')
    with open(path, 'rb') as f:
        catalog_b64[i] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')
print(f"  Done: {len(catalog_b64)} catalog images encoded")

# ── 1b. Base64-encode TruHealth brochure images (고화질 2x 업스케일본) ────
print("Encoding TruHealth brochure images (HQ 2x upscaled)...")
th_b64 = {}
for i in range(13):
    # 고화질 폴더 우선 사용, 없으면 원본 폴백
    hq_path = os.path.join(WEBAPP, f'images/truhealth_hq/truhealth-{i}.jpg')
    orig_path = os.path.join(WEBAPP, f'images/truhealth/truhealth-{i}.jpg')
    path = hq_path if os.path.exists(hq_path) else orig_path
    with open(path, 'rb') as f:
        th_b64[i] = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('ascii')
    tag = 'HQ' if os.path.exists(hq_path) else 'orig'
    print(f"  [{tag}] truhealth-{i}.jpg")
print(f"  Done: {len(th_b64)} TruHealth images encoded")

# ── 2. Read source files ──────────────────────────────────────────
print("Reading source files...")

with open(os.path.join(WEBAPP, 'css/style.css'), 'r', encoding='utf-8') as f:
    CSS = f.read()

with open(os.path.join(WEBAPP, 'js/main.js'), 'r', encoding='utf-8') as f:
    MAIN_JS_RAW = f.read()

with open(os.path.join(WEBAPP, 'price-compare-standalone.html'), 'r', encoding='utf-8') as f:
    PC_HTML = f.read()

print("  Done")

# ── 3. Patch main.js: replace image src paths with base64 ────────
print("Patching main.js image references...")
MAIN_JS = MAIN_JS_RAW
for i in range(8):
    old = f'images/catalog-{i}.jpg'
    MAIN_JS = MAIN_JS.replace(f"'images/catalog-{i}.jpg'", f"'{catalog_b64[i]}'")
    MAIN_JS = MAIN_JS.replace(f'"images/catalog-{i}.jpg"', f'"{catalog_b64[i]}"')

print("  Done")

# ── 4. Extract price-compare CSS, HTML body, JS ──────────────────
print("Extracting price-compare sections...")

# Extract CSS between <style>...</style>
pc_css_match = re.search(r'<style>(.*?)</style>', PC_HTML, re.DOTALL)
PC_CSS = pc_css_match.group(1) if pc_css_match else ''

# Extract JS between <script>...</script>  (last one = main app JS)
pc_js_matches = re.findall(r'<script>(.*?)</script>', PC_HTML, re.DOTALL)
PC_JS = pc_js_matches[-1] if pc_js_matches else ''

# Extract body content
pc_body_match = re.search(r'<body>(.*?)</script>\s*</body>', PC_HTML, re.DOTALL)
if pc_body_match:
    pc_body_full = pc_body_match.group(1)
else:
    pc_body_full = ''

# Remove the <script> block from body content (we include JS separately)
pc_body_html = re.sub(r'<script>.*', '', pc_body_full, flags=re.DOTALL).strip()

print(f"  CSS: {len(PC_CSS)} chars, JS: {len(PC_JS)} chars, HTML: {len(pc_body_html)} chars")

# ── 5. Patch CSS: replace 'Noto Sans KR' font references with full system stack ─
# style.css 에서 body font-family 를 시스템 폰트로 직접 교체
SYSTEM_FONT = ("'Apple SD Gothic Neo', 'Malgun Gothic', '맑은 고딕', '나눔고딕', "
               "'Noto Sans CJK KR', -apple-system, BlinkMacSystemFont, sans-serif")
CSS = CSS.replace("font-family: 'Noto Sans KR', sans-serif;",
                  f"font-family: {SYSTEM_FONT};")
CSS = CSS.replace("font-family: 'Noto Sans KR',sans-serif;",
                  f"font-family: {SYSTEM_FONT};")
# 혹시 남아있는 Noto Sans KR 단독 참조도 교체
CSS = CSS.replace("'Noto Sans KR'", 
                  "'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕','나눔고딕','Noto Sans CJK KR'")

FONT_CSS = """
/* ── Standalone: 시스템 폰트 최우선 적용 (Google Fonts 불필요) ── */
html, body, * {
  font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', '맑은 고딕', '나눔고딕',
               'Noto Sans CJK KR', -apple-system, BlinkMacSystemFont, sans-serif;
}
"""

# ── 5b. Pre-build TruHealth slides HTML (separate var for f-string safety) ──
TH_SLIDES_META = [
    ("TruHealth Clean Diet 표지",              "portrait"),
    ("매나테크 제안 - 클린다이어트",           "landscape"),
    ("6가지 비만유형 / 다이어트의 이해",       "landscape"),
    ("클린다이어트의 원리 1",                  "landscape"),
    ("클린다이어트의 원리 2",                  "landscape"),
    ("3주 프로그램 1·2~3주차",                 "landscape"),
    ("3개월 유지 / 스마트 구독",               "landscape"),
    ("트루헬스 클렌즈 패키지 상세",            "landscape"),
    ("함께하면 좋은 제품",                     "landscape"),
    ("클린다이어트 진행시 개선과정 Q&amp;A",   "landscape"),
    ("클린다이어트가 효과적인 이유",            "portrait"),
    ("333 클린다이어트 / 3일 프로그램 리셋",   "landscape"),
    ("Q&amp;A / 명현반응 호전반응",             "landscape"),
]

TH_SLIDES_HTML = ''
for i, (alt, orient) in enumerate(TH_SLIDES_META):
    active_cls = ' active' if i == 0 else ''
    TH_SLIDES_HTML += (
        f'          <div class="th-slide{active_cls}" data-th="{i}" data-orient="{orient}">\n'
        f'            <img src="{th_b64[i]}" alt="{alt}" />\n'
        f'          </div>\n'
    )

TH_DOTS_HTML = ''.join(
    f'        <button class="th-dot{" active" if i == 0 else ""}" data-thdot="{i}"></button>\n'
    for i in range(13)
)

# ── 5c. TruHealth slider CSS ─────────────────────────────────────
TH_CSS = """
/* ═══════════════════════════════════════════════════
   TruHealth Clean Diet Brochure Slider
   ═══════════════════════════════════════════════════ */
.th-brochure-section {
  background: #f9f6f0;
  padding: 80px 0;
}
.th-slider-wrap {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 960px;
  margin: 0 auto 20px;
}
.th-slider {
  overflow: hidden;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 8px 40px rgba(0,0,0,.13);
  background: #fff;
}
.th-slide {
  display: none;
  width: 100%;
}
.th-slide.active {
  display: block;
}
.th-slide img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 12px;
  image-rendering: -webkit-optimize-contrast;
  image-rendering: crisp-edges;
}
.th-slide[data-orient="portrait"] {
  display: none;
  justify-content: center;
  background: #fff;
}
.th-slide[data-orient="portrait"].active {
  display: flex;
}
.th-slide[data-orient="portrait"] img {
  max-width: 480px;
  width: 100%;
  margin: 0 auto;
}
.th-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: rgba(255,255,255,.92);
  box-shadow: 0 2px 12px rgba(0,0,0,.18);
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  color: #2d6a4f;
  transition: background .2s, transform .2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.th-nav:hover {
  background: #2d6a4f;
  color: #fff;
  transform: translateY(-50%) scale(1.08);
}
.th-prev { left: -24px; }
.th-next { right: -24px; }
.th-dots {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 7px;
  margin: 14px 0 6px;
}
.th-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  border: none;
  background: #c8d8c0;
  cursor: pointer;
  padding: 0;
  transition: background .2s, transform .2s;
}
.th-dot.active {
  background: #2d6a4f;
  transform: scale(1.35);
}
.th-counter {
  text-align: center;
  font-size: .85rem;
  color: #888;
  margin-bottom: 0;
}
@media (max-width: 768px) {
  .th-prev { left: -14px; }
  .th-next { right: -14px; }
  .th-nav { width: 36px; height: 36px; font-size: 1.3rem; }
}
@media (max-width: 480px) {
  .th-prev { left: 4px; }
  .th-next { right: 4px; }
}
"""

# ── 5d. TruHealth slider JS ──────────────────────────────────────
TH_JS = """
(function() {
  var slides   = document.querySelectorAll('.th-slide');
  var dots     = document.querySelectorAll('.th-dot');
  var prevBtn  = document.getElementById('thPrev');
  var nextBtn  = document.getElementById('thNext');
  var curNumEl = document.getElementById('thCurrentNum');
  var totalEl  = document.getElementById('thTotalNum');
  var total    = slides.length;
  var cur      = 0;
  if (!slides.length) return;
  if (totalEl) totalEl.textContent = total;

  function goTo(n) {
    slides[cur].classList.remove('active');
    dots[cur]  && dots[cur].classList.remove('active');
    cur = (n + total) % total;
    slides[cur].classList.add('active');
    dots[cur]  && dots[cur].classList.add('active');
    if (curNumEl) curNumEl.textContent = cur + 1;
  }

  prevBtn && prevBtn.addEventListener('click', function() { goTo(cur - 1); });
  nextBtn && nextBtn.addEventListener('click', function() { goTo(cur + 1); });
  dots.forEach(function(d, i) { d.addEventListener('click', function() { goTo(i); }); });

  /* swipe */
  var startX = 0;
  var sliderEl = document.getElementById('thSlider');
  if (sliderEl) {
    sliderEl.addEventListener('touchstart', function(e) {
      startX = e.touches[0].clientX;
    }, { passive: true });
    sliderEl.addEventListener('touchend', function(e) {
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) goTo(dx < 0 ? cur + 1 : cur - 1);
    }, { passive: true });
  }
})();
"""

# ── 6. Assemble the complete HTML ────────────────────────────────
print("Assembling final HTML...")

# Main site nav link: change price-compare.html link to JS-based page switch
# We'll add a page-switching mechanism

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>매나테크 GLG | Transform Your Life — 완전판</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌿</text></svg>" />
  <meta name="description" content="매나테크 GLG 글로벌리더스그룹 — Transform Your Life. 제품 소개 + 5개국 가격비교 완전판" />

  <style>
/* ══════════════════════════════════════════════════════════
   SYSTEM FONT OVERRIDE — 최우선 (Google Fonts 대체)
   ══════════════════════════════════════════════════════════ */
{FONT_CSS}

/* ══════════════════════════════════════════════════════════
   MAIN STYLESHEET (style.css — Noto Sans KR 참조 패치 완료)
   ══════════════════════════════════════════════════════════ */
{CSS}

/* ── PAGE SWITCHER ── */
#page-main    {{ display: block; }}
#page-compare {{ display: none;  }}
body.show-compare #page-main    {{ display: none; }}
body.show-compare #page-compare {{ display: block; }}

/* ══════════════════════════════════════════════════════════
   PRICE COMPARE STYLESHEET
   ══════════════════════════════════════════════════════════ */
/* scope compare styles inside #page-compare */
#page-compare {{
  font-family: 'Apple SD Gothic Neo','Malgun Gothic','맑은 고딕','나눔고딕','Noto Sans KR',sans-serif;
}}
{PC_CSS}

/* Override compare topbar back button behavior */
.topbar-back-main {{
  font-size: .85rem;
  color: rgba(255,255,255,.82);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 20px;
  transition: all .2s;
  cursor: pointer;
  background: none;
}}
.topbar-back-main:hover {{ background: rgba(255,255,255,.12); color: #fff; }}

/* stats-source in business section — override for light bg */
.business-section .stats-source {{ color: var(--text-sub) !important; }}

{TH_CSS}
  </style>
</head>
<body>

<!-- ╔══════════════════════════════════════════════════════╗
     ║  PAGE 1: MAIN MARKETING SITE                        ║
     ╚══════════════════════════════════════════════════════╝ -->
<div id="page-main">

  <!-- ===== NAVIGATION ===== -->
  <header id="header">
    <nav class="nav-container">
      <div class="nav-logo">
        <span class="logo-glg">GLG</span>
        <span class="logo-text">MANNATECH</span>
      </div>
      <button class="nav-toggle" id="navToggle" aria-label="메뉴 열기">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-menu" id="navMenu">
        <li><a href="#about">매나테크란</a></li>
        <li><a href="#product">제품 소개</a></li>
        <li><a href="#catalog">전제품 안내</a></li>
        <li><a href="#truhealth">클린다이어트</a></li>
        <li><a href="#science">과학적 근거</a></li>
        <li><a href="#business">비즈니스</a></li>
        <li><a href="#compensation">보상플랜</a></li>
        <li><a href="#faq">FAQ</a></li>
        <li><a href="#" class="nav-cta nav-price" onclick="showComparePage(event)">🌏 가격 비교</a></li>
        <li><a href="#contact" class="nav-cta">문의하기</a></li>
      </ul>
    </nav>
  </header>

  <!-- ===== HERO SECTION ===== -->
  <section class="hero" id="hero">
    <div class="hero-bg">
      <div class="stripe stripe-1"></div>
      <div class="stripe stripe-2"></div>
      <div class="stripe stripe-3"></div>
      <div class="stripe stripe-4"></div>
      <div class="stripe stripe-5"></div>
    </div>
    <div class="hero-content">
      <p class="hero-eyebrow">SPECIAL MANNATECH</p>
      <h1 class="hero-title">
        <span class="hero-title-light">TRANSFORM</span>
        <span class="hero-title-bold">YOUR LIFE</span>
      </h1>
      <div class="hero-divider"></div>
      <p class="hero-sub">매나테크 이야기</p>
      <div class="hero-badges">
        <span class="badge badge-green">NASDAQ 상장기업</span>
        <span class="badge badge-dark">29개국 글로벌</span>
        <span class="badge badge-yellow">특허 149개 보유</span>
      </div>
      <a href="#about" class="hero-btn">더 알아보기 <span>↓</span></a>
    </div>
    <div class="hero-circle">
      <div class="circle-inner">
        <span class="circle-glg">GLG</span>
        <span class="circle-sub">Global Leaders Group</span>
      </div>
    </div>
  </section>

  <!-- ===== ABOUT MANNATECH ===== -->
  <section class="section about-section" id="about">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">ABOUT MANNATECH</span>
        <h2 class="section-title">네트워크 마케팅 선택 시<br><em>반드시 검토해야 할 5가지</em></h2>
      </div>

      <div class="five-pillars">
        <div class="pillar-card">
          <div class="pillar-icon">🏛️</div>
          <h3>회사의 안정성</h3>
          <p>1994년 창립, NASDAQ 상장, 29개국 진출한 글로벌 기업</p>
        </div>
        <div class="pillar-card featured">
          <div class="pillar-icon">🔬</div>
          <h3>아이템 (특허·대체불가)</h3>
          <p>글리코영양소 독점 특허 149개 보유, 세계 유일의 기술</p>
        </div>
        <div class="pillar-card">
          <div class="pillar-icon">📊</div>
          <h3>합리적 보상플랜</h3>
          <p>업계 최상위 34.5% 후원수당 지급률</p>
        </div>
        <div class="pillar-card featured">
          <div class="pillar-icon">🎓</div>
          <h3>검증된 성공 교육시스템</h3>
          <p>MBA·MBS·SO워크샵 체계적인 단계별 교육 시스템</p>
        </div>
        <div class="pillar-card">
          <div class="pillar-icon">⏰</div>
          <h3>타이밍</h3>
          <p>글리코영양소, 차세대 건강 산업의 핵심으로 급부상 중</p>
        </div>
      </div>

      <!-- Timeline -->
      <div class="timeline-wrap">
        <h3 class="timeline-title">MANNATECH HISTORY</h3>
        <div class="timeline">
          <div class="tl-item"><div class="tl-year">1994</div><div class="tl-dot"></div><div class="tl-content">미국 사무소 설립</div></div>
          <div class="tl-item"><div class="tl-year">1996</div><div class="tl-dot"></div><div class="tl-content">앰브로토스® 글로벌 출시</div></div>
          <div class="tl-item"><div class="tl-year">1999</div><div class="tl-dot"></div><div class="tl-content">NASDAQ 상장</div></div>
          <div class="tl-item"><div class="tl-year">2003</div><div class="tl-dot"></div><div class="tl-content">MIT 10대 신기술 글리코믹스 선정</div></div>
          <div class="tl-item"><div class="tl-year">2004</div><div class="tl-dot"></div><div class="tl-content">매나테크 코리아 설립</div></div>
          <div class="tl-item"><div class="tl-year">2008</div><div class="tl-dot"></div><div class="tl-content">NSF 인증 획득</div></div>
          <div class="tl-item"><div class="tl-year">2013</div><div class="tl-dot"></div><div class="tl-content">M5M 프로그램 전세계 500만명 영향</div></div>
          <div class="tl-item"><div class="tl-year">2023</div><div class="tl-dot"></div><div class="tl-content">글리코믹스 특허 149개 보유</div></div>
          <div class="tl-item highlight"><div class="tl-year">2025</div><div class="tl-dot"></div><div class="tl-content">브랜드 고객충성도 면역기능식품 <strong>1위</strong></div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== PRODUCT SECTION ===== -->
  <section class="section product-section" id="product">
    <div class="container">
      <div class="section-header light">
        <span class="section-tag white">PRODUCT</span>
        <h2 class="section-title white">독자적 글리코영양소를 기반한<br><em>리얼 푸드 테크놀로지 솔루션</em></h2>
        <p class="section-desc white">우리 몸 = 60조 ~ 100조개의 세포 | 건강한 세포 = 건강한 몸</p>
      </div>

      <div class="product-grid">
        <div class="product-card">
          <div class="product-card-header"><span class="product-icon">🧬</span><h3>세포의 건강에 작용하는 글리코영양소</h3></div>
          <!-- 인체 → 세포 흐름 + 중앙 세포 SVG -->
          <div class="body-flow-wrap">
            <div class="body-flow">
              <div class="flow-step">인체</div><div class="flow-arrow">→</div>
              <div class="flow-step">5장 6부</div><div class="flow-arrow">→</div>
              <div class="flow-step">조직</div><div class="flow-arrow">→</div>
              <div class="flow-step active">세포</div>
            </div>
            <!-- 세포 + 당사슬 SVG 일러스트 -->
            <div class="cell-svg-hero">
              <svg viewBox="0 0 120 120" width="110" height="110" xmlns="http://www.w3.org/2000/svg">
                <!-- 외부 당사슬 (긴 돌기, 다수) -->
                <g stroke="#74c69d" stroke-width="2.2" stroke-linecap="round" fill="none">
                  <line x1="60" y1="4"  x2="60" y2="18"/>
                  <line x1="82" y1="9"  x2="76" y2="21"/>
                  <line x1="99" y1="26" x2="89" y2="33"/>
                  <line x1="108" y1="48" x2="95" y2="50"/>
                  <line x1="105" y1="71" x2="93" y2="66"/>
                  <line x1="91" y1="90" x2="82" y2="80"/>
                  <line x1="72" y1="103" x2="67" y2="91"/>
                  <line x1="50" y1="106" x2="52" y2="93"/>
                  <line x1="30" y1="101" x2="36" y2="90"/>
                  <line x1="14" y1="88" x2="23" y2="79"/>
                  <line x1="4"  y1="69" x2="17" y2="65"/>
                  <line x1="2"  y1="48" x2="15" y2="50"/>
                  <line x1="7"  y1="28" x2="19" y2="34"/>
                  <line x1="22" y1="11" x2="31" y2="22"/>
                  <line x1="42" y1="4"  x2="46" y2="18"/>
                </g>
                <!-- 당사슬 끝 노드 -->
                <g fill="#40916c">
                  <circle cx="60" cy="3"   r="3.5"/>
                  <circle cx="83" cy="8"   r="3"/>
                  <circle cx="100" cy="25" r="3"/>
                  <circle cx="109" cy="47" r="3"/>
                  <circle cx="106" cy="72" r="3"/>
                  <circle cx="92" cy="91"  r="3"/>
                  <circle cx="73" cy="104" r="3"/>
                  <circle cx="50" cy="107" r="3"/>
                  <circle cx="29" cy="102" r="3"/>
                  <circle cx="13" cy="89"  r="3"/>
                  <circle cx="3"  cy="70"  r="3"/>
                  <circle cx="1"  cy="48"  r="3"/>
                  <circle cx="6"  cy="27"  r="3"/>
                  <circle cx="21" cy="10"  r="3"/>
                  <circle cx="41" cy="3"   r="3"/>
                </g>
                <!-- 세포막 -->
                <circle cx="60" cy="60" r="36" fill="rgba(116,198,157,0.2)" stroke="#74c69d" stroke-width="3"/>
                <!-- 세포질 내부 -->
                <circle cx="60" cy="60" r="28" fill="rgba(116,198,157,0.10)"/>
                <!-- 핵막 -->
                <ellipse cx="59" cy="59" rx="16" ry="15" fill="rgba(29,68,40,0.75)" stroke="#52d68a" stroke-width="2"/>
                <!-- 인 (nucleolus) -->
                <circle cx="55" cy="55" rx="6" ry="5" r="5.5" fill="rgba(82,214,138,0.55)"/>
                <circle cx="63" cy="63" r="3" fill="rgba(82,214,138,0.3)"/>
                <!-- 미토콘드리아 점들 -->
                <ellipse cx="44" cy="65" rx="5" ry="3" fill="rgba(255,209,102,0.45)" stroke="#ffd166" stroke-width="1"/>
                <ellipse cx="74" cy="52" rx="4" ry="2.5" fill="rgba(255,209,102,0.45)" stroke="#ffd166" stroke-width="1"/>
                <ellipse cx="50" cy="75" rx="3.5" ry="2" fill="rgba(255,209,102,0.35)" stroke="#ffd166" stroke-width="1"/>
              </svg>
            </div>
          </div>
          <p class="product-desc">세포와 세포 사이에 흐르는 정보인 당사슬이 호르몬, 미네랄, 비타민을 인지하고, 바이러스·박테리아·독소에 대한 1차 면역작용을 합니다.</p>
        </div>
        <div class="product-card">
          <div class="product-card-header"><span class="product-icon">⚡</span><h3>글리코영양소(당 영양소)의 8가지 기능</h3></div>
          <ul class="func-list">
            <li><span class="num">1</span> 해독 (MCP + 알긴산나트륨)</li>
            <li><span class="num">2</span> 영양소 흡수 (세포, 소장)</li>
            <li><span class="num">3</span> 면역조절 기능</li>
            <li><span class="num">4</span> 세포의 소멸과 발생</li>
            <li><span class="num">5</span> 호르몬 인지</li>
            <li><span class="num">6</span> 위와 장의 건강</li>
            <li><span class="num">7</span> 센서의 역할</li>
            <li><span class="num">8</span> 줄기세포</li>
          </ul>
        </div>
        <div class="product-card">
          <div class="product-card-header"><span class="product-icon">🔬</span><h3>세포 상태와 당사슬</h3></div>
          <div class="cell-status">

            <!-- 건강한 세포: 당사슬(돌기) 풍부 -->
            <div class="cell-item healthy">
              <div class="cell-circle">
                <svg viewBox="0 0 90 90" width="90" height="90" xmlns="http://www.w3.org/2000/svg">
                  <!-- 당사슬 돌기 (많음) -->
                  <g stroke="#52d68a" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.85">
                    <line x1="45" y1="6"  x2="45" y2="14"/><circle cx="45" cy="5"  r="2.5" fill="#52d68a"/>
                    <line x1="63" y1="11" x2="59" y2="18"/><circle cx="64" cy="10" r="2.5" fill="#52d68a"/>
                    <line x1="76" y1="24" x2="70" y2="28"/><circle cx="78" cy="23" r="2.5" fill="#52d68a"/>
                    <line x1="82" y1="42" x2="74" y2="43"/><circle cx="84" cy="42" r="2.5" fill="#52d68a"/>
                    <line x1="76" y1="60" x2="70" y2="56"/><circle cx="78" cy="62" r="2.5" fill="#52d68a"/>
                    <line x1="63" y1="73" x2="59" y2="67"/><circle cx="64" cy="75" r="2.5" fill="#52d68a"/>
                    <line x1="45" y1="78" x2="45" y2="70"/><circle cx="45" cy="80" r="2.5" fill="#52d68a"/>
                    <line x1="27" y1="73" x2="31" y2="67"/><circle cx="26" cy="75" r="2.5" fill="#52d68a"/>
                    <line x1="14" y1="60" x2="20" y2="56"/><circle cx="12" cy="62" r="2.5" fill="#52d68a"/>
                    <line x1="8"  y1="42" x2="16" y2="43"/><circle cx="6"  cy="42" r="2.5" fill="#52d68a"/>
                    <line x1="14" y1="24" x2="20" y2="28"/><circle cx="12" cy="23" r="2.5" fill="#52d68a"/>
                    <line x1="27" y1="11" x2="31" y2="18"/><circle cx="26" cy="10" r="2.5" fill="#52d68a"/>
                  </g>
                  <!-- 세포막 -->
                  <circle cx="45" cy="45" r="28" fill="rgba(82,214,138,0.18)" stroke="#52d68a" stroke-width="2.5"/>
                  <!-- 세포질 -->
                  <circle cx="45" cy="45" r="21" fill="rgba(82,214,138,0.12)"/>
                  <!-- 핵 -->
                  <ellipse cx="44" cy="44" rx="11" ry="10" fill="rgba(45,106,79,0.7)" stroke="#52d68a" stroke-width="1.5"/>
                  <ellipse cx="41" cy="41" rx="4" ry="3.5" fill="rgba(82,214,138,0.5)" stroke="none"/>
                </svg>
              </div>
              <span class="cell-label">건강<br/>(당사슬 10만개)</span>
            </div>

            <!-- 반건강 세포: 당사슬 보통 -->
            <div class="cell-item warning">
              <div class="cell-circle">
                <svg viewBox="0 0 90 90" width="90" height="90" xmlns="http://www.w3.org/2000/svg">
                  <!-- 당사슬 돌기 (중간) -->
                  <g stroke="#ffd166" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.85">
                    <line x1="45" y1="8"  x2="45" y2="16"/><circle cx="45" cy="7"  r="2.5" fill="#ffd166"/>
                    <line x1="68" y1="18" x2="63" y2="24"/><circle cx="70" cy="17" r="2.5" fill="#ffd166"/>
                    <line x1="80" y1="42" x2="72" y2="43"/><circle cx="82" cy="42" r="2.5" fill="#ffd166"/>
                    <line x1="68" y1="66" x2="63" y2="61"/><circle cx="70" cy="68" r="2.5" fill="#ffd166"/>
                    <line x1="45" y1="76" x2="45" y2="68"/><circle cx="45" cy="78" r="2.5" fill="#ffd166"/>
                    <line x1="22" y1="66" x2="27" y2="61"/><circle cx="20" cy="68" r="2.5" fill="#ffd166"/>
                    <line x1="10" y1="42" x2="18" y2="43"/><circle cx="8"  cy="42" r="2.5" fill="#ffd166"/>
                    <line x1="22" y1="18" x2="27" y2="24"/><circle cx="20" cy="17" r="2.5" fill="#ffd166"/>
                  </g>
                  <!-- 세포막 -->
                  <circle cx="45" cy="45" r="28" fill="rgba(255,209,102,0.15)" stroke="#ffd166" stroke-width="2.5"/>
                  <circle cx="45" cy="45" r="21" fill="rgba(255,209,102,0.10)"/>
                  <!-- 핵 -->
                  <ellipse cx="44" cy="44" rx="11" ry="10" fill="rgba(120,80,20,0.6)" stroke="#ffd166" stroke-width="1.5"/>
                  <ellipse cx="41" cy="41" rx="4" ry="3.5" fill="rgba(255,209,102,0.5)" stroke="none"/>
                </svg>
              </div>
              <span class="cell-label">반건강<br/>(3~4만개)</span>
            </div>

            <!-- 질병 세포: 당사슬 희소 -->
            <div class="cell-item danger">
              <div class="cell-circle">
                <svg viewBox="0 0 90 90" width="90" height="90" xmlns="http://www.w3.org/2000/svg">
                  <!-- 당사슬 돌기 (매우 적음) -->
                  <g stroke="#ef4444" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.85">
                    <line x1="45" y1="10" x2="45" y2="17"/><circle cx="45" cy="9"  r="2.5" fill="#ef4444"/>
                    <line x1="76" y1="42" x2="69" y2="43"/><circle cx="78" cy="42" r="2.5" fill="#ef4444"/>
                    <line x1="14" y1="42" x2="21" y2="43"/><circle cx="12" cy="42" r="2.5" fill="#ef4444"/>
                  </g>
                  <!-- 세포막 (불규칙) -->
                  <path d="M45,17 Q62,14 72,27 Q83,40 77,56 Q70,72 55,76 Q40,82 28,73 Q14,63 13,48 Q12,33 23,23 Q34,13 45,17Z"
                        fill="rgba(239,68,68,0.12)" stroke="#ef4444" stroke-width="2"/>
                  <circle cx="45" cy="47" r="19" fill="rgba(239,68,68,0.08)"/>
                  <!-- 핵 (찌그러짐) -->
                  <ellipse cx="44" cy="46" rx="9" ry="11" fill="rgba(100,20,20,0.65)" stroke="#ef4444" stroke-width="1.5"/>
                  <ellipse cx="42" cy="43" rx="3" ry="2.5" fill="rgba(239,68,68,0.4)" stroke="none"/>
                </svg>
              </div>
              <span class="cell-label">질병<br/>(1만개 미만)</span>
            </div>

          </div>
          <p class="product-desc small">건강한 세포는 10만개의 당사슬을 가지고 있으며, 질병 상태에서는 1만개 미만으로 줄어듭니다.</p>
        </div>
        <div class="product-card wide">
          <div class="product-card-header"><span class="product-icon">🌿</span><h3>글리코영양소 = 8개의 필수 단당류</h3></div>
          <div class="saccharides">
            <span class="sac">포도당</span><span class="sac">갈락토스</span><span class="sac">만노스</span>
            <span class="sac">푸코스</span><span class="sac">자일로스</span><span class="sac">N-아세틸글루코사민</span>
            <span class="sac">N-아세틸갈락토사민</span><span class="sac">N-아세틸뉴라민산</span>
          </div>
          <p class="product-desc">당사슬, 축수, 섬모, 글리칸, 당쇄, 당으로 구성된 8가지 핵심 탄수화물로 이루어진 세포 커뮤니케이션의 핵심 영양소입니다.</p>
        </div>
      </div>

      <div class="clean-program">
        <h3 class="clean-title">클린 프로그램 (Clean Program)</h3>
        <div class="clean-steps">
          <div class="clean-step"><div class="clean-step-icon">🌱</div><h4>비움</h4><p>독소 배출 및 해독 과정</p></div>
          <div class="clean-arrow">→</div>
          <div class="clean-step"><div class="clean-step-icon">💪</div><h4>채움</h4><p>최적의 영양소 공급</p></div>
          <div class="clean-arrow">→</div>
          <div class="clean-step"><div class="clean-step-icon">✨</div><h4>경험</h4><p>체지방 감소, 조직 회복</p></div>
        </div>
        <p class="clean-note">※ 굶는 다이어트(X) — 1주 클린 식사의 효과, 단진단 Real Food 영양식</p>
      </div>
    </div>
  </section>

  <!-- ===== PRODUCT CATALOG SECTION ===== -->
  <section class="section catalog-section" id="catalog">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">PRODUCT CATALOG</span>
        <h2 class="section-title">매나테크 전제품 안내서<br><em>카테고리별 제품 살펴보기</em></h2>
        <p class="section-desc">슬라이드를 클릭하면 크게 볼 수 있습니다</p>
      </div>

      <div class="cat-tabs">
        <button class="cat-tab active" data-slide="0"><span class="cat-tab-icon">📦</span><span>전체 안내서</span></button>
        <button class="cat-tab" data-slide="1"><span class="cat-tab-icon">🌿</span><span>Life &amp; Health</span></button>
        <button class="cat-tab" data-slide="2"><span class="cat-tab-icon">💊</span><span>면역·에너지</span></button>
        <button class="cat-tab" data-slide="3"><span class="cat-tab-icon">🌸</span><span>Beauty &amp; Skin</span></button>
        <button class="cat-tab" data-slide="4"><span class="cat-tab-icon">💪</span><span>Energy &amp; Body</span></button>
        <button class="cat-tab" data-slide="5"><span class="cat-tab-icon">👁️</span><span>눈·관절·여성</span></button>
        <button class="cat-tab" data-slide="6"><span class="cat-tab-icon">✨</span><span>스킨케어 라인</span></button>
        <button class="cat-tab" data-slide="7"><span class="cat-tab-icon">🧴</span><span>뷰티 홈케어</span></button>
      </div>

      <div class="catalog-slider-wrap">
        <button class="slider-nav slider-prev" id="sliderPrev" aria-label="이전">&#8249;</button>
        <div class="catalog-slider" id="catalogSlider">

          <div class="catalog-slide active" data-index="0">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="0">
                <img src="{catalog_b64[0]}" alt="매나테크 전제품 안내서 - 패키지" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge">패키지 제품</span>
                <h3>트루헬스 클렌즈 패키지 &amp; 미라클17</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>트루헬스 클렌즈 패키지</strong><p>트루플레니쉬·트루쉐이프·트루퓨어·오소린·엠브로토스 등</p><span class="price-tag">회원가 990,000원 / 639PV</span></div>
                  <div class="slide-product-item"><strong>미라클17 스타트팩</strong><p>오소린·뉴트리베루스·트루퓨어·트루플레니쉬 구성</p><span class="price-tag">회원가 350,000원 / 226PV</span></div>
                  <div class="slide-product-item"><strong>미라클17 파워팩</strong><p>스타트팩 3배 구성 + 홈인바디 무료 증정</p><span class="price-tag">회원가 1,050,000원 / 678PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="1">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="1">
                <img src="{catalog_b64[1]}" alt="Life &amp; Health - 소화·혈당 제품" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge green">Life &amp; Health</span>
                <h3>점막·소화 / 혈당·장 건강</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>매나-C®</strong><p>국내산 고려인삼 + 비타민C | 면역·피로 개선</p><span class="price-tag">회원가 66,000원 / 43PV</span></div>
                  <div class="slide-product-item"><strong>혈당 프로밸런스</strong><p>바나바잎·마그네슘·크롬 | 식후 혈당 상승 억제</p><span class="price-tag">회원가 54,000원 / 35PV</span></div>
                  <div class="slide-product-item"><strong>엔자임 프로밸런스</strong><p>17가지 곡물 발효 효소 | 소화·대사 지원</p><span class="price-tag">회원가 62,000원 / 40PV</span></div>
                  <div class="slide-product-item"><strong>지아이-프로밸런스</strong><p>프로바이오틱스 8종 55억 마리 | 장 건강</p><span class="price-tag">회원가 49,000원 / 32PV</span></div>
                  <div class="slide-product-item"><strong>바이탈 프로밸런스</strong><p>오렌지&amp;자몽 추출·아카시아검·비오틴 | 장벽 강화</p><span class="price-tag">회원가 77,000원 / 50PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="2">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="2">
                <img src="{catalog_b64[2]}" alt="Life &amp; Health - 면역·에너지·뇌건강 제품" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge green">Life &amp; Health</span>
                <h3>면역건강 / 에너지 / 혈액순환 / 뇌건강</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>만나폴</strong><p>알로에 베라 겔 415:1 고농축 | 면역·장·피부</p><span class="price-tag">회원가 330,000원 / 213PV</span></div>
                  <div class="slide-product-item"><strong>뉴트리베루스™</strong><p>멀티비타민+미네랄+과일채소 분말 파우더</p><span class="price-tag">회원가 97,000원 / 63PV</span></div>
                  <div class="slide-product-item"><strong>임팩트 플러스™</strong><p>비타민B군+철분+아미노산 | 활력·에너지 회복</p><span class="price-tag">회원가 72,000원 / 46PV</span></div>
                  <div class="slide-product-item"><strong>매나붐™ 리포좀 비타민C</strong><p>리포좀 제형 비타민C 500mg | 물 없이 섭취 가능</p><span class="price-tag">회원가 54,000원 / 35PV</span></div>
                  <div class="slide-product-item"><strong>오메가-3 위드 비타민D</strong><p>rTG형 오메가-3 + 비타민D | 혈행·뼈 건강</p><span class="price-tag">회원가 49,000원 / 32PV</span></div>
                  <div class="slide-product-item"><strong>브레인플러스</strong><p>포스파티딜세린 | 인지능력·피부 자외선 보호</p><span class="price-tag">회원가 131,000원 / 85PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="3">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="3">
                <img src="{catalog_b64[3]}" alt="Life &amp; Health - 앰브로토스·옵티멀 패킷" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge green">Life &amp; Health</span>
                <h3>면역 / 종합 건강 / 항산화 / 호르몬</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>앰브로토스 라이프™</strong><p>20년 연구 글리코영양소 | 면역·장·피부 100% 식물성</p><span class="price-tag">회원가 223,000원 / 144PV</span></div>
                  <div class="slide-product-item"><strong>앰브로토스 라이프 이지™</strong><p>슬림스틱 파우더 형태 | 간편 섭취</p><span class="price-tag">회원가 127,000원 / 82PV</span></div>
                  <div class="slide-product-item"><strong>옵티멀 서포트 패킷</strong><p>종합 비타민·미네랄 22가지 | 면역·혈관·기억력</p><span class="price-tag">회원가 269,000원 / 174PV</span></div>
                  <div class="slide-product-item"><strong>앰브로토스 AO®</strong><p>비타민C+E+플라보노이드 | 항산화 세포 보호</p><span class="price-tag">회원가 81,000원 / 52PV</span></div>
                  <div class="slide-product-item"><strong>카탈리스트</strong><p>13가지 비타민+9가지 미네랄 | 에너지·뼈·면역</p><span class="price-tag">회원가 71,000원 / 46PV</span></div>
                  <div class="slide-product-item"><strong>플러스™</strong><p>진세노사이드+대두 추출 | 면역·피로 개선</p><span class="price-tag">회원가 66,000원 / 43PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="4">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="4">
                <img src="{catalog_b64[4]}" alt="Beauty &amp; Skin Care - 헤어·바디·오랄 케어" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge pink">Beauty &amp; Skin Care</span>
                <h3>헤어 / 바디 / 오랄 / 홈 케어</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>디오갠트 바디 클렌저</strong><p>천연 유래 성분+6-히알루론산 | pH5~6.5 미산성</p><span class="price-tag">회원가 30,000원 / 19PV</span></div>
                  <div class="slide-product-item"><strong>디오갠트 헤어 샴푸</strong><p>탈모 증상 완화 기능성 | 실페이트 FREE</p><span class="price-tag">회원가 31,000원 / 20PV</span></div>
                  <div class="slide-product-item"><strong>디오갠트 컨디셔너</strong><p>탈모 증상 완화 기능성 | 실리콘 FREE</p><span class="price-tag">회원가 21,000원 / 14PV</span></div>
                  <div class="slide-product-item"><strong>엠프리존®</strong><p>앰브로토스®+알로에+비타민E | 피부 진정·재생</p><span class="price-tag">회원가 42,000원 / 27PV</span></div>
                  <div class="slide-product-item"><strong>프레시덴 치약 / 칫솔</strong><p>9가지 무첨가 치약 | 특허 PLA 소재 칫솔</p><span class="price-tag">치약 9,500원 / 칫솔 9,300원</span></div>
                  <div class="slide-product-item"><strong>퓨로 주방세제 / 세탁세제</strong><p>EWG 1등급 천연 성분 | 코코넛 유래 계면활성제</p><span class="price-tag">주방 9,500원 / 세탁 17,500원</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="5">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="5">
                <img src="{catalog_b64[5]}" alt="Life &amp; Health - 눈·콜라겐·관절·여성 건강" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge green">Life &amp; Health</span>
                <h3>눈건강 / 콜라겐 / 관절 / 남성·여성 건강</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>아이 서포트</strong><p>루테인+지아잔틴+아스타잔틴 | 눈 건강</p><span class="price-tag">회원가 45,000원 / 29PV</span></div>
                  <div class="slide-product-item"><strong>로즈 뷰티 콜라겐</strong><p>300Da 초저분자 콜라겐 2,000mg | 3중 피부 시너지</p><span class="price-tag">회원가 65,000원 / 42PV</span></div>
                  <div class="slide-product-item"><strong>조인트 서포트</strong><p>MSM 1,500mg+강황 추출물 | 관절·연골 건강</p><span class="price-tag">회원가 78,000원 / 50PV</span></div>
                  <div class="slide-product-item"><strong>맨즈 프라임7™</strong><p>쏘팔메토+옥타코사놀 | 전립선·남성 건강</p><span class="price-tag">회원가 62,000원 / 40PV</span></div>
                  <div class="slide-product-item"><strong>우먼스 프리미어7™</strong><p>감마리놀렌산+복숭아씨 추출물 | 갱년기·여성 건강</p><span class="price-tag">회원가 88,000원 / 57PV</span></div>
                  <div class="slide-product-item"><strong>매나베어즈™ (어린이)</strong><p>앰브로토스®+7가지 과일채소 | 어린이 면역 젤리</p><span class="price-tag">회원가 49,000원 / 32PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="6">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="6">
                <img src="{catalog_b64[6]}" alt="Beauty &amp; Skin Care - 루미노베이션 스킨케어 라인" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge pink">Beauty &amp; Skin Care</span>
                <h3>루미노베이션 스킨케어 풀 라인</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>퍼스트 에센셜 토너</strong><p>세라마이드+43가지 천연보습인자 | 광채 보습</p><span class="price-tag">회원가 48,000원 / 31PV</span></div>
                  <div class="slide-product-item"><strong>루미너스 에센스 로션</strong><p>에센스+로션 2in1 | 고보습 윤광</p><span class="price-tag">회원가 57,000원 / 37PV</span></div>
                  <div class="slide-product-item"><strong>유스 인텐시브 케어 크림</strong><p>8가지 펩타이드 | 탄력·주름 개선</p><span class="price-tag">회원가 78,000원 / 50PV</span></div>
                  <div class="slide-product-item"><strong>루미노베이션 CC 쿠션</strong><p>다이아몬드 가루+마이크로비아 성분 | 화사한 광채</p><span class="price-tag">회원가 61,000원 / 39PV</span></div>
                  <div class="slide-product-item"><strong>글리코 스킨 리터닝 케어 프로그램</strong><p>캡슐+앰플+필링젤 4주 집중 케어</p><span class="price-tag">회원가 185,000원 / 119PV</span></div>
                  <div class="slide-product-item"><strong>글로우 글리칸 비타민C 세럼</strong><p>순수 비타민C 15% | 광채·탄력 강화</p><span class="price-tag">회원가 66,000원 / 43PV</span></div>
                </div>
              </div>
            </div>
          </div>

          <div class="catalog-slide" data-index="7">
            <div class="slide-inner">
              <div class="slide-img-wrap" data-lightbox="7">
                <img src="{catalog_b64[7]}" alt="Energy &amp; Body - 간건강·식사대용·다이어트·음료" loading="lazy" />
                <div class="slide-zoom-hint">🔍 클릭하여 크게 보기</div>
              </div>
              <div class="slide-info">
                <span class="slide-cat-badge navy">Energy &amp; Body</span>
                <h3>간건강 / 식사대용 / 다이어트 / 건강 음료</h3>
                <div class="slide-products">
                  <div class="slide-product-item"><strong>트루퓨어™</strong><p>밀크씨슬+비타민B6 | 간 건강·에너지 대사</p><span class="price-tag">회원가 66,000원 / 43PV</span></div>
                  <div class="slide-product-item"><strong>트루플레니쉬™ (바닐라/초콜릿/곡물)</strong><p>식물성 단백질 20g | 한 끼 식사대용 체중조절</p><span class="price-tag">회원가 76,000~78,000원</span></div>
                  <div class="slide-product-item"><strong>트루쉐이프™</strong><p>공액리놀레산(CLA) | 체지방 분해</p><span class="price-tag">회원가 58,000원 / 37PV</span></div>
                  <div class="slide-product-item"><strong>오소린™</strong><p>유청단백질 가수분해물 | 근육 생성·단백질 보충</p><span class="price-tag">회원가 90,000원 / 58PV</span></div>
                  <div class="slide-product-item"><strong>파이토클렌즈 (ABC주스)</strong><p>그린새싹·당근오렌지·비트베리 20가지 야채</p><span class="price-tag">회원가 40,500원 / 26PV</span></div>
                  <div class="slide-product-item"><strong>차가 카페 / 글리코 카페 / 매나티</strong><p>차가버섯 커피 / 글리코 다이어트 커피 / 붓기차</p><span class="price-tag">회원가 33,000~34,000원</span></div>
                </div>
              </div>
            </div>
          </div>

        </div><!-- /catalog-slider -->
        <button class="slider-nav slider-next" id="sliderNext" aria-label="다음">&#8250;</button>
      </div>

      <div class="slide-dots" id="slideDots">
        <button class="dot active" data-dot="0"></button>
        <button class="dot" data-dot="1"></button>
        <button class="dot" data-dot="2"></button>
        <button class="dot" data-dot="3"></button>
        <button class="dot" data-dot="4"></button>
        <button class="dot" data-dot="5"></button>
        <button class="dot" data-dot="6"></button>
        <button class="dot" data-dot="7"></button>
      </div>
      <div class="slide-counter">
        <span id="slideCurrentNum">1</span> / <span id="slideTotalNum">8</span>
      </div>
    </div>
  </section>

  <!-- ===== TRUHEALTH CLEAN DIET BROCHURE SECTION ===== -->
  <section class="section th-brochure-section" id="truhealth">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">TruHealth Clean Diet</span>
        <h2 class="section-title">트루헬스 클린다이어트<br><em>브로셔 전체 보기</em></h2>
      </div>

      <div class="th-slider-wrap">
        <button class="th-nav th-prev" id="thPrev" aria-label="이전">&#8249;</button>
        <div class="th-slider" id="thSlider">
{TH_SLIDES_HTML}
        </div><!-- /th-slider -->
        <button class="th-nav th-next" id="thNext" aria-label="다음">&#8250;</button>
      </div>

      <div class="th-dots" id="thDots">
{TH_DOTS_HTML}
      </div>
      <div class="th-counter">
        <span id="thCurrentNum">1</span> / <span id="thTotalNum">13</span>
      </div>
    </div>
  </section>

  <!-- ===== LIGHTBOX OVERLAY ===== -->
  <div class="lightbox-overlay" id="lightboxOverlay">
    <button class="lightbox-close" id="lightboxClose">✕</button>
    <button class="lightbox-nav lightbox-prev" id="lightboxPrev">&#8249;</button>
    <div class="lightbox-content">
      <img src="" alt="" id="lightboxImg" />
      <p class="lightbox-caption" id="lightboxCaption"></p>
    </div>
    <button class="lightbox-nav lightbox-next" id="lightboxNext">&#8250;</button>
  </div>

  <!-- ===== SCIENCE SECTION ===== -->
  <section class="section science-section" id="science">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">SCIENCE</span>
        <h2 class="section-title">세계가 인정한<br><em>글리코영양소의 과학적 근거</em></h2>
      </div>
      <div class="science-grid">
        <div class="sci-card sci-card-featured">
          <div class="sci-card-badge">2012</div>
          <h3>NAS 중대 발표</h3>
          <p class="sci-org">National Academy of Sciences · 200명 이상 노벨 수상자들로 구성</p>
          <blockquote class="sci-quote">"Glycans play roles in almost every biological process and are involved in every major disease."</blockquote>
          <p class="sci-summary">당쇄는 거의 모든 생물학적 과정에 영향을 미치며, 모든 주요 질병에 관여한다.</p>
        </div>
        <div class="sci-card">
          <div class="sci-card-badge">2003</div>
          <h3>MIT 10대 신기술</h3>
          <p class="sci-org">MIT Technology Review</p>
          <p class="sci-content">글리코믹스(Glycomics)를 세상을 바꿀 10대 신기술로 선정</p>
          <div class="sci-tags"><span>분자 영상</span><span>양자 암호</span><span>글리코믹스</span></div>
        </div>
        <div class="sci-card">
          <div class="sci-card-badge">수상</div>
          <h3>노벨상 연구 연보</h3>
          <p class="sci-org">다수의 노벨 수상자 연구 성과</p>
          <ul class="sci-list">
            <li>2001 · 세포주기와 글리코영양소</li>
            <li>2000 · 신경계의 세포 커뮤니케이션</li>
            <li>1999 · 글리코영양소의 기능</li>
            <li>1998 · 산화질소</li>
            <li>1997 · 세포 감염의 생물학적 원리</li>
          </ul>
        </div>
        <div class="sci-card">
          <div class="sci-card-badge">149개</div>
          <h3>매나테크 보유 특허</h3>
          <p class="sci-org">대한민국 특허청 등록 (10-0450097)</p>
          <div class="patent-info">
            <div class="patent-row"><span class="patent-label">등록일</span><span>2004년 9월 30일</span></div>
            <div class="patent-row"><span class="patent-label">특허번호</span><span>10-0450097</span></div>
            <div class="patent-row"><span class="patent-label">분야</span><span>글리코영양소 조성물</span></div>
          </div>
        </div>
        <div class="sci-card sci-card-award">
          <div class="award-icon">🏆</div>
          <h3>2025 브랜드 고객충성도</h3>
          <h4 class="award-sub">면역기능개선식품 부문 <strong>1위</strong></h4>
          <p class="sci-org">Brand Customer Loyalty Index (BCLI) 2025</p>
          <p class="sci-content">대한민국 소비자들이 선택한 면역기능식품 분야 최고의 브랜드</p>
        </div>
        <div class="sci-card">
          <div class="sci-card-badge">2006</div>
          <h3>일본 Newton지 · 문부과학성</h3>
          <p class="sci-org">일본 학술 기관 공인</p>
          <ul class="sci-list">
            <li>뇌 기능 및 신경 근육과 당쇄</li>
            <li>면역 조절 과정에서의 당쇄 역할</li>
            <li>암과 당쇄의 상관관계</li>
            <li>글리코믹스와 생명 연구 특정 영역 지정</li>
          </ul>
        </div>
      </div>
      <div class="disease-section">
        <h3>글리코영양소 결핍 시 나타나는 증상</h3>
        <div class="disease-table-wrap">
          <table class="disease-table">
            <thead><tr><th>분류</th><th>관련 질환 및 증상</th></tr></thead>
            <tbody>
              <tr><td class="disease-cat">세포교통 오류</td><td>류마티스성 관절염, 골관절염, 루푸스, 피부근염, 다발성경화증, 당뇨병, 건선, 바이러스 감염</td></tr>
              <tr><td class="disease-cat">과면역반응</td><td>알레르기, 천식, 비염, 두드러기, 습진, 아토피, 환경적 독소 증후군</td></tr>
              <tr><td class="disease-cat">지면역반응</td><td>암, 세균감염(각종), 소화성궤양, 요도염, 바이러스성 감염, B형 및 C형 간염, AIDS, 갑상선염</td></tr>
              <tr><td class="disease-cat">뇌기능</td><td>학습장애, 주의집중장애, 행동장애, 알츠하이머, 파킨슨, 치매, 우울증, 과다행동 발작</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== BUSINESS SECTION ===== -->
  <section class="section business-section" id="business">
    <div class="container">
      <div class="section-header light">
        <span class="section-tag white">BUSINESS</span>
        <h2 class="section-title white">바로 여기<br><em>매나테크에 있습니다!</em></h2>
        <p class="section-desc white">오늘부터 나와 배우자의 소득이 없어진다면? — 은퇴 후 소득 없이 살아갈 40년에 대한 대처는 있으신가요?</p>
      </div>
      <div class="distrib-section">
        <h3 class="distrib-title">유통의 흐름 — 네트워크 마케팅(회원직접판매)</h3>
        <div class="distrib-compare">
          <div class="distrib-card traditional">
            <h4>전통적 유통</h4>
            <div class="distrib-flow"><span>기업</span><span class="arr">→</span><span>총판</span><span class="arr">→</span><span>대리점</span><span class="arr">→</span><span>소매</span><span class="arr">→</span><span>소비자</span></div>
            <p class="distrib-note">60% 유통마진 발생</p>
          </div>
          <div class="distrib-card network highlight-card">
            <h4>네트워크 마케팅 ✓</h4>
            <div class="distrib-flow"><span>기업</span><span class="arr">→</span><span class="highlight-span">회원사업자</span><span class="arr">→</span><span>소비자</span></div>
            <p class="distrib-note highlight-note">35% 사업자에게 환원 — 소비가 소득으로!</p>
          </div>
        </div>
      </div>
      <div class="stats-section">
        <h3>2023년 실소득 통계 — 업계 최상위 34.5% 후원수당</h3>
        <div class="stats-table-wrap">
          <table class="stats-table">
            <thead><tr><th>회사명</th><th>후원수당 지급률</th><th>연간 1인 평균 수당</th><th>연간 상위 1% 평균 수당</th></tr></thead>
            <tbody>
              <tr><td>암***</td><td>33.1%</td><td>1,123,800원</td><td>68,941,332원</td></tr>
              <tr><td>허***</td><td>34.8%</td><td>924,745원</td><td>56,231,511원</td></tr>
              <tr><td>피***</td><td>32.7%</td><td>1,550,353원</td><td>75,979,640원</td></tr>
              <tr><td>뉴***</td><td>34.5%</td><td>2,348,148원</td><td>114,051,411원</td></tr>
              <tr class="mannatech-row"><td><strong>매나테크 ★</strong></td><td><strong>34.5%</strong></td><td><strong>3,737,982원</strong></td><td><strong>146,855,736원</strong></td></tr>
              <tr><td>시***</td><td>30.6%</td><td>2,517,052원</td><td>142,057,487원</td></tr>
            </tbody>
          </table>
        </div>
        <p class="stats-source">출처: 2024 공정위 정보공개 자료</p>
      </div>
      <div class="cashflow-section">
        <h3>1%만 아는 부자들의 비밀 — 현금흐름 사분면</h3>
        <div class="cashflow-grid">
          <div class="cf-quad cf-e"><div class="cf-letter">E</div><div class="cf-name">직장인</div><p>고정 월급, 시간 교환형 수입</p></div>
          <div class="cf-quad cf-b"><div class="cf-letter">B</div><div class="cf-name">사업가</div><p>파이프라인 구축, 시스템 수입</p></div>
          <div class="cf-quad cf-s"><div class="cf-letter">S</div><div class="cf-name">전문직·자영업</div><p>고수입이지만 시간 구속</p></div>
          <div class="cf-quad cf-i"><div class="cf-letter">I</div><div class="cf-name">투자자</div><p>돈이 돈을 버는 구조</p></div>
        </div>
        <p class="cashflow-note">네트워크 마케팅 = <strong>B사분면</strong> — 평범한 사람도 파이프라인을 만들 수 있는 유일한 방법</p>
      </div>
    </div>
  </section>

  <!-- ===== COMPENSATION PLAN ===== -->
  <section class="section compensation-section" id="compensation">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">COMPENSATION</span>
        <h2 class="section-title">스마트 보상플랜<br><em>6가지 혜택으로 안정적 소득 실현</em></h2>
      </div>
      <div class="smart-plan">
        <h3 class="plan-title">스마트구독 80만원 (500PV) 시작</h3>
        <div class="plan-levels">
          <div class="plan-level">
            <div class="plan-level-circle start">나</div>
            <div class="plan-level-label">시작</div>
            <div class="plan-level-amount">80만원</div>
          </div>
          <div class="plan-arrow-h" aria-hidden="true">
            <svg viewBox="0 0 64 20" xmlns="http://www.w3.org/2000/svg">
              <line x1="0" y1="10" x2="52" y2="10" stroke="#9ca3af" stroke-width="2"/>
              <polygon points="52,4 64,10 52,16" fill="#9ca3af"/>
            </svg>
          </div>
          <div class="plan-level">
            <div class="plan-level-circle sd">SD</div>
            <div class="plan-level-label">4명 소개</div>
            <div class="plan-level-amount plan-earn">+ 32만원/월</div>
          </div>
          <div class="plan-arrow-h" aria-hidden="true">
            <svg viewBox="0 0 64 20" xmlns="http://www.w3.org/2000/svg">
              <line x1="0" y1="10" x2="52" y2="10" stroke="#9ca3af" stroke-width="2"/>
              <polygon points="52,4 64,10 52,16" fill="#9ca3af"/>
            </svg>
          </div>
          <div class="plan-level">
            <div class="plan-level-circle sed">SED</div>
            <div class="plan-level-label">확장</div>
            <div class="plan-level-amount plan-earn">+ 118만원/월</div>
          </div>
          <div class="plan-arrow-h" aria-hidden="true">
            <svg viewBox="0 0 64 20" xmlns="http://www.w3.org/2000/svg">
              <line x1="0" y1="10" x2="52" y2="10" stroke="#9ca3af" stroke-width="2"/>
              <polygon points="52,4 64,10 52,16" fill="#9ca3af"/>
            </svg>
          </div>
          <div class="plan-level">
            <div class="plan-level-circle pd">PD</div>
            <div class="plan-level-label">성장</div>
            <div class="plan-level-amount plan-earn">+ 450만원/월</div>
          </div>
          <div class="plan-arrow-h" aria-hidden="true">
            <svg viewBox="0 0 64 20" xmlns="http://www.w3.org/2000/svg">
              <line x1="0" y1="10" x2="52" y2="10" stroke="#9ca3af" stroke-width="2"/>
              <polygon points="52,4 64,10 52,16" fill="#9ca3af"/>
            </svg>
          </div>
          <div class="plan-level">
            <div class="plan-level-circle spd">SPD</div>
            <div class="plan-level-label">리더</div>
            <div class="plan-level-amount plan-earn">+ 1,800만원/월</div>
          </div>
        </div>
      </div>
      <div class="bonus-section">
        <h3>매나테크 보상플랜의 6가지 혜택</h3>
        <div class="bonus-grid">
          <div class="bonus-card"><div class="bonus-num">①</div><h4>비즈니스 개발 보너스</h4><p>사전 자격 조건 달성 후 지급되는 즉각적 성과 보너스</p></div>
          <div class="bonus-card"><div class="bonus-num">②</div><h4>유니레벨 보너스</h4><p>1~3단계 8% / 4~5단계 6% / 5~6단계 5% / 7단계 4%</p></div>
          <div class="bonus-card"><div class="bonus-num">③</div><h4>무한 보너스</h4><p>메인 레그 외 계열의 8단계 이하 0.5% 단계 무제한 인정</p></div>
          <div class="bonus-card"><div class="bonus-num">④</div><h4>멘토 보너스</h4><p>GA 3만원 / D 4만원 / SD 6만원 / GD 7.5만원 / ED이상 10만원</p></div>
          <div class="bonus-card"><div class="bonus-num">⑤</div><h4>매칭 보너스</h4><p>1~2세대 20% / 3~4세대 10% / 5~6세대 2.5%</p></div>
          <div class="bonus-card"><div class="bonus-num">⑥</div><h4>글로벌 보너스</h4><p>전세계 매출의 1.5%를 8PD이상 직급자에게 지분화하여 지급</p></div>
        </div>
      </div>
      <div class="so-section" id="so">
        <div class="so-header">
          <div class="so-logo">SO</div>
          <div>
            <h3>시스템 오너 (System Owner)</h3>
            <p>GL그룹에서 제공하는 모든 시스템을 무료로 제공받고, 정식 S.O미팅을 주관할 수 있는 사업자</p>
          </div>
        </div>
        <div class="so-compare">
          <div class="so-compare-col traditional">
            <h4>자영업자 사장님</h4>
            <ul>
              <li>창업 비용: 5천만 ~ 3억</li>
              <li>시간 투자: 경우에 따라 4~7일 집중</li>
              <li>리스크: 높음 (고정비, 투자금 회수)</li>
              <li>안세소득: 불가능</li>
              <li>시간적 자유: 불가능</li>
            </ul>
          </div>
          <div class="so-compare-col gl">
            <h4>GL그룹 S.O (시스템오너)</h4>
            <ul>
              <li>창업 비용: <strong>필요 없음 (무자본, 무점포)</strong></li>
              <li>시간 투자: <strong>평균 3~4일 파트타임 집중</strong></li>
              <li>리스크: <strong>없음 (무고정비, 투자금×)</strong></li>
              <li>안세소득: <strong>가능</strong></li>
              <li>시간적 자유: <strong>가능 (S.O배출을 통한 성장 기반)</strong></li>
            </ul>
          </div>
        </div>
        <div class="edu-system">
          <h4>글로벌리더스그룹의 검증된 성공 교육시스템</h4>
          <div class="edu-cycle">
            <div class="edu-step"><div class="edu-icon">📱</div><div class="edu-name">S.O.M 온라인 특강</div><div class="edu-desc">제품·사업 안내</div></div>
            <div class="edu-arr">→</div>
            <div class="edu-step featured"><div class="edu-icon">🎓</div><div class="edu-name">MBA</div><div class="edu-desc">매나테크 비즈니스 아카데미</div></div>
            <div class="edu-arr">→</div>
            <div class="edu-step"><div class="edu-icon">📋</div><div class="edu-name">MBS/MBT</div><div class="edu-desc">사업 실전 과정 1:1 양성</div></div>
            <div class="edu-arr">→</div>
            <div class="edu-step"><div class="edu-icon">🎤</div><div class="edu-name">GOPD 워크샵</div><div class="edu-desc">사업자 성장 시스템</div></div>
            <div class="edu-arr">→</div>
            <div class="edu-step"><div class="edu-icon">🏆</div><div class="edu-name">SO/PD 워크샵</div><div class="edu-desc">리더십 역량강화</div></div>
          </div>
          <p class="edu-tagline">평범한 사람이 리더로 성장할 수 있는 교육 프로그램을 갖춘 시스템 그룹</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ===== ONLINE MEDIA ===== -->
  <section class="section media-section" id="media">
    <div class="container">
      <div class="section-header light">
        <span class="section-tag white">ONLINE MEDIA</span>
        <h2 class="section-title white">언택트 시대에 온라인 매체의 활용은<br><em>선택이 아닌 필수</em></h2>
      </div>
      <div class="youtube-guide">
        <div class="yt-step">
          <div class="yt-num">①</div>
          <div class="yt-content"><h4>검색창에</h4><div class="yt-search-box">"글로벌리더스 그룹"</div></div>
        </div>
        <div class="yt-arrow">→</div>
        <div class="yt-step">
          <div class="yt-num">②</div>
          <div class="yt-content"><h4>"구독" 눌러주시고</h4><div class="yt-subscribe-btn">구독</div></div>
        </div>
        <div class="yt-arrow">→</div>
        <div class="yt-step">
          <div class="yt-num">③</div>
          <div class="yt-content"><h4>재생목록에서</h4><p>필요한 동영상 선택</p></div>
        </div>
      </div>
      <a class="yt-brand" href="https://www.happyglg.com/" target="_blank" rel="noopener noreferrer">
        <div class="yt-logo">▶</div>
        <div>
          <h3>매나테크글로벌리더스그룹 공식채널</h3>
          <p>유튜브 채널 | 사업 안내, 제품 설명, 성공 사례 영상 제공</p>
        </div>
      </a>
    </div>
  </section>

  <!-- ===== FAQ SECTION ===== -->
  <section class="section faq-section" id="faq">
    <div class="container">
      <div class="section-header">
        <span class="section-tag">FAQ</span>
        <h2 class="section-title">자주 묻는 질문들</h2>
      </div>
      <div class="faq-categories">
        <button class="faq-cat-btn active" data-cat="all">전체</button>
        <button class="faq-cat-btn" data-cat="network">네트워크 마케팅</button>
        <button class="faq-cat-btn" data-cat="product">제품</button>
        <button class="faq-cat-btn" data-cat="business">비즈니스</button>
        <button class="faq-cat-btn" data-cat="family">가족·지인</button>
      </div>
      <div class="faq-list" id="faqList">
        <div class="faq-item" data-cat="network"><button class="faq-q">Q. 네트워크마케팅 왜 이렇게 부정적일까요?<span class="faq-icon">+</span></button><div class="faq-a">과거 불법 다단계와의 혼동으로 인한 오해입니다. 매나테크는 NASDAQ 상장 기업으로 공정거래위원회의 정식 등록 업체이며, 합법적인 회원 직접판매 구조를 갖추고 있습니다.</div></div>
        <div class="faq-item" data-cat="network"><button class="faq-q">Q. 네트워크마케팅이 뭔가요?<span class="faq-icon">+</span></button><div class="faq-a">제품을 직접 소비하면서 그 경험을 지인에게 소개하고, 소비가 소득으로 연결되는 구조입니다. 전통 유통에서 발생하는 60% 유통마진 대신 35%를 사업자에게 환원하는 현대적 비즈니스 모델입니다.</div></div>
        <div class="faq-item" data-cat="business"><button class="faq-q">Q. 아는 사람이 없어도 성공이 가능할까요?<span class="faq-icon">+</span></button><div class="faq-a">네, 가능합니다. GL그룹의 체계적인 교육 시스템(MBA, MBS, SO 워크샵)과 온라인 마케팅 도구(유튜브 채널, SNS)를 통해 새로운 인맥을 형성하고 성장할 수 있습니다.</div></div>
        <div class="faq-item" data-cat="product"><button class="faq-q">Q. 매나테크 글리코영양소의 특징이 뭐예요?<span class="faq-icon">+</span></button><div class="faq-a">글리코영양소는 8개의 필수 단당류로 구성된 세포 커뮤니케이션의 핵심 영양소입니다. 세포와 세포 간의 정보 전달을 돕고, 면역 조절 및 해독 기능을 수행합니다. 매나테크는 이 분야에서 149개의 특허를 보유한 세계 유일의 기업입니다.</div></div>
        <div class="faq-item" data-cat="family"><button class="faq-q">Q. 남편이나 가족이 사업을 반대한다면 어떻게 하나요?<span class="faq-icon">+</span></button><div class="faq-a">처음에는 반대하는 경우가 많습니다. 하지만 직접 제품을 경험하고, GL그룹의 사업 설명회(MBA)에 함께 참여하면 이해가 깊어지는 경우가 대부분입니다. 가족의 동참이 가장 큰 힘이 됩니다.</div></div>
        <div class="faq-item" data-cat="business"><button class="faq-q">Q. 부업으로 시작해도 성공할 수 있을까요?<span class="faq-icon">+</span></button><div class="faq-a">네, 가능합니다. GL그룹 SO 시스템은 평균 3~4일의 파트타임 집중으로 운영할 수 있어, 직장을 유지하면서도 단계적으로 성장이 가능합니다.</div></div>
        <div class="faq-item" data-cat="product"><button class="faq-q">Q. 코로나19 이후 네트워크마케팅 전망은?<span class="faq-icon">+</span></button><div class="faq-a">언택트 시대를 맞아 온라인 비즈니스가 폭발적으로 성장했습니다. 건강기능식품 시장은 1조 달러 이상의 차세대 산업으로, 글리코영양소는 그 중심에 있습니다.</div></div>
        <div class="faq-item" data-cat="business"><button class="faq-q">Q. GL그룹만의 차별화된 성공 비결은?<span class="faq-icon">+</span></button><div class="faq-a">검증된 교육 시스템(S.O.M → MBA → MBS → GOPD → SO/PD), 유튜브 온라인 채널 활용, 그리고 무자본·무점포로 파트타임 운영 가능한 S.O 시스템이 핵심입니다.</div></div>
      </div>
    </div>
  </section>

  <!-- ===== CONTACT SECTION ===== -->
  <section class="section contact-section" id="contact">
    <div class="container">
      <div class="section-header light">
        <span class="section-tag white">CONTACT</span>
        <h2 class="section-title white">지금 시작하세요</h2>
        <p class="section-desc white">평범한 사람이 리더로 성장할 수 있는 기회, 지금 바로 문의하세요.</p>
      </div>
      <div class="contact-wrap">
        <div class="contact-info">
          <h3>GLG 매나테크 이야기</h3>
          <div class="contact-item"><span class="contact-icon">▶</span><div><strong>유튜브 채널</strong><p>검색창에 "글로벌리더스 그룹" 검색 후 구독</p></div></div>
          <div class="contact-item"><span class="contact-icon">🌐</span><div><strong>공식 홈페이지</strong><p>www.mannatech.com</p></div></div>
          <div class="contact-item"><span class="contact-icon">📋</span><div><strong>MANNATECH INDEPENDENT ASSOCIATE</strong><p>GLG 글로벌리더스그룹</p></div></div>
        </div>
        <form class="contact-form" id="contactForm">
          <div class="form-group"><label for="name">이름</label><input type="text" id="name" placeholder="성함을 입력해 주세요" /></div>
          <div class="form-group"><label for="phone">연락처</label><input type="tel" id="phone" placeholder="연락처를 입력해 주세요" /></div>
          <div class="form-group">
            <label for="interest">관심 분야</label>
            <select id="interest">
              <option value="">선택해 주세요</option>
              <option value="product">제품 구매 및 체험</option>
              <option value="business">비즈니스 사업 참여</option>
              <option value="info">정보 수집 및 학습</option>
              <option value="youtube">유튜브 채널 구독</option>
            </select>
          </div>
          <div class="form-group"><label for="message">메시지</label><textarea id="message" rows="4" placeholder="궁금하신 내용을 자유롭게 작성해 주세요"></textarea></div>
          <button type="submit" class="form-submit">문의 보내기</button>
        </form>
      </div>
    </div>
  </section>

  <!-- ===== FOOTER ===== -->
  <footer class="footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <div class="footer-logo"><span class="logo-glg">GLG</span><span class="logo-text">MANNATECH</span></div>
          <p>Special Mannatech — Transform Your Life</p>
          <p class="footer-sub">매나테크 이야기 | INDEPENDENT ASSOCIATE</p>
        </div>
        <div class="footer-links">
          <h4>바로가기</h4>
          <ul>
            <li><a href="#about">매나테크란</a></li>
            <li><a href="#product">제품 소개</a></li>
            <li><a href="#science">과학적 근거</a></li>
            <li><a href="#business">비즈니스</a></li>
            <li><a href="#compensation">보상플랜</a></li>
            <li><a href="#faq">FAQ</a></li>
          </ul>
        </div>
        <div class="footer-info">
          <h4>주요 수상 및 인증</h4>
          <ul>
            <li>🏆 2025 BCLI 면역기능식품 1위</li>
            <li>📜 특허 149개 보유</li>
            <li>🔬 NAS 공인 글리코사이언스</li>
            <li>🏛 NASDAQ 상장기업</li>
            <li>🌍 29개국 글로벌 운영</li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2025 Mannatech GLG Independent Associate. All rights reserved.</p>
        <p class="footer-disclaimer">본 웹사이트는 매나테크 독립 사업자가 운영합니다. 제품 효과는 개인에 따라 다를 수 있습니다.</p>
      </div>
    </div>
  </footer>

</div><!-- /#page-main -->


<!-- ╔══════════════════════════════════════════════════════╗
     ║  PAGE 2: PRICE COMPARISON                           ║
     ╚══════════════════════════════════════════════════════╝ -->
<div id="page-compare">

<!-- ══ TOPBAR ══ -->
<header class="topbar">
  <div class="topbar-logo">
    <svg width="26" height="26" viewBox="0 0 26 26" fill="none"><circle cx="13" cy="13" r="13" fill="rgba(116,198,157,.25)"/><path d="M8 13.5c0-2.76 2.24-5 5-5s5 2.24 5 5-2.24 5-5 5-5-2.24-5-5z" fill="#74c69d"/><circle cx="13" cy="13.5" r="2" fill="#fff"/></svg>
    Mannatech <span>GLG</span>
  </div>
  <button class="topbar-back-main" onclick="showMainPage()">
    ← 메인으로
  </button>
</header>

{pc_body_html}

</div><!-- /#page-compare -->


<!-- ════════════════════════════════════════════════════════
     SCRIPTS
     ════════════════════════════════════════════════════════ -->
<script>
/* ── Page switcher ── */
function showComparePage(e) {{
  if (e) e.preventDefault();
  document.body.classList.add('show-compare');
  document.getElementById('page-compare').scrollTop = 0;
  window.scrollTo(0, 0);
}}
function showMainPage() {{
  document.body.classList.remove('show-compare');
  window.scrollTo(0, 0);
}}
</script>

<script>
/* ════════════════════════════════════════════════════════
   MAIN SITE JS (main.js — catalog images already patched)
   ════════════════════════════════════════════════════════ */
{MAIN_JS}
</script>

<script>
/* ════════════════════════════════════════════════════════
   PRICE COMPARE JS
   ════════════════════════════════════════════════════════ */
{PC_JS}
</script>

<script>
/* ════════════════════════════════════════════════════════
   TRUHEALTH CLEAN DIET BROCHURE SLIDER JS
   ════════════════════════════════════════════════════════ */
{TH_JS}
</script>

</body>
</html>
"""

out_path = os.path.join(WEBAPP, 'mannatech-glg-complete.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

size_mb = os.path.getsize(out_path) / 1024 / 1024
print(f"\n✅ Done! Output: {out_path}")
print(f"   File size: {size_mb:.1f} MB")
