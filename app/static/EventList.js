import EventForm from "/static/EventForm.js";
import EventRow from "/static/EventRow.js";


export default {
	components: { EventForm, EventRow },
	data: () => ({ events: undefined, dialogEvent: undefined, list: 'future', open: false }),
	created() {
		this.load()
	},
	mounted() {
		dialogPolyfill.registerDialog(this.$refs.dialog);
	},
	methods: {
		load() {
			this.rest(`/event/${this.list}`).then(e => this.events = e.sort((a, b) => a.date.localeCompare(b.date)))
		},
		submit(promise) {
			this.$refs.dialog.close();
			this.load();
		},
		form(event = undefined) {
			const now = new Date((new Date()).getTime() - ((new Date()).getTimezoneOffset() * 60000)).toJSON()
			this.dialogEvent = event || { date: now.slice(0, 10), time: now.slice(11, 16) };
			this.$refs.dialog.showModal();
		},
	},
	template: `
<section>
	<dialog ref=dialog class=card><event-form @submit=submit :value=dialogEvent /></dialog>
	<div class=grouped>
		<select v-model=list @change=load>
			<option value=future selected>Upcomming Events</option>
			<option value=past>Archived Events</option>
		</select>
		<button v-if=$auth.get.name class="button primary" @click=form()>Create</button>
	</div>
	<hr/>
	<p v-if="events === undefined">Loading</p>
	<p v-if="events === null">Not Found</p>
	<table class=striped v-if="events&&events.length">
		<tr v-for="event in events">
			<td><event-row :event=event class=row @change=load @edit=form /></td>
		</tr>
	</table>
	<p v-if="events && !events.length" class=text-grey>No event !</p>
</section>`,
}