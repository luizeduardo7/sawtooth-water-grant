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

const api = require('../services/api')
const parsing = require('../services/parsing')
const layout = require('../components/layout')
const forms = require('../components/forms')

const updateSubmitter = state => e => {
  e.preventDefault()

  const publicKey = _.get(state, 'user.public_key', '')
  const updateKeys = ['quota']
  const update = _.pick(state, updateKeys)
  update.quota = parsing.toFloat(update.quota)

  api.post(`users/${publicKey}/update`, update)
    .then(() => m.route.set(`/users/${publicKey}`))
    .catch(api.alertError)
}

/**
 * Displays information for a particular user
 */
const UserDetailPage = {
  oninit(vnode) {
    api.get(`users/${vnode.attrs.publicKey}`)
      .then(user => {vnode.state.user = user})
      .catch(api.alertError)
  },

  view (vnode) {
    const setter = forms.stateSetter(vnode.state)
    const publicKey = _.get(vnode.state, 'user.public_key', '')
    const timestamp = new Date(
      _.get(vnode.state, 'user.timestamp', '') * 1000).toString()
    const quota = _.get(vnode.state, 'user.quota', '')
    return [
      layout.title(_.get(vnode.state, 'user.name', '')),
      m('.container',
        layout.row(layout.staticField('Chave Pública', publicKey)),
        layout.row(layout.staticField('Registrado', timestamp)),
        layout.row(layout.staticField('Cota concedida (m³)', quota)),
        layout.row(
          m('.update-form', [
            m('form', { onsubmit: updateSubmitter(vnode.state, publicKey) },
            m('legend', 'Atualizar Cota'),
            layout.row([
              forms.group('Nova cota (m³)', forms.field(setter('quota'), {
                type: 'number',
                step: 'any',
                min: 0
              }))
            ]),
            m('.form-group',
              m('.row.justify-content-end.align-items-end',
                m('col-2',
                  m('button.btn.btn-primary',
                    'Atualizar cota')))))
            ])
        )
      )
    ]
  }
}

module.exports = UserDetailPage