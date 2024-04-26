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
const sortBy = require('lodash/sortBy')
const Table = require('../components/tables.js')
const api = require('../services/api.js')

const UserList = {
  oninit(vnode) {
    vnode.state.users = []
    if(api.getIsAdmin()) {
      api.get('users').then((users) => {
        vnode.state.users = sortBy(users, 'name')
      })
    }
  },

  view(vnode) {
    return [
      (api.getIsAdmin())
      ? m('.user-list',
          m('input[type=text]', {
            placeholder: 'Procurar por Nome',
            oninput: (e) => {
              const searchName = e.target.value
              api.get('users').then((users) => {
                vnode.state.users = sortBy(users.filter(user => user.name.includes(searchName)), 'name')
              })
            }
          }),
          m(Table, {
            headers: [
              'Nome',
              'Chave'
            ],
            rows: vnode.state.users
              .map((user) => [
                m(`a[href=/users/${user.public_key}]`,
                  { oncreate: m.route.link },
                  user.name),
                user.public_key,
              ]),
            noRowsText: 'Sem usuários encontrados'
          })
        )
    : "Você não tem permissão para acessar esta página"]
  }
}

module.exports = UserList