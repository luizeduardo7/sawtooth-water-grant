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
  oninit(vnode) {
    vnode.state.sensors = [];
    if (api.getIsAdmin()) {
      api.get('sensors').then((sensors) => {
        vnode.state.sensors = sortBy(sensors, 'sensor_id');
      });
    } else {
      const user_public_key = api.getPublicKey();
      api.get(`/sensors/owner/${user_public_key}`).then((sensors) => {
        vnode.state.sensors = sortBy(sensors, 'sensor_id');
      });
    }
  },

  view(vnode) {
    const isAdmin = api.getIsAdmin();

    return [
      m('.sensor-list',
        m('input[type=text]', {
          placeholder: isAdmin ? 'Procurar por ID ou Chave' : 'Procurar por ID',
          oninput: (e) => {
            const searchQuery = e.target.value.toLowerCase();
            api.get('sensors').then((sensors) => {
              vnode.state.sensors = sortBy(
                sensors.filter(sensor => {
                  if (isAdmin) {
                    const owners = sensor.owners || [];
                    const sensorIdMatch = sensor.sensor_id.toLowerCase().includes(searchQuery);
                    const ownerPublicKeyMatch = owners.length > 0 && 
                                                owners[0].user_public_key.toLowerCase().includes(searchQuery);
                    return sensorIdMatch || ownerPublicKeyMatch;
                  } else {
                    return sensor.sensor_id.toLowerCase().includes(searchQuery);
                  }
                }),
                'sensor_id'
              );
            });
          }
        }),
        m(Table, {
          headers: isAdmin ? ['ID', 'Proprietário (Chave Pública)'] : ['ID'],
          rows: vnode.state.sensors.map(sensor => {
            if (isAdmin) {
              const owners = sensor.owners || [];
              const ownerPublicKey = owners.length > 0 ? owners[0].user_public_key : 'N/A';
              return [
                m(`a[href=/sensors/${sensor.sensor_id}]`, { oncreate: m.route.link }, sensor.sensor_id),
                ownerPublicKey
              ];
            } else {
              return [
                m(`a[href=/sensors/${sensor.sensor_id}]`, { oncreate: m.route.link }, sensor.sensor_id)
              ];
            }
          }),
          noRowsText: 'Sem sensores encontrados'
        })
      )
    ];
  }
};

module.exports = SensorList;