function plugin(Vue, options = {}) {
  if (plugin.installed) return;
  Vue.auth = new Vue({
    data() { return { cookie: document.cookie } },
    computed: {
      get() {
        let toObj = (tuple) => {const [k,v] = tuple.trim().split('='); return {[k]:v};}
        let res = this.cookie.split(';').reduce((res, c) => Object.assign(res, toObj(c)), {});
        return res.payload ? JSON.parse(atob(res.payload)) : {}
      }
    },
    methods: {
      login() { this.cookie = document.cookie },
      logout() { this.cookie = document.cookie },
    }
  });
  Object.defineProperty(Vue.prototype, '$auth', { get() { return Vue.auth; } });
}


if (typeof window !== 'undefined' && window.Vue) {
  window.Vue.use(plugin);
}
export default plugin;