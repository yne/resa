({props: ["id"],
  template: `<div v-if=recipe>
  <h1>{{recipe.name}} <small>by <router-link :to="{ name: 'user', params: { id: recipe.by }}">{{recipe.by}}</router-link></small></h1>
  <img v-for="photo in recipe.photos" :key=photo :src=photo>
  <ul>
    <li v-for="ingredient in recipe.ingredients" :key=ingredient.name>{{ingredient.name}} {{ingredient.amount}} {{ingredient.unit}}</li>
  </ul>
  <ol>
    <li v-for="step in recipe.steps" :key=step>{{step}}</li>
  </ol>
  </div>
  <div v-else-if="recipe===null">Loading</div>
  <div v-else>Error</div>`,
  methods: {
  },
  data: () => ({recipe:null}),
  watch: {
    id:{handler(id){this.$root.fetch(`recipe/${id}`).then(j=>this.recipe=j)}, immediate:true}
  }
})