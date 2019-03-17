export default ({
props: ['id'],
watch: { id: { handler: 'load', immediate: true } },
data() {
	return {
		data: undefined,
		names: ['Squash', 'Tennis', 'Rugby', 'Badmington', 'Sandwich Techno', 'Vernissage'],
		token: localStorage.token,
		now: new Date((new Date()).getTime() - ((new Date()).getTimezoneOffset() * 60000)).toJSON()
	}
},
computed: {
	user: function () { return (this.token ? JSON.parse(atob(this.token.split('.')[1])) : {}).user },
	participants: function () { return ((this.data || {}).part || []).map(p => p.user); },
	mails: function () { return this.participants.map(p => p + '@toulouse.viveris.fr').join(); },
},
methods: {
	form:form,
	async load(force) {
		if (force || (this.$props.id && !(this.data || {}).id))
			this.data = await rest(`/event/${this.id}`);
		else if (!this.id)
			this.data = {
				date: this.now.slice(0, 10),
				time: this.now.slice(11, 16),
			}
	},
	async create(body) {
		const id = await rest('/event/', 'POST', body)
		this.$router.push({ name: 'event', params: { id } })
	},
	async update(body, id) {
		await rest(`/event/${id}`, 'PUT', body)
		this.load(true)
	},
	async remove(id) {
		if (this.participants.length && !confirm('They are still some participants\n Are you sure ?')) return;
		await rest(`/event/${id}`, 'DELETE')
		this.$router.push({ name: 'events' })
	},
	async join(id) {
		await rest(`/join/`, 'POST', { event: id })
		this.load(true)
	},
	async leave(id = null) {
		if (!id) id = this.data.part.find(p => p.user == this.user).id
		// if (!confirm('Your ranking will be lost.\nAre you sure ?')) return;
		await rest(`/join/${id}`, 'DELETE')
		this.load(true)
	},
},
template: `
<form v-if=data @submit.prevent="(id?update:create)(form($event.target),id)">
	<blockquote v-if="!user">You must be <router-link :to="{name:'me'}">logged</router-link> to create an event</blockquote>
	<fieldset :disabled='!user || (id && user!=data.owner)'>
		<legend>
			<router-link :to="{name:'user', params:{id:data.owner}}">{{data.owner}}</router-link>
			Event {{id?'':'create'}}
		</legend>
		<div class=row>
			<input class="col is-text-center" name=title :value=data.title list=names placeholder="Name" required>
			<datalist id=names>
				<option v-for="t in names" :value=t>{{t}}</option>
			</datalist>
		</div>

		<div class=row>
			<div class=col><label>Date:</label><input name=date  :value=data.date  type=date :min=now.slice(0,10) required></div>
			<div class=col><label>Time:</label><input name=time  :value=data.time  type=time required></div>
			<div class=col><label>Seats:</label><input name=total :value=data.total type=number min=1 placeholder="unlimited"></div>
		</div>
		<div class=is-right v-if="!id || user==data.owner">
			<button class="button outline" v-if=id @click.prevent=remove(id)>Remove</button>
			<button class="button primary">{{id?'Update':'Create'}}</button>
		</div>
		<input name=id :value=data.id type=hidden v-if=data.id>
	</fieldset>
	<div v-if='id && data.part'>
		<h4>Participants:</h4>
		<ul v-if="data.part && data.part.length">
			<li v-for="(p,i) in data.part">
				<router-link :to="{name:'user', params:{id:p.user}}">{{p.user}}</router-link>
				<span class="tag is-small" v-if="data.total && i>=data.total">in queue</span>
				<button v-if="user==data.owner" class="button error" style='padding: 0.5rem 1rem;margin: 3px;' @click.prevent=leave(p.id)>&times;</button>
			</li>
		</ul>
		<p v-else class=text-light>Empty</p>

		<div v-if=data.part>
			<a v-if=data.part.length class="button outline" :href="'mailto:'+mails">Mail</a>
			<button v-if="user && participants.indexOf(user)<0" class="button outline primary" @click.prevent=join(id)>Join</button>
			<button v-if="user && participants.indexOf(user)>=0" class="button error" @click.prevent=leave()>Leave</button>
		</div>
	</div>
</form>
<p v-else-if="data===undefined">Loading</p>
<p v-else-if="data===null">No such event</p>
<p v-else-if="data===0">Server error</p>
`,})