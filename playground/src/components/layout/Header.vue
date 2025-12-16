<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">🔷</span>
          <div class="logo-text">
            <h1>SHACL UI Widget Scoring</h1>
            <p class="subtitle">Data Shapes WG Playground</p>
          </div>
        </div>
      </div>
      <div class="header-right">
        <a
          href="https://www.w3.org/groups/wg/data-shapes/"
          target="_blank"
          rel="noopener noreferrer"
          class="header-link"
          aria-label="W3C Data Shapes Working Group"
        >
          <span class="link-icon">🌐</span>
          <span class="link-text">Data Shapes WG</span>
        </a>
        <a
          href="https://github.com/kurrawong/shui-widget-scoring"
          target="_blank"
          rel="noopener noreferrer"
          class="header-link"
          aria-label="View on GitHub"
        >
          <span class="link-icon">⚙️</span>
          <span class="link-text">GitHub</span>
        </a>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #252526 0%, #2d2d30 100%);
  border-bottom: 2px solid #007acc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 10;
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #007acc 0%, #4ec9b0 50%, #007acc 100%);
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  max-width: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  font-size: 32px;
  filter: drop-shadow(0 2px 4px rgba(0, 122, 204, 0.4));
}

.logo-text h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.subtitle {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #9cdcfe;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(62, 62, 66, 0.6);
  border: 1px solid #3e3e42;
  border-radius: 6px;
  color: #cccccc;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-link:hover {
  background: #3e3e42;
  border-color: #007acc;
  color: #ffffff;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 122, 204, 0.3);
}

.header-link:focus-visible {
  outline: 2px solid #007acc;
  outline-offset: 2px;
}

.link-icon {
  font-size: 14px;
}

.link-text {
  white-space: nowrap;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .logo-text h1 {
    font-size: 16px;
  }

  .subtitle {
    font-size: 11px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
  }

  .link-text {
    display: none;
  }

  .header-link {
    padding: 8px 10px;
  }
}
</style>
