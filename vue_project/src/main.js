
import Vue from 'vue'
import App from './App.vue'
import router from './router/index'
// Vue.use(router)

import ElementUI from 'element-ui';
// import 'element-ui/lib/theme-chalk/index.css';
// import 'Mystyle/theme/index.css';
import '../src/theme/Mystyle/theme/index.css'
Vue.use(ElementUI)


import VueSocketIO from 'vue-socket.io'
import 'font-awesome/css/font-awesome.min.css';


// Vue.config.productionTip = false

Vue.use(new VueSocketIO({
  debug: true,
  connection: 'http://localhost:5000', // the address of your Flask server
  // connection: 'http://192.168.3.241:5000', // the address of your Flask server
  // options: {
  //   withCredentials: true,
  //   extraHeaders: {}
  // }
}))


new Vue({
  render: h => h(App),
  router,
}).$mount('#app')
