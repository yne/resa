export default {
	template:`
<main>
	<code>Root:{{$auth}}</code>
	<code>Root:{{$data.$token}}</code>
	<router-link v-if=$auth :to="{name:'user',params:{id:42}}">USER42</router-link>
	<router-link v-if=$auth :to="{name:'event',params:{id:42}}">EVENT42</router-link>
</main>`,
	methods:{
	}
}
