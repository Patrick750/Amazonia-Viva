<script setup>
import heroImage from '@/assets/public/IMG_2820.JPG'
import logoImage from '@/assets/public/amazon_logo.png'

defineProps({
  wide: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <main class="auth-page">
    <section :class="['auth-layout', { 'auth-layout--wide': wide }]">
      <aside class="auth-story" aria-label="Amazonia Viva">
        <img :src="heroImage" alt="" class="auth-story__image" aria-hidden="true" />
        <div class="auth-story__shade" aria-hidden="true"></div>

        <router-link to="/" class="auth-brand auth-brand--light" aria-label="Ir al inicio de Amazonia Viva">
          <span class="auth-brand__mark">
            <img :src="logoImage" alt="" />
          </span>
          <span>Amazonia Viva</span>
        </router-link>

        <div class="auth-story__content">
          <p class="auth-story__label">Turismo que conecta</p>
          <h2>Descubre la Amazonía con quienes la conocen.</h2>
          <p>Encuentra experiencias locales, organiza tu viaje y conecta con agencias y proveedores de la región.</p>
        </div>

        <p class="auth-story__footer">Experiencias, naturaleza y comunidades en un solo lugar.</p>
      </aside>

      <div class="auth-panel">
        <div class="auth-panel__mobile-brand">
          <router-link to="/" class="auth-brand" aria-label="Ir al inicio de Amazonia Viva">
            <span class="auth-brand__mark">
              <img :src="logoImage" alt="" />
            </span>
            <span>Amazonia Viva</span>
          </router-link>
        </div>

        <div class="auth-panel__content">
          <slot />
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  min-height: 100svh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: #f2f5f0;
  color: #17221a;
}

.auth-layout {
  width: min(1080px, 100%);
  min-height: min(760px, calc(100svh - 48px));
  display: grid;
  grid-template-columns: minmax(360px, 1.05fr) minmax(430px, 0.95fr);
  overflow: hidden;
  border: 1px solid #dce5dc;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(32, 58, 39, 0.13);
}

.auth-layout--wide {
  width: min(1240px, 100%);
  grid-template-columns: minmax(340px, 0.8fr) minmax(570px, 1.2fr);
}

.auth-story {
  position: relative;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100%;
  padding: 38px 42px;
  color: #fff;
}

.auth-story__image,
.auth-story__shade {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.auth-story__image {
  z-index: -2;
  object-fit: cover;
  object-position: center;
}

.auth-story__shade {
  z-index: -1;
  background: linear-gradient(180deg, rgba(8, 36, 23, 0.58), rgba(8, 36, 23, 0.84));
}

.auth-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: fit-content;
  color: #17351f;
  font-size: 1rem;
  font-weight: 800;
  text-decoration: none;
}

.auth-brand--light {
  color: #fff;
}

.auth-brand__mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.94);
}

.auth-brand__mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.auth-story__content {
  max-width: 440px;
}

.auth-story__label {
  margin-bottom: 12px;
  color: #bde8c8;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.auth-story__content h2 {
  max-width: 12ch;
  margin: 0 0 20px;
  font-size: clamp(2.4rem, 4.2vw, 4.25rem);
  font-weight: 800;
  line-height: 0.98;
  letter-spacing: -0.035em;
}

.auth-story__content p:last-child {
  max-width: 42ch;
  margin: 0;
  color: #e0ebe3;
  font-size: 1rem;
  line-height: 1.7;
}

.auth-story__footer {
  margin: 0;
  color: #d9e7dc;
  font-size: 0.82rem;
}

.auth-panel {
  display: flex;
  flex-direction: column;
  background: #fff;
}

.auth-panel__mobile-brand {
  display: none;
}

.auth-panel__content {
  width: 100%;
  max-width: 660px;
  margin: auto;
  padding: 48px clamp(32px, 5vw, 68px);
}

@media (max-width: 860px) {
  .auth-page {
    display: block;
    padding: 0;
    background: #fff;
  }

  .auth-layout,
  .auth-layout--wide {
    display: block;
    min-height: 100svh;
    border: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .auth-story {
    display: none;
  }

  .auth-panel__mobile-brand {
    display: block;
    padding: 22px 24px 0;
  }

  .auth-panel__content {
    max-width: 680px;
    padding: 38px 24px 48px;
  }
}

@media (max-width: 420px) {
  .auth-panel__mobile-brand {
    padding-inline: 18px;
  }

  .auth-panel__content {
    padding-inline: 18px;
  }
}
</style>
