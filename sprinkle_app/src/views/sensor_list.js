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

const SensorList = {
  oninit (vnode) {
    vnode.state.sensors = []
    api.get('sensors').then((sensors) => {
        vnode.state.sensors = sortBy(sensors, 'sensor_id')
      })
  },

  view (vnode) {
    return [
      m('.sensor-list',
        m(Table, {
          headers: [
            'ID'
          ],
          rows: vnode.state.sensors
            .map((sensor) => [
              m(`a[href=/sensors/${sensor.sensor_id}]`,
                { oncreate: m.route.link },
                sensor.sensor_id)
            ]),
          noRowsText: 'Sem sensores encontrados'
        })
      )
    ]
  }
}

module.exports = SensorList
