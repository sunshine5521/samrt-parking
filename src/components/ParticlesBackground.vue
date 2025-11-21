<template>
  <div class="particles-container" @click="handleParticleClick">
    <!-- 使用CSS动画创建粒子效果 -->
    <div class="css-particles" :class="{ 'gathering': isGathering, 'ended': isEnded }"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';

// 定义事件 - 禁用ESLint检查，defineEmits是Vue的编译器宏
// eslint-disable-next-line no-undef
const emit = defineEmits(['particles-ended']);
console.log('ParticlesBackground组件已初始化，事件发射器已创建');

// 状态管理
const isGathering = ref(false);
const isEnded = ref(false);

// 处理粒子点击事件
const handleParticleClick = async (event) => {
  console.log('粒子效果被点击，event.target.classList:', event.target.classList);
  // 确保点击的是粒子容器而不是其他元素
  if (event.target.classList.contains('particles-container') || 
      event.target.classList.contains('css-particles')) {
    console.log('点击有效，开始聚集动画');
    // 开始聚集动画
    isGathering.value = true;
    console.log('isGathering设置为true');
    
    // 等待聚集动画完成（大约2秒）
    await new Promise(resolve => setTimeout(() => {
      console.log('聚集动画完成，等待结束');
      resolve();
    }, 2000));
    
    // 结束粒子效果
    isEnded.value = true;
    console.log('isEnded设置为true');
    
    // 显示登录界面
    console.log('准备调用showLoginScreen函数');
    await showLoginScreen();
    console.log('showLoginScreen函数执行完成');
  }
};

// 显示登录界面
  const showLoginScreen = () => {
    console.log('showLoginScreen函数被调用');
    return new Promise(resolve => {
      // 发出粒子效果结束事件，通知父组件
      console.log('发出particles-ended事件到父组件');
      emit('particles-ended');
      
      // 获取粒子容器元素并添加ended类
      console.log('尝试查找粒子容器元素');
      const particleContainer = document.querySelector('.particles-container');
      console.log('找到的粒子容器元素:', particleContainer);
      
      if (particleContainer) {
        // 直接在容器上添加ended类，用于CSS控制显示/隐藏
        particleContainer.classList.add('ended');
        console.log('已向粒子容器添加ended类');
      }
      
      // 获取登录界面元素（假设登录界面有login-container类）
      console.log('尝试查找登录界面元素');
      const loginContainer = document.querySelector('.login-container') || 
                            document.querySelector('.login-page') || 
                            document.querySelector('#app > div:not(.particles-container)');
      
      console.log('找到的登录容器元素:', loginContainer);
      
      if (loginContainer) {
        // 确保登录界面是可见的
        console.log('设置登录容器样式：display:block, opacity:0');
        loginContainer.style.display = 'block';
        loginContainer.style.opacity = '0';
        
        // 添加淡入动画
        setTimeout(() => {
          console.log('添加淡入动画：transition: opacity 1s ease-in, opacity:1');
          loginContainer.style.transition = 'opacity 1s ease-in';
          loginContainer.style.opacity = '1';
          console.log('淡入动画设置完成，resolve promise');
          resolve();
        }, 100); // 小延迟确保display属性生效
      } else {
        console.log('未找到登录容器元素，直接resolve');
        resolve(); // 如果找不到登录界面元素，直接 resolve
      }
    });
  };

onMounted(() => {
  console.log('粒子群特效已加载，点击任意位置结束特效并显示登录界面');
});
</script>

<style scoped>
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10; /* 确保粒子效果在登录界面之上 */
  overflow: hidden;
  cursor: pointer;
  transition: opacity 1s ease-out, visibility 1s ease-out;
  visibility: visible; /* 默认可见 */
}

.css-particles {
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, #1976d222 0%, #64b5f611 100%);
  position: relative;
  transition: all 0.3s ease;
}

/* 正常状态的粒子 */
.css-particles::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(#1976d2 1px, transparent 1px),
    radial-gradient(#64b5f6 1px, transparent 1px);
  background-size: 50px 50px;
  background-position: 0 0, 25px 25px;
  animation: particleMove 30s linear infinite;
  transition: all 2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.css-particles::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(#1976d2 2px, transparent 2px),
    radial-gradient(#64b5f6 2px, transparent 2px),
    radial-gradient(#1976d2 2px, transparent 2px),
    radial-gradient(#64b5f6 2px, transparent 2px),
    radial-gradient(#1976d2 2px, transparent 2px);
  background-size: 100px 100px;
  background-position: 
    10% 20%, 
    30% 40%, 
    50% 60%, 
    70% 80%, 
    90% 10%;
  animation: particleFloat 20s ease-in-out infinite alternate;
  transition: all 2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* 正常移动动画 */
@keyframes particleMove {
  0% {
    background-position: 0 0, 25px 25px;
  }
  100% {
    background-position: 500px 500px, 525px 525px;
  }
}

@keyframes particleFloat {
  0% {
    background-position: 
      10% 20%, 
      30% 40%, 
      50% 60%, 
      70% 80%, 
      90% 10%;
  }
  50% {
    background-position: 
      20% 30%, 
      40% 50%, 
      60% 70%, 
      80% 90%, 
      10% 20%;
  }
  100% {
    background-position: 
      15% 25%, 
      35% 45%, 
      55% 65%, 
      75% 85%, 
      5% 15%;
  }
}

/* 聚集动画状态 - 使用更醒目的黄色 */
.css-particles.gathering::before,
.css-particles.gathering::after {
  animation: none;
  background-size: 20px 20px;
  background-position: 50% 50% !important;
  opacity: 0.9;
  /* 更改颜色为黄色系，与背景形成强烈对比 */
  background-image: 
    radial-gradient(#FFD700 3px, transparent 3px),
    radial-gradient(#FFA500 3px, transparent 3px);
}

.css-particles.gathering {
  background: radial-gradient(ellipse at center, rgba(255, 215, 0, 0.4) 0%, rgba(255, 165, 0, 0.2) 100%);
}

/* 结束状态 */
.css-particles.ended::before,
.css-particles.ended::after {
  opacity: 0;
  transform: scale(0.5);
}

.css-particles.ended {
  background: transparent;
  opacity: 0;
  transform: scale(0.5);
}

/* 当粒子效果结束时 */
.particles-container {
  transition: all 1s ease-out;
}

.particles-container.ended {
  z-index: -1;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}
</style>
