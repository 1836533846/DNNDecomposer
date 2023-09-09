
import Vue from 'vue'
import App from './App.vue'
import VueSocketIO from 'vue-socket.io'
import 'font-awesome/css/font-awesome.min.css';


// Vue.config.productionTip = false

Vue.use(new VueSocketIO({
  debug: true,
  connection: 'http://localhost:5000' // the address of your Flask server
}))

new Vue({
render: h => h(App),
}).$mount('#app')
