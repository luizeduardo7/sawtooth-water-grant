/**
 * Copyright 2018 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------------
 */
'use strict'

// These requires inform webpack which styles to build
require('bootstrap')
require('../styles/main.scss')

const m = require('mithril')

const api = require('./services/api')
const navigation = require('./components/navigation')

const UserList = require('./views/user_list')
const UserDetailPage = require('./views/user_detail')
const RegisterSensorForm = require('./views/register_sensor_form')
const Dashboard = require('./views/dashboard')
const LoginForm = require('./views/login_form')
const SensorList = require('./views/sensor_list')
const SensorDetailPage = require('./views/sensor_detail')
const SignupForm = require('./views/signup_form')

/**
 * A basic layout component that adds the navbar to the view.
 */
const Layout = {
  view (vnode) {
    return [
      vnode.attrs.navbar,
      m('.content.container', vnode.children)
    ]
  }
}

const loggedInNav = () => {
  const links = [
    ['/register', 'Registrar Sensor'],
    ['/sensors', 'Ver Registro de Sensores'],
    ['/users', 'Ver Usuários']
  ]
  return m(navigation.Navbar, {}, [
    navigation.links(links),
    navigation.link('/profile', 'Perfil'),
    navigation.button('/logout', 'Sair')
  ])
}

const loggedOutNav = () => {
  const links = [
    ['/sensors', 'Ver Registro de Sensores'],
    ['/users', 'Ver Usuários']
  ]
  return m(navigation.Navbar, {}, [
    navigation.links(links),
    navigation.button('/login', 'Log in/Criar conta')
  ])
}

/**
 * Returns a route resolver which handles authorization related business.
 */
const resolve = (view, restricted = false) => {
  const resolver = {}

  if (restricted) {
    resolver.onmatch = () => {
      if (api.getAuth()) return view
      m.route.set('/login')
    }
  }

  resolver.render = vnode => {
    if (api.getAuth()) {
      return m(Layout, { navbar: loggedInNav() }, m(view, vnode.attrs))
    }
    return m(Layout, { navbar: loggedOutNav() }, m(view, vnode.attrs))
  }

  return resolver
}

/**
 * Clears user info from memory/storage and redirects.
 */
const logout = () => {
  api.clearAuth()
  m.route.set('/')
}

/**
 * Redirects to user's personal account page if logged in.
 */
const profile = () => {
  const publicKey = api.getPublicKey()
  if (publicKey) m.route.set(`/users/${publicKey}`)
  else m.route.set('/')
}

/**
 * Build and mount app/router
 */
document.addEventListener('DOMContentLoaded', () => {
  m.route(document.querySelector('#app'), '/', {
    '/': resolve(Dashboard),
    '/users': resolve(UserList),
    '/users/:publicKey': resolve(UserDetailPage),
    '/register': resolve(RegisterSensorForm, true),
    '/login': resolve(LoginForm),
    '/logout': { onmatch: logout },
    '/profile': { onmatch: profile},
    '/sensors': resolve(SensorList),
    '/sensors/:sensorId': resolve(SensorDetailPage),
    '/signup': resolve(SignupForm)
  })
})
