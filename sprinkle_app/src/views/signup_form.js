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

const m = require('mithril')
const _ = require('lodash')

const forms = require('../components/forms')
const api = require('../services/api')

const userSubmitter = state => e => {
  e.preventDefault()

  const userKeys = ['username', 'name', 'password', 'created_by_admin_public_key']
  const user = _.pick(state, userKeys)

  // Inclue created_by_admin_public_key no objeto do usuário
  user.created_by_admin_public_key = api.getPublicKey()

  api.post('users', user)
    .then(res => api.setAuth(res.authorization))
    .then(() => m.route.set('/'))
    .catch(api.alertError)
}

const SignupForm = {
  view (vnode) {
    const setter = forms.stateSetter(vnode.state)

    return m('.signup-form', [
      m('form', { onsubmit: userSubmitter(vnode.state) },
      m('legend', 'Criar Usuário'),
      forms.textInput(setter('username'), 'Username'),
      forms.textInput(setter('name'), 'Nome'),
      forms.passwordInput(setter('password'), 'Senha'),
      m('.form-group',
        m('.row.justify-content-end.align-items-end',
          m('col-2',
            m('button.btn.btn-primary',
              'Criar Usuário')))))
    ])
  }}

module.exports = SignupForm
