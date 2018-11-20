
//Vue.prototype.$toaster = new (Vue.extend(Toaster))({propsData: options})

export default {
	name : "Toaster",
	template: `<ul><li v-for="i in items" :key="i.key">{{i.message}}</li></ul>`,
	methods:{
		toggle(){
			console.log(42)
		}
	}
}
