const Days = ['dim', 'lun', 'mar', 'mer', 'jeu', 'ven', 'sam'];
const Mois = ['jan', 'fev', 'mar', 'avr', 'mai', 'juin', 'juill', "aout", "sept", "oct", "nov", "dec"];
const Week = 7 * 24 * 60 * 60 * 1000;
export default {
  props: ['event'],
  data: () => ({ now: new Date() }),
  methods: {
    moment(dateStr) {
      const date = new Date(dateStr);
      if (date < +this.now + Week)
        return Days[date.getDay()]
      if (date.getMonth() == this.now.getMonth())
        return Days[date.getDay()] + ' ' + dateStr.substring(8, 10)
      return dateStr.substring(8, 10) + ' ' + Mois[+dateStr.substring(5, 7) - 1]
    },
    join(event, btn) {
      btn.disabled = true;
      this.rest(`/event/${event.id}/part`, 'POST', {})
        .then(e => btn.disabled = false)
        .then(e => this.$emit('change'))
    },
    leave(event, btn) {
      const part = event.parts.find(p => p.user == this.$auth.get.name);
      // if (!confirm('Your ranking will be lost.\nContinue ?')) return;
      btn.disabled = true;
      part && this.rest(`/event/${event.id}/part/${part.id}`, 'DELETE')
        .then(e => btn.disabled = false)
        .then(e => this.$emit('change'))
    },
    save(event, part, data) {
      console.log(this)
      this.rest(`/event/${event.id}/part/${part.id}`, 'PUT', data)
        .then(e => this.$emit('change'))
    },
  },
  template: `<div>
<span class="col-2 text-grey is-text-right" :title=event.date>{{moment(event.date)}} {{event.time}}</span>
<span class=col>
	<div>
		<strong>{{event.title}}</strong>
		<span class=text-grey>{{event.detail}}</span>
	</div>
	<details v-if=event.parts.length>
		<summary>
			With <span v-for="(p,i) in event.parts" :class="p.queue?'text-grey':null"><template v-if="i&&i!=event.parts.length">, </template>{{p.user}} {{p.message}}</span>
		</summary>
		<ul>
			<li v-for="p in event.parts" :class=p.queue>
				<form v-if="$auth.get.name==p.user" class=grouped @submit.prevent=save(event,p,$event.target.json())>
					<span :class="p.queue?'text-grey':null" style="margin:auto .5em auto 0">{{p.user}}</span>
					<input name=message :value=p.message placeholder=Message>
					<button class="button outline primary">Save</button>
				</form>
				<span v-else :class="p.queue?'text-grey':null">{{p.user}} {{p.message}}</span>
			</li>
		</ul>
	</details>
	<div v-else class=text-light>Nobody joined, yet !</div>
</span>
<span class="col-3 is-text-right" v-if=$auth.get.name>
	<button class="button outline bd-error text-error"  @click.prevent="leave(event,$event.target)" v-if="event.parts.filter(p=>p.user==$auth.get.name).length">Quit</button>
	<button class="button outline primary" @click.prevent="join(event,$event.target)" v-else>Join</button>
	<button class="button primary" @click="$emit('edit',event)" v-if="$auth.get.name==event.owner">Edit</button>
</span>
</div>`
}
