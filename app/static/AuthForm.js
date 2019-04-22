export default {
  mounted(){
    dialogPolyfill.registerDialog(this.$refs.login);
  },
  template: `<div>
  <p style="margin: .2em 0 0 1em;">
    <button v-if=$auth.get.name class="is-full-width button outline text-error bd-error" @click.prevent="rest(/auth/, 'DELETE').then($auth.logout)">logout</button>
    <button v-else class="is-full-width button primary" @click.prevent="$refs.login.showModal()">login</button>
  </p>
  <dialog ref=login class=card>
    <form method=dialog @submit="rest(/auth/, 'POST', $event.target.json()).then($auth.login)">
      <p><input name=username required placeholder="prenom.nom" pattern="\\w+\\.\\w+" title="firstname.familyname"></p>
      <p><input name=password required type=password placeholder="LDAP password"></p>
      <footer class=is-right>
        <input type=button class=button @click.prevent="$event.target.closest('dialog').close()" value=Cancel>
        <button class="button primary">Login</button>
      </footer>
    </form>
  </dialog>
</div>
`,
}