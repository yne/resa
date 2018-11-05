({
  template: `
  <form action=recipe @submit.prevent=$root.fetch class=flex>
  <input type=search name=q placeholder="Ingredients... (ex. beef, apple:3, milk:500ml)" @change="validate()" list=ingredients>
  <input type=submit value=search>
  <datalist id=ingredients><option v-for="i in ingredients" :key=i.name :value=i.name>{{i.name}} ({{i.unit}})</option></datalist>
  </form>`,
  data : () => ({
    ingredients:[],
  }),
  created() {
    this.$root.fetch("ingredient")
    .then(j => this.ingredients=j)
    .catch(console.error);
  },
  methods: {
    validate() {
      console.log(this);
    },
  }
})