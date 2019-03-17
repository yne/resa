export default ({
props: ['id'],
watch: { id: { handler: 'load', immediate: true } },
data() {
	return {
		token: localStorage.token,
		events: undefined,
	}
},
computed: {
	user: function () { return (this.token ? JSON.parse(atob(this.token.split('.')[1])) : {user:''}).user },
	_id: function () { return this.id || this.user },
},
methods: {
	async load() {
		//if(!this.id)this.id=this.user;
		if(this._id)this.events = await rest(`/join/?user=${this._id}`)
	},
	async login(f) {
		if (this.token = await rest("/token", 'POST', form(f))) {
			localStorage.token = this.token;
			this.$router.push({ name: 'user', params: { id: this.user } });
		}
	},
	logout() {
		this.token = localStorage.token = ''
		this.$router.push({ name: 'me' })
	},
},
template: `
<section>
	<form @submit.prevent=login($event.target)>
		<button v-if=token @click.prevent=logout class="button error pull-right">Logout {{user}}</button>
		<div v-if="!token && !id" class=grouped>
			<input name=user placeholder="LDAP username" required>
			<input name=pass placeholder="LDAP password" required type=password>
			<button class="button primary">login</button>
		</div>
	</form>
	<h2 v-if=_id>{{_id}} joined:</h2>
	<template v-if="_id || user">
		<ul v-if='events && events.length'>
			<li v-for='event in events'>
				{{event.date}} {{event.time}}
				<router-link :to="{name:'event', params:{id:event.event}}">
					{{event.title}}
				</router-link>
				<cite>{{event.message}}</cite>
			</li>
		</ul>
		<span v-else class=text-light>Nothing</span>
	</template>
</section>`,
})