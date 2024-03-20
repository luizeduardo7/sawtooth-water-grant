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
const MapWidget = require('../components/data')
const forms = require('../components/forms')

// Transferência de sensores desativada.
// const transferSubmitter = state => e => {
//   e.preventDefault()

//   const sensorId = _.get(state, 'sensor.sensor_id', '')
//   const transferKeys = ['receiving_agent']
//   const transfer = _.pick(state, transferKeys)

//   api.post(`sensors/${sensorId}/transfer`, transfer)
//     .then(() => m.route.set(`/sensors/${sensorId}`))
//     .catch(api.alertError)
// }

const updateSubmitter = state => e => {
  e.preventDefault()

  const sensorId = _.get(state, 'sensor.sensor_id', '')
  const updateKeys = ['measurement']
  const update = _.pick(state, updateKeys)
  update.measurement = parsing.toFloat(update.measurement)

  api.post(`sensors/${sensorId}/update`, update)
    .then(() => m.route.set(`/sensors/${sensorId}`))
    .catch(api.alertError)
}

const SensorDetailPage = {
  oninit(vnode) {
    api.get(`sensors/${vnode.attrs.sensorId}`)
      .then(sensor => {vnode.state.sensor = sensor})
      .catch(api.alertError)

      // Inicializa o estado da página para 1
      vnode.state.page = 1
  },

  view (vnode) {
    const setter = forms.stateSetter(vnode.state)
    const sensorId = _.get(vnode.state, 'sensor.sensor_id', '')
    const coordinates = _.get(vnode.state, 'sensor.locations', [])
    const created = new Date(
      _.get(_.minBy(coordinates, 'timestamp'), 'timestamp') * 1000).toString()
    const updated = new Date(
      _.get(_.maxBy(coordinates, 'timestamp'), 'timestamp') * 1000).toString()
    const owners = _.get(vnode.state, 'sensor.owners', [])
    const owner = _.get(_.maxBy(owners, 'timestamp'), 'user_id', '')
    const measurements = _.get(vnode.state, 'sensor.measurements', [])
    const measurement = _.get(_.maxBy(measurements, 'timestamp'), 'measurement', '')

    // Função para formatar a data e hora de uma medição
    const formatDateTime = timestamp => {
      const date = new Date(timestamp * 1000)
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`
    }

    // Página atual e número total de páginas
    const currentPage = vnode.state.page
    const totalItems = measurements.length
    const totalPages = Math.ceil(totalItems / 10)

    // Índices dos itens a serem exibidos nesta página
    const startIndex = (currentPage - 1) * 10
    const endIndex = Math.min(startIndex + 10, totalItems)

    // Reverte a ordem das medições para que as últimas leituras sejam exibidas primeiro
    const reversedMeasurements = _.reverse(_.clone(measurements));

    // Renderiza somente os itens da página atual
    const measurementTable = reversedMeasurements.slice(startIndex, endIndex).map(measurement => {
      return m('tr', [
        m('td', measurement.measurement),
        m('td', formatDateTime(measurement.timestamp))
      ])
    })

    // Funções para navegar entre páginas
    const goToPage = page => {
      vnode.state.page = page
    }

    const nextPage = () => {
      if (currentPage < totalPages) {
        vnode.state.page++
      }
    }

    const prevPage = () => {
      if (currentPage > 1) {
        vnode.state.page--
      }
    }

    return [
      layout.title(sensorId),
      m('.container',
        layout.row(layout.staticField('Leitura atual (m³)', measurement)),
        layout.row(layout.staticField('Proprietário', owner)),
        layout.row(layout.staticField('Criado', created)),
        layout.row(layout.staticField('Atualizado', updated))),
      m(MapWidget, {
        coordinates: coordinates
      }),
      layout.row(
          (owner == api.getPublicKey())
          ? m('.update-form', [
            m('form', { onsubmit: updateSubmitter(vnode.state, sensorId) },
            m('legend', 'Atualizar Leitura'),
            layout.row([
              forms.group('Leitura (m³)', forms.field(setter('measurement'), {
                type: 'number',
                step: 'any',
                min: 0
              }))
            ]),
            m('.form-group',
              m('.row.justify-content-end.align-items-end',
                m('col-2',
                  m('button.btn.btn-primary',
                    'Atualizar Leitura')))))
            ])
          : ''),
        (owner == api.getPublicKey())
        ? 
        m('table.table', [
          m('thead',
            m('tr', [
              m('th', 'Leitura (m³)'),
              m('th', 'Data e Hora')
            ])
          ),
          m('tbody', measurementTable)
        ]) : "",
        (owner == api.getPublicKey())
        ? 
        m('.pagination', [
          m('button.btn.btn-primary', { onclick: prevPage, disabled: currentPage === 1 }, 'Página Anterior'),
          m('span', ` Página ${currentPage} de ${totalPages} `),
          m('button.btn.btn-primary', { onclick: nextPage, disabled: currentPage === totalPages }, 'Próxima Página')
        ]) : "",
    // Atualização de localização desativada.
    // layout.row(
    //   (owner == api.getPublicKey())
    //   ? m('.update-form', [
    //     m('form', { onsubmit: updateSubmitter(vnode.state, sensorId) },
    //     m('legend', 'Atualizar Localização'),
    //     layout.row([
    //       forms.group('Latitude', forms.field(setter('latitude'), {
    //         type: 'number',
    //         step: 'any',
    //         min: -90,
    //         max: 90,
    //       })),
    //       forms.group('Longitude', forms.field(setter('longitude'), {
    //         type: 'number',
    //         step: 'any',
    //         min: -180,
    //         max: 180,
    //       }))
    //     ]),
    //     m('.form-group',
    //       m('.row.justify-content-end.align-items-end',
    //         m('col-2',
    //           m('button.btn.btn-primary',
    //             'Atualizar Localização')))))
    //     ])
    //   : '')
    // Transferência de sensores desativada.
    // layout.row(
    //   (owner == api.getPublicKey())
    //   ? m('transfer-form', [
    //     m('form', { onsubmit: transferSubmitter(vnode.state, sensorId) },
    //     m('legend', 'Transferir Propriedade'),
    //     layout.row([
    //       forms.group('Chave Pública', forms.field(setter('receiving_agent'), {
    //         type: 'string'
    //       }))
    //     ]),
    //     m('.form-group',
    //       m('.row.justify-content-end.align-items-end',
    //         m('col-2',
    //           m('button.btn.btn-primary',
    //             'Transferir Propriedade')))))
    //     ])
    //   : '')
    ]
  }
}

module.exports = SensorDetailPage