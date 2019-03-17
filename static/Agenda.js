export default ({
data: () => ({ events: undefined, view: {} }),
async created() {
	this.events = (await rest("/event/")).sort((a, b) => a.date + a.time < b.date + b.time);
	let today = (new Date()).toJSON().slice(0, 10);
	this.view.today = this.events.filter(e => e.date == today);
	this.view.upcomming = this.events.filter(e => e.date > today);
	// this.view.archive = this.events.filter(e => e.date < today);
},
template: `
<section>
	<article v-for="(events, type) in view">
		<h3 class=is-text-capitalize>{{type}}</h3>
		<ul v-if=events.length>
			<li v-for="event in events">
				<template v-if="type!='today'">{{event.date}}</template>
				{{event.time}}
				<router-link :to="{name:'event', params:{id:event.id}}">
					{{event.title}}
				</router-link>
				by
				<router-link :to="{name:'user', params:{id:event.owner}}">{{event.owner}}</router-link>
			</li>
		</ul>
		<p v-else class=text-light>Nobody here but us chickens</p>
	</article>
	<p v-if="events===undefined">Loading</p>
	<p v-if="events===null">Not Found</p>
</section>`,
})