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

const Dashboard = {
  view(vnode) {
    return [
      m('.header.text-center.mb-4',
        m('h4', 'Seja bem vindo ao'),
        m('h1.mb-3', 'Outorga ANA'),
        m('h5',
          m('em',
            'Oferecido por ',
            m('strong', 'Zetta/UFLA')))),
      m('.blurb',
        m('p',
          m('em', 'Outorga ANA'),
          ' é uma aplicação que permite o controle e auditória das captações de água',
          ' concedidas pela ANA.  Com base na plataforma blockchain Hyperledger Sawtooth,',
          ' a aplicação faz uso de uma blockchain não comissionada, que registra',
          ' o consumo de água lido por sensores, e esses são atrelados ao consumidores.'),
        m('p',
          'Para usar o ',
          m('em', 'Outorga ANA'),
          ', crie um novo usuário usando Log in/Criar conta na barra de navegação',
          ' acima.'))
    ]
  }
}

module.exports = Dashboard
