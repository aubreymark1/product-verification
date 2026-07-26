<template>
  <section class="phone-preview-shell">
    <div class="phone-frame">
      <div class="dynamic-island" aria-hidden="true"></div>
      <div class="status-bar" aria-hidden="true">
        <span>12:51</span>
        <div class="status-right"><span>5G</span><span>73%</span></div>
      </div>
      <main class="phone-content"><slot /></main>
    </div>
  </section>
</template>

<style scoped>
.phone-preview-shell {
  min-height: 100%;
  padding: 28px 16px;
  display: grid;
  place-items: center;
  background: #ececee;
  box-sizing: border-box;
}

.phone-frame {
  position: relative;
  width: min(100%, 430px);
  height: min(820px, calc(100dvh - 56px));
  min-height: 620px;
  overflow: hidden;
  background: #f7f7f8;
  border: 9px solid #161823;
  border-radius: 42px;
  box-shadow: 0 22px 52px rgba(22, 24, 35, 0.22);
}

.dynamic-island {
  position: absolute;
  z-index: 2;
  top: 12px;
  left: 50%;
  width: 112px;
  height: 28px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: #000;
}

.status-bar {
  position: absolute;
  z-index: 1;
  top: 0;
  right: 0;
  left: 0;
  height: 48px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #161823;
  font-size: 13px;
  font-weight: 700;
  background: #ffffff;
  box-sizing: border-box;
}

.status-right { display: flex; gap: 8px; }

.phone-content {
  height: 100%;
  padding-top: 48px;
  overflow-y: auto;
  overscroll-behavior: contain;
  box-sizing: border-box;
  scrollbar-width: none;
}

.phone-content::-webkit-scrollbar { display: none; }

@media (max-width: 480px) {
  .phone-preview-shell { padding: 0; }
  .phone-frame {
    width: 100%;
    height: 100dvh;
    min-height: 0;
    border: 0;
    border-radius: 0;
  }
}
</style>
