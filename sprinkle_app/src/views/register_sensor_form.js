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
const L = require('leaflet')

const api = require('../services/api')
const parsing = require('../services/parsing')
const forms = require('../components/forms')
const layout = require('../components/layout')

const sensorSubmitter = state => e => {
  e.preventDefault()

  const sensorKeys = ['latitude', 'longitude', 'sensor_id']
  const sensor = _.pick(state, sensorKeys)
  sensor.latitude = parsing.toInt(sensor.latitude)
  sensor.longitude = parsing.toInt(sensor.longitude)

  api.post('sensors', sensor)
    .then(() => m.route.set('/sensors'))
    .catch(api.alertError)
}

const RegisterSensorForm = {
  view (vnode) {
    const setter = forms.stateSetter(vnode.state)
    return [
    (api.getIsAdmin() === false) // Admin não pode registrar sensores
    ? m('.register-form', [
        m('form', { onsubmit: sensorSubmitter(vnode.state) },
        m('legend', 'Registrar Sensor'),
        forms.textInput(setter('sensor_id'), 'ID do Sensor'),
        layout.row([
          forms.group('Latitude', forms.field(setter('latitude'), {
            type: 'number',
            step: 'any',
            min: -90,
            max: 90,
          })),
          forms.group('Longitude', forms.field(setter('longitude'), {
            type: 'number',
            step: 'any',
            min: -180,
            max: 180,
          }))
        ]),
        m('.form-group',
          m('.row.justify-content-end.align-items-end',
            m('col-2',
              m('button.btn.btn-primary',
                'Registrar Sensor')))))
      ])
    : 'Você não tem permissão para acessar esta página.']
  }
}

module.exports = RegisterSensorForm
