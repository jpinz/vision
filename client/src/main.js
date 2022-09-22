import Vue from 'vue'
import App from './App.vue'
import WebCam from 'vue-web-cam'

Vue.config.productionTip = false
Vue.config.devtools = true

Vue.use(WebCam)

new Vue({
  render: h => h(App),
}).$mount('#app')
