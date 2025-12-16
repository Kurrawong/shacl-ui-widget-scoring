<template>
  <footer class="app-footer">
    <div class="footer-content">
      <div class="footer-left">
        <p class="copyright">
          © 2026 <a href="https://www.w3.org/groups/wg/data-shapes/" target="_blank" rel="noopener noreferrer">W3C Data Shapes Working Group</a>
        </p>
        <div class="footer-links">
          <a href="https://w3c.github.io/data-shapes/shacl12-ui/" target="_blank" rel="noopener noreferrer">SHACL 1.2 User-Interfaces</a>
        </div>
      </div>
      <div class="footer-right">
        <p class="powered-by">
          Powered by <a href="https://pyodide.org/" target="_blank" rel="noopener noreferrer">Pyodide</a> & <a href="https://vuejs.org/" target="_blank" rel="noopener noreferrer">Vue 3</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: #252526;
  border-top: 1px solid #3e3e42;
  padding: 16px 24px;
  font-size: 12px;
  color: #858585;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.2);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  max-width: 100%;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.copyright {
  margin: 0;
  color: #858585;
}

.copyright a {
  color: #9cdcfe;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.copyright a:hover {
  color: #4ec9b0;
  text-decoration: underline;
}

.footer-links {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.footer-links a {
  color: #9cdcfe;
  text-decoration: none;
  transition: color 0.2s;
  font-weight: 500;
}

.footer-links a:hover {
  color: #4ec9b0;
  text-decoration: underline;
}

.separator {
  color: #3e3e42;
}

.footer-right {
  display: flex;
  align-items: center;
}

.powered-by {
  margin: 0;
  color: #858585;
}

.powered-by a {
  color: #9cdcfe;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.powered-by a:hover {
  color: #4ec9b0;
  text-decoration: underline;
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .footer-right {
    width: 100%;
  }
}
</style>
