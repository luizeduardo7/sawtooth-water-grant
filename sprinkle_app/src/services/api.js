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

const API_PATH = 'api/'
const STORAGE_KEY = 'sprinkle.authorization'
const ADMIN_FLAG = 'sprinkle.adminflag'
let authToken = null
let isAdminFlag = null

/**
 * Getters and setters to handle the auth token both in memory and storage
 */
const getAuth = () => {
  if (!authToken) {
    authToken = window.localStorage.getItem(STORAGE_KEY)
  }
  return authToken
}

const setAuth = token => {
  window.localStorage.setItem(STORAGE_KEY, token)
  authToken = token
  return authToken
}

const getIsAdmin = () => {
  if (!isAdminFlag) {
    isAdminFlag = window.localStorage.getItem(ADMIN_FLAG)
  }
  if(isAdminFlag == "true"){
    return true
  }
  return false
}

const setIsAdmin = adminFlag => {
  window.localStorage.setItem(ADMIN_FLAG, adminFlag)
  isAdminFlag = adminFlag
  return isAdminFlag
}

const clearAuth = () => {
  const token = getAuth()
  window.localStorage.clear(STORAGE_KEY)
  window.localStorage.clear(ADMIN_FLAG)
  authToken = null

  return token
}

/**
 * Parses the authToken to return the logged in user's public key
 */
const getPublicKey = () => {
  const token = getAuth()
  if (!token) return null

  const content = window.atob(token.split('.')[1])
  return JSON.parse(content).public_key
}

// Adds Authorization header and prepends API path to url
const baseRequest = opts => {
  const Authorization = getAuth()
  const authHeader = Authorization ? { Authorization } : {}
  opts.headers = _.assign(opts.headers, authHeader)
  opts.url = API_PATH + opts.url
  return m.request(opts)
}

/**
 * Submits a request to an api endpoint with an auth header if present
 */
const request = (method, endpoint, data) => {
  return baseRequest({
    method,
    url: endpoint,
    data
  })
}

/**
 * Method specific versions of request
 */
const get = _.partial(request, 'GET')
const post = _.partial(request, 'POST')

/**
 * Sends the user an alert with the error message and reloads the page.
 * Appropriate for requests triggered by user action.
 */
const alertError = err => {
  console.error(err)
  window.alert(err.error || err.message || err)
  window.location.reload()
}

module.exports = {
  getAuth,
  setAuth,
  getIsAdmin,
  setIsAdmin,
  clearAuth,
  getPublicKey,
  post,
  get,
  alertError
}
