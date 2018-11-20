const $auth = {install (Vue, options) {
	let name = 'token'; // localStorage name
	Vue.mixin({
		data: function() {
			return {
				get $token() {return localStorage[name]},
				set $token(jwt) {console.log("set",localStorage[name]=jwt||"")},
			}
		},
		computed: {
			$auth: {
				get() {return JSON.parse(atob((this.$root.$data.$token||'.bnVsbA==.').split('.')[1]))},
			}
		},
		methods: {
			fetch(formOrPath, params = {}) {
				params.headers = localStorage.token ? { Authorization: `Bearer ${localStorage.token}` } : {};
				if (formOrPath instanceof HTMLFormElement) {
					params.method = (formOrPath.attributes.method||{}).value || 'GET';
					if (params.method.toUpperCase()=='POST')
						params.body = new FormData(formOrPath);
					else
						params.query = new URLSearchParams(new FormData(formOrPath));
					params.path = new URL(formOrPath.action).pathname;
				} else {
					params.path = formOrPath;
					params.query = Object.keys(params.query||{}).map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params.query[k])).join('&');
				}
				return fetch(`${params.path}?${params.query}`, params).then(r => {
					if (!r.ok) throw Error(r.statusText);
					return params.Text ? r.text() : r.json();
				})
			}
		}
	})
}};
export default $auth;
Vue.use($auth);