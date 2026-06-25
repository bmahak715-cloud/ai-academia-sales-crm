import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { institutionsApi, authApi } from '../services'
import { useToast } from '../context/ToastContext'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Badge from '../components/Badge'
import {
  INSTITUTION_TYPES, PROGRAM_INTERESTS, LEAD_SOURCES, LEAD_STATUSES,
  PRIORITIES, priorityColor, statusColor,
} from '../utils/constants'

const emptyForm = {
  name: '', location: '', contact_person: '', email: '', phone: '',
  institution_type: 'Engineering College', student_strength: '',
  program_interest: 'Artificial Intelligence', lead_source: 'Website',
  lead_status: 'New Lead', previous_partnership: false, notes: '', assigned_to_id: '',
}

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({ status: '', ai_priority: '', institution_type: '', lead_source: '', program_interest: '', assigned_to_id: '' })
  const [sort, setSort] = useState('newest')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [formErrors, setFormErrors] = useState({})
  const [deleteId, setDeleteId] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useToast()

  const fetchLeads = async () => {
    try {
      const params = { search, sort, ...filters }
      const res = await institutionsApi.list(params)
      setLeads(res.data.institutions)
    } catch {
      showToast('Failed to load leads', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLeads()
    authApi.users().then((res) => setUsers(res.data.users)).catch(() => {})
  }, [search, filters, sort])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setFormErrors({})
    try {
      const res = await institutionsApi.create(form)
      showToast('Lead created successfully!')
      if (res.data.warnings?.name) showToast(res.data.warnings.name, 'warning')
      if (res.data.ai_error) showToast(res.data.ai_error, 'warning')
      setShowModal(false)
      setForm(emptyForm)
      fetchLeads()
    } catch (err) {
      const errors = err.response?.data?.errors
      if (errors) setFormErrors(errors)
      showToast(err.response?.data?.error || 'Failed to create lead', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async () => {
    try {
      await institutionsApi.delete(deleteId)
      showToast('Lead deleted')
      setDeleteId(null)
      fetchLeads()
    } catch {
      showToast('Failed to delete', 'error')
    }
  }

  const updateField = (field, value) => setForm((f) => ({ ...f, [field]: value }))

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Institution Leads</h1>
        <button onClick={() => { setForm(emptyForm); setShowModal(true) }}
          className="px-4 py-2 bg-sidebar text-white rounded-lg hover:bg-sidebarHover transition-colors">
          + Add Lead
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4 space-y-3">
        <input type="text" placeholder="Search institution, contact, or email..."
          value={search} onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sidebar outline-none" />
        <div className="flex flex-wrap gap-2">
          <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-3 py-1.5 border rounded-lg text-sm">
            <option value="">All Statuses</option>
            {LEAD_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={filters.ai_priority} onChange={(e) => setFilters({ ...filters, ai_priority: e.target.value })}
            className="px-3 py-1.5 border rounded-lg text-sm">
            <option value="">All Priorities</option>
            {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={filters.institution_type} onChange={(e) => setFilters({ ...filters, institution_type: e.target.value })}
            className="px-3 py-1.5 border rounded-lg text-sm">
            <option value="">All Types</option>
            {INSTITUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={filters.lead_source} onChange={(e) => setFilters({ ...filters, lead_source: e.target.value })}
            className="px-3 py-1.5 border rounded-lg text-sm">
            <option value="">All Sources</option>
            {LEAD_SOURCES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={sort} onChange={(e) => setSort(e.target.value)}
            className="px-3 py-1.5 border rounded-lg text-sm">
            <option value="newest">Newest</option>
            <option value="name">Institution Name</option>
            <option value="ai_score">AI Score</option>
            <option value="follow_up_date">Last Updated</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading leads...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium text-gray-600">Institution</th>
                  <th className="text-left p-3 font-medium text-gray-600">Contact</th>
                  <th className="text-left p-3 font-medium text-gray-600">Status</th>
                  <th className="text-left p-3 font-medium text-gray-600">AI Priority</th>
                  <th className="text-left p-3 font-medium text-gray-600">Owner</th>
                  <th className="text-left p-3 font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.length === 0 ? (
                  <tr><td colSpan={6} className="p-8 text-center text-gray-500">No leads found</td></tr>
                ) : leads.map((lead) => (
                  <tr key={lead.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <Link to={`/leads/${lead.id}`} className="font-medium text-sidebar hover:underline">{lead.name}</Link>
                      <p className="text-xs text-gray-500">{lead.location}</p>
                    </td>
                    <td className="p-3">
                      <p>{lead.contact_person}</p>
                      <p className="text-xs text-gray-500">{lead.email}</p>
                    </td>
                    <td className="p-3"><Badge className={statusColor(lead.lead_status)}>{lead.lead_status}</Badge></td>
                    <td className="p-3">
                      {lead.ai_analysis ? (
                        <Badge className={priorityColor(lead.ai_analysis.priority)}>
                          {lead.ai_analysis.priority} ({lead.ai_analysis.score})
                        </Badge>
                      ) : <span className="text-gray-400">—</span>}
                    </td>
                    <td className="p-3 text-sm">{lead.assigned_to?.name || '—'}</td>
                    <td className="p-3">
                      <div className="flex gap-2">
                        <Link to={`/leads/${lead.id}`} className="text-sidebar hover:underline text-xs">View</Link>
                        <button onClick={() => setDeleteId(lead.id)} className="text-red-500 hover:underline text-xs">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add New Lead" size="lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { field: 'name', label: 'Institution Name', required: true },
              { field: 'location', label: 'Location', required: true },
              { field: 'contact_person', label: 'Contact Person', required: true },
              { field: 'email', label: 'Email', required: true, type: 'email' },
              { field: 'phone', label: 'Phone', required: true },
              { field: 'student_strength', label: 'Student Strength', required: true, type: 'number' },
            ].map(({ field, label, required, type = 'text' }) => (
              <div key={field}>
                <label className="block text-sm font-medium text-gray-700 mb-1">{label}{required && ' *'}</label>
                <input type={type} value={form[field]} onChange={(e) => updateField(field, e.target.value)} required={required}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-sidebar outline-none ${formErrors[field] ? 'border-red-500' : ''}`} />
                {formErrors[field] && <p className="text-xs text-red-500 mt-1">{formErrors[field]}</p>}
              </div>
            ))}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Institution Type *</label>
              <select value={form.institution_type} onChange={(e) => updateField('institution_type', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg">
                {INSTITUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Program Interest *</label>
              <select value={form.program_interest} onChange={(e) => updateField('program_interest', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg">
                {PROGRAM_INTERESTS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Lead Source *</label>
              <select value={form.lead_source} onChange={(e) => updateField('lead_source', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg">
                {LEAD_SOURCES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Assign To</label>
              <select value={form.assigned_to_id} onChange={(e) => updateField('assigned_to_id', e.target.value)}
                className="w-full px-3 py-2 border rounded-lg">
                <option value="">Auto-assign</option>
                {users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.previous_partnership}
                onChange={(e) => updateField('previous_partnership', e.target.checked)} />
              Previous Partnership Experience
            </label>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea value={form.notes} onChange={(e) => updateField('notes', e.target.value)} rows={3}
              className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-lg">Cancel</button>
            <button type="submit" disabled={submitting}
              className="px-4 py-2 bg-sidebar text-white rounded-lg disabled:opacity-50">
              {submitting ? 'Creating...' : 'Create Lead'}
            </button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog isOpen={deleteId !== null} onClose={() => setDeleteId(null)}
        onConfirm={handleDelete} title="Delete Lead"
        message="This will permanently delete the lead and all related records. Are you sure?"
        confirmText="Delete" />
    </div>
  )
}
