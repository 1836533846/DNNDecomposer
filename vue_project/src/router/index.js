import Vue from "vue"
import VueRouter from "vue-router"

import MyComponent from '../components/MyComponent.vue'
import Modularization from '../components/Modularization.vue'
import Deployment from '../components/Deployment.vue'
import Benchmark from '../components/Benchmark'

Vue.use(VueRouter)


const router = new VueRouter({
    routes:[
        { path: '/', redirect:'/modularization' },
        { path:'/modularization', component: Modularization, meta:{title: 'SeaMGrad Modularization'}},
        { path:'/deployment', component: Deployment, meta:{title: 'SeaMGrad Deployment'}},
        { path:'/benchmark', component: Benchmark , meta:{title: 'SeaMGrad Deployment'}},
        { path:'/old', component: MyComponent , meta:{title: 'SeaMGrad Deployment'}},
    ]
})


router.beforeEach((to, from, next) => {
    if (to.meta.title) {
      document.title = to.meta.title
    }
    next()
  })


export default router

