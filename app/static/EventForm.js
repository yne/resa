export default ({
	props: ['value'],
	data() {
		return {
			autofill: {
				squash: { min: 2, max: 8, step: 2 },
				tennis: { min: 2, max: 8, step: 2 },
				rugby: { min: 10, max: 20, step: 1 },
				padel: { min: 4, max: 8, step: 4 },
				badminton: { min: 2, max: 8, step: 2 },
				'sandwich techno': { min: 10, max: 40, step: 1 }
			},
			now: new Date((new Date()).getTime() - ((new Date()).getTimezoneOffset() * 60000)).toJSON()
		}
	},
	methods: {
		autocomplete(e) {
			const choices = this.autofill[e.target.value.toLowerCase()];
			if (!choices) return;
			for (let name in choices) {
				e.target.form[name].value = choices[name];
			}
		},
		create(body) {
			this.rest('/event/', 'POST', body).then(r => this.$emit('submit', r))
		},
		update(body, id) {
			this.rest(`/event/${id}`, 'PUT', body).then(r => this.$emit('submit', r))
		},
		remove(id, remain) {
			if (remain.length && !confirm(`They are still ${remain.length} participants\n Are you sure ?`)) return;
			this.rest(`/event/${id}`, 'DELETE').then(r => this.$emit('submit', r))
		},
	},
	template: `
<form v-if=value @submit.prevent="(value.id?update:create)($event.target.json(),value.id)">
	<datalist id=names>
		<option v-for="v,k in autofill">{{k}}</option>
	</datalist>
	<div class=row>
		<div class=col><label>Title</label><input @change=autocomplete name=title :value=value.title list=names required></div>
	</div>
	<div class=row>
		<div class=col><label>Descriptions</label><textarea name=detail :value=value.detail style=resize:vertical></textarea></div>
	</div>
	<div class=row>
		<div class=col><label>Date</label><input name=date :value=value.date  type=date :min=now.slice(0,10) required></div>
		<div class=col><label>Time</label><input name=time :value=value.time  type=time required></div>
	</div>
	<div class=row>
		<div class=col><label>Min</label><input name=min :value=value.min type=number min=1 placeholder="0"></div>
		<div class=col><label>Max</label><input name=max :value=value.max type=number :min=value.min placeholder="∞"></div>
		<div class=col><label>Step</label><input name=step :value=value.step type=number min=1 placeholder="1"></div>
	</div>
	<footer class=is-right>
		<input type=button class="button outline" @click.prevent="$emit('submit')" value=Cancel>
		<input type=button class="button outline text-error bd-error" v-if=value.id @click.prevent="remove(value.id, value.parts)" value=Remove>
		<button class="button primary">{{value.id?'Update':'Create'}}</button>
	</footer>
	<input name=id :value=value.id type=hidden v-if=value.id>
</form>
`,
})