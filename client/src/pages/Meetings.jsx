import { useState, useEffect } from 'react'
import { meetingsApi, institutionsApi, authApi } from '../services'
import { useToast } from '../context/ToastContext'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Badge from '../components/Badge'
import { MEETING_MODES, statusColor, formatDate } from '../utils/constants'

const emptyForm = {
  institution_id: '', contact_person: '', meeting_date: '', meeting_time: '',
  mode: 'Online', location_or_link: '', agenda: '', assigned_to_id: '',
}

export default function Meetings() {
  const [meetings, setMeetings] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [showComplete, setShowComplete] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [completeForm, setCompleteForm] = useState({
    meeting_notes: '', requirements: '', budget_discussion: '',
    expected_dates: '', next_step: '',
  })
  const [editId, setEditId] = useState(null)
  const [cancelId, setCancelId] = useState(null)
  const [statusPrompt, setStatusPrompt] = useState(null)
  const { showToast } = useToast()

  const fetchMeetings = async () => {
    try {
      const params = { search, status: statusFilter }
      const res = await meetingsApi.list(params)
      setMeetings(res.data.meetings)
    } catch {
      showToast('Failed to load meetings', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchMeetings()
    institutionsApi.list().then((res) => setInstitutions(res.data.institutions)).catch(() => {})
    authApi.users().then((res) => setUsers(res.data.users)).catch(() => {})
  }, [search, statusFilter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editId) {
        await meetingsApi.update(editId, form)
        showToast('Meeting updated')
        setShowModal(false)
        setEditId(null)
        setForm(emptyForm)
      } else {
        const res = await meetingsApi.create({ ...form, update_lead_status: false })
        showToast('Meeting scheduled')
        setShowModal(false)
        setForm(emptyForm)
        if (res.data.ask_status_update) {
          setStatusPrompt(res.data.meeting)
        }
      }
      fetchMeetings()
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed', 'error')
    }
  }

  const handleStatusUpdate = async (update) => {
    if (update && statusPrompt) {
      try {
        await institutionsApi.updateStatus(statusPrompt.institution_id, 'Meeting Scheduled')
        showToast('Lead status updated to Meeting Scheduled')
      } catch {
        showToast('Failed to update lead status', 'error')
      }
    }
    setStatusPrompt(null)
  }

  const handleComplete = async (e) => {
    e.preventDefault()
    try {
      await meetingsApi.complete(showComplete, completeForm)
      showToast('Meeting completed')
      setShowComplete(null)
      setCompleteForm({ meeting_notes: '', requirements: '', budget_discussion: '', expected_dates: '', next_step: '' })
      fetchMeetings()
    } catch {
      showToast('Failed to complete meeting', 'error')
    }
  }

  const handleCancel = async () => {
    try {
      await meetingsApi.delete(cancelId)
      showToast('Meeting cancelled')
      setCancelId(null)
      fetchMeetings()
    } catch {
      showToast('Failed to cancel', 'error')
    }
  }

  const openEdit = (m) => {
    setEditId(m.id)
    setForm({
      institution_id: m.institution_id,
      contact_person: m.contact_person,
      meeting_date: m.meeting_date,
      meeting_time: m.meeting_time,
      mode: m.mode,
      location_or_link: m.location_or_link || '',
      agenda: m.agenda || '',
      assigned_to_id: m.assigned_to_id || '',
    })
    setShowModal(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Meetings</h1>
        <button onClick={() => { setEditId(null); setForm(emptyForm); setShowModal(true) }}
          className="px-4 py-2 bg-sidebar text-white rounded-lg hover:bg-sidebarHover">
          + Schedule Meeting
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4 space-y-3">
        <input type="text" placeholder="Search meetings..."
          value={search} onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sidebar outline-none" />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-1.5 border rounded-lg text-sm">
          <option value="">All Statuses</option>
          <option value="Scheduled">Scheduled</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium text-gray-600">Institution</th>
                  <th className="text-left p-3 font-medium text-gray-600">Contact</th>
                  <th className="text-left p-3 font-medium text-gray-600">Date & Time</th>
                  <th className="text-left p-3 font-medium text-gray-600">Mode</th>
                  <th className="text-left p-3 font-medium text-gray-600">Status</th>
                  <th className="text-left p-3 font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {meetings.length === 0 ? (
                  <tr><td colSpan={6} className="p-8 text-center text-gray-500">No meetings found</td></tr>
                ) : meetings.map((m) => (
                  <tr key={m.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">{m.institution_name}</td>
                    <td className="p-3">{m.contact_person}</td>
                    <td className="p-3">{formatDate(m.meeting_date)} {m.meeting_time}</td>
                    <td className="p-3">{m.mode}</td>
                    <td className="p-3"><Badge className={statusColor(m.status)}>{m.status}</Badge></td>
                    <td className="p-3">
                      <div className="flex gap-2">
                        {m.status === 'Scheduled' && (
                          <>
                            <button onClick={() => setShowComplete(m.id)} className="text-green-600 hover:underline text-xs">Complete</button>
                            <button onClick={() => setCancelId(m.id)} className="text-red-500 hover:underline text-xs">Cancel</button>
                          </>
                        )}
                        <button onClick={() => openEdit(m)} className="text-sidebar hover:underline text-xs">Edit</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <Modal isOpen={showModal} onClose={() => { setShowModal(false); setEditId(null) }}
        title={editId ? 'Edit Meeting' : 'Schedule Meeting'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Institution *</label>
            <select value={form.institution_id} onChange={(e) => {
              const inst = institutions.find((i) => i.id === parseInt(e.target.value))
              setForm({ ...form, institution_id: e.target.value, contact_person: inst?.contact_person || '' })
            }} required className="w-full px-3 py-2 border rounded-lg" disabled={editId}>
              <option value="">Select institution</option>
              {institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Contact Person *</label>
            <input value={form.contact_person} onChange={(e) => setForm({ ...form, contact_person: e.target.value })}
              required className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Date *</label>
              <input type="date" value={form.meeting_date} onChange={(e) => setForm({ ...form, meeting_date: e.target.value })}
                required className="w-full px-3 py-2 border rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Time *</label>
              <input value={form.meeting_time} onChange={(e) => setForm({ ...form, meeting_time: e.target.value })}
                placeholder="10:00 AM" required className="w-full px-3 py-2 border rounded-lg" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Mode *</label>
              <select value={form.mode} onChange={(e) => setForm({ ...form, mode: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg">
                {MEETING_MODES.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Assigned To</label>
              <select value={form.assigned_to_id} onChange={(e) => setForm({ ...form, assigned_to_id: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg">
                <option value="">Auto-assign</option>
                {users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">{form.mode === 'Online' ? 'Meeting Link' : 'Location'}</label>
            <input value={form.location_or_link} onChange={(e) => setForm({ ...form, location_or_link: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Agenda</label>
            <textarea value={form.agenda} onChange={(e) => setForm({ ...form, agenda: e.target.value })}
              rows={3} className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-lg">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-sidebar text-white rounded-lg">
              {editId ? 'Update' : 'Schedule'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal isOpen={showComplete !== null} onClose={() => setShowComplete(null)} title="Complete Meeting" size="lg">
        <form onSubmit={handleComplete} className="space-y-4">
          {['meeting_notes', 'requirements', 'budget_discussion', 'expected_dates', 'next_step'].map((field) => (
            <div key={field}>
              <label className="block text-sm font-medium mb-1">{field.replace(/_/g, ' ')}</label>
              <textarea value={completeForm[field]} onChange={(e) => setCompleteForm({ ...completeForm, [field]: e.target.value })}
                rows={2} className="w-full px-3 py-2 border rounded-lg" />
            </div>
          ))}
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowComplete(null)} className="px-4 py-2 border rounded-lg">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-sidebar text-white rounded-lg">Complete Meeting</button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog isOpen={cancelId !== null} onClose={() => setCancelId(null)}
        onConfirm={handleCancel} title="Cancel Meeting"
        message="Are you sure you want to cancel this meeting?" confirmText="Cancel Meeting" />

      <ConfirmDialog isOpen={statusPrompt !== null} onClose={() => handleStatusUpdate(false)}
        onConfirm={() => handleStatusUpdate(true)} title="Update Lead Status"
        message="Would you like to change the lead status to 'Meeting Scheduled'?"
        confirmText="Yes, Update Status" />
    </div>
  )
}
