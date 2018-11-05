({
  template: `<nav>
  <router-link :to="{ name: 'home'}">Logo</router-link>
  <form action=token method=POST class=flex>
    <input name=user placeholder=user type=text class=shrink>
    <input name=pass placeholder=pass type=password class=shrink>
    <input type=submit value="Sign in">
  </form>
  <router-link :to="{ name: 'recipe', params: { id: 123 }}">Cake</router-link>
  <router-link :to="{ name: 'user', params: { id: 123 }}">Sign up</router-link>
  </nav>`,
  data: () => ({
    isSignin:0
  })
})