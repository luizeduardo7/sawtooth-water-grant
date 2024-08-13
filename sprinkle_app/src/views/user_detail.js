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
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express ou implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------------
 */

'use strict'

const m = require('mithril');
const _ = require('lodash');

const api = require('../services/api');
const parsing = require('../services/parsing');
const layout = require('../components/layout');
const forms = require('../components/forms');

const WaterTank = {
  view: (vnode) => {
    let percentageUsed = vnode.attrs.percentage;
    if (percentageUsed > 100) percentageUsed = 100; // Limita o percentual a 100%
    let waterHeight = 100 - percentageUsed; // Ajuste da altura da água
    return m("div", { class: "water-tank" },
      m("div", { class: "water-level", style: { height: `${waterHeight}%` }})
    );
  }
};  

const updateSubmitter = state => e => {
  e.preventDefault();

  const publicKey = _.get(state, 'user.public_key', '');
  const updateKeys = ['user_public_key', 'quota', 'updated_by_admin_public_key'];
  const update = _.pick(state, updateKeys);
  update.user_public_key = publicKey;
  update.quota = parsing.toFloat(update.quota);
  update.updated_by_admin_public_key = api.getPublicKey();

  api.post(`users/${publicKey}/update`, update)
    .then(() => {
      window.location.reload();
    })
    .catch(api.alertError)
}

const UserDetailPage = {
  async oninit(vnode) {
    try {
      await api.get(`users/${vnode.attrs.publicKey}`)
      .then(user => {vnode.state.user = user})
      .catch(api.alertError);

      await api.get(`users/usage/${vnode.attrs.publicKey}`)
      .then(quota_usage => {vnode.state.quota_usage = quota_usage})
      .catch(api.alertError);
    } catch (error) {
      api.alertError(error);
    }
  },

  view(vnode) {
    const setter = forms.stateSetter(vnode.state);
    const publicKey = _.get(vnode.state, 'user.public_key', '');
    const timestamp = new Date(_.get(vnode.state, 'user.created_at', '') * 1000).toString();
    const quota = _.get(vnode.state, 'user.quota', '');
    const quota_usage = _.get(vnode.state, 'quota_usage.sum', 0);
    let percentageUsed = (quota_usage / quota * 100).toFixed(2);

    return m("div", { class: "user-detail-container" },
      m("div", { class: "user-info" },
        layout.title(_.get(vnode.state, 'user.name', '')),
        m('.container',
          layout.row(layout.staticField('Chave Pública', publicKey)),
          layout.row(layout.staticField('Registrado', timestamp)),
          layout.row(layout.staticField('Cota concedida (m³)', quota)),
          layout.row(layout.staticField('Consumo atual (m³)', quota_usage)),
          layout.row(layout.staticField('Percentual usado', percentageUsed + '%')),
          layout.row(
            (api.getIsAdmin())
            ? m('.update-form', [
                m('form', { onsubmit: updateSubmitter(vnode.state) },
                m('legend', 'Atualizar Cota Mensal'),
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
                      m('button.btn.btn-primary', 'Atualizar cota')))
                ))
              ])
            : '')
        )
      ),
      m("div", { class: "water-tank-container" },
        m(WaterTank, { percentage: percentageUsed })
      )
    );
  }
}

module.exports = UserDetailPage;
