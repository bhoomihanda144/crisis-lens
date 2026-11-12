import { api } from './api'
import { isDemo } from './mode'
import * as mock from './mockApi'

// params: { status, severity, type }
export const listIncidents = (params) => (isDemo() ? mock.listIncidents(params) : api.get('/incidents', { params }))
export const getIncident = (id) => (isDemo() ? mock.getIncident(id) : api.get(`/incidents/${encodeURIComponent(id)}`))