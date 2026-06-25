import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { institutionsApi, authApi, communicationsApi } from '../services'
import { useToast } from '../context/ToastContext'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Badge from '../components/Badge'
import {
  INSTITUTION_TYPES, PROGRAM_INTERESTS, LEAD_SOURCES, LEAD_STATUSES,
  priorityColor, statusColor, formatDate,
} from '../utils/constants'

export default function LeadDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { showToast } = useToast()
  const [lead, setLead] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [form, setForm] = useState(null)
  const [showDelete, setShowDelete] = useState(false)
  const [showMessage, setShowMessage] = useState(false)
  const [messageBody, setMessageBody] = useState('')
  const [messageSubject, setMessageSubject] = useState('')
  const [commId, setCommId] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  const fetchLead = async () => {
    try {
      const res = await institutionsApi.get(id)
      setLead(res.data.institution)
      setForm(res.data.institution)
    } catch {
      showToast('Failed to load lead', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLead()
    authApi.users().then((res) => setUsers(res.data.users)).catch(() => {})
  }, [id])

  const handleUpdate = async (e) => {
    e.preventDefault()
    try {
      const res = await institutionsApi.update(id, form)
      setLead(res.data.institution)
      setEditMode(false)
      showToast('Lead updated')
    } catch (err) {
      showToast(err.response?.data?.error || 'Update failed', 'error')
    }
  }

  const handleStatusChange = async (status) => {
    try {
      const res = await institutionsApi.updateStatus(id, status)
      setLead(res.data.institution)
      showToast('Status updated')
    } catch {
      showToast('Failed to update status', 'error')
    }
  }

  const handleAssign = async (userId) => {
    try {
      const res = await institutionsApi.assign(id, parseInt(userId))
      setLead(res.data.institution)
      showToast('Owner assigned')
    } catch {
      showToast('Assignment failed', 'error')
    }
  }

  const handleRetryAI = async () => {
    setAnalyzing(true)
    try {
      const res = await institutionsApi.analyze(id)
      setLead(res.data.institution)
      showToast(res.data.message || 'Analysis completed')
    } catch (err) {
      showToast(err.response?.data?.error || 'AI analysis failed', 'error')
      fetchLead()
    } finally {
      setAnalyzing(false)
    }
  }

  const handleGenerateMessage = async () => {
    try {
      const res = await communicationsApi.generate({ institution_id: parseInt(id), message_type: 'outreach' })
      setMessageBody(res.data.communication.body)
      setMessageSubject(res.data.communication.subject || '')
      setCommId(res.data.communication.id)
      setShowMessage(true)
    } catch {
      showToast('Failed to generate message', 'error')
    }
  }

  const handleRegenerateMessage = async () => {
    try {
      const res = await institutionsApi.regenerateOutreach(id)
      setMessageBody(res.data.outreach_message)
      showToast('Message regenerated')
    } catch {
      showToast('Regeneration failed', 'error')
    }
  }

  const handleMarkSent = async () => {
    try {
      if (commId) {
        await communicationsApi.markSent(commId, { body: messageBody, subject: messageSubject })
      } else {
        await communicationsApi.send({
          institution_id: parseInt(id),
          body: messageBody,
          subject: messageSubject,
          message_type: 'outreach',
        })
      }
      showToast('Message marked as sent')
      setShowMessage(false)
      fetchLead()
    } catch {
      showToast('Failed to send message', 'error')
    }
  }

  const handleDelete = async () => {
    try {
      await institutionsApi.delete(id)
      showToast('Lead deleted')
      navigate('/leads')
    } catch {
      showToast('Delete failed', 'error')
    }
  }

  if (loading) return <div className="text-center py-12 text-gray-500">Loading...</div>
  if (!lead) return <div className="text-center py-12 text-red-500">Lead not found</div>

  const ai = lead.ai_analysis

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <Link to="/leads" className="text-sm text-sidebar hover:underline">← Back to Leads</Link>
          <h1 className="text-2xl font-bold text-gray-800 mt-2">{lead.name}</h1>
          <p className="text-gray-500">{lead.location}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => setEditMode(true)} className="px-3 py-1.5 border rounded-lg text-sm hover:bg-gray-50">Edit</button>
          <button onClick={handleGenerateMessage} className="px-3 py-1.5 bg-accent text-white rounded-lg text-sm hover:bg-accentDark">Generate Message</button>
          <button onClick={() => setShowDelete(true)} className="px-3 py-1.5 border border-red-300 text-red-600 rounded-lg text-sm hover:bg-red-50">Delete</button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-5">
            <h2 className="text-lg font-semibold mb-4">Institution Details</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              {[
                ['Contact Person', lead.contact_person],
                ['Email', lead.email],
                ['Phone', lead.phone],
                ['Type', lead.institution_type],
                ['Students', lead.student_strength],
                ['Program', lead.program_interest],
                ['Source', lead.lead_source],
                ['Partnership', lead.previous_partnership ? 'Yes' : 'No'],
                ['Added', formatDate(lead.created_at)],
                ['Updated', formatDate(lead.updated_at)],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-gray-500">{label}</p>
                  <p className="font-medium">{value}</p>
                </div>
              ))}
            </div>
            {lead.notes && (
              <div className="mt-4">
                <p className="text-gray-500 text-sm">Notes</p>
                <p className="text-sm mt-1">{lead.notes}</p>
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-5">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">AI Analysis</h2>
              {ai?.status === 'Failed' && (
                <button onClick={handleRetryAI} disabled={analyzing}
                  className="px-3 py-1.5 bg-orange-500 text-white rounded-lg text-sm disabled:opacity-50">
                  {analyzing ? 'Analyzing...' : 'Retry AI Analysis'}
                </button>
              )}
            </div>
            {ai ? (
              <div className="space-y-3">
                {ai.status === 'Failed' ? (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    AI analysis failed. Click "Retry AI Analysis" to try again.
                  </div>
                ) : (
                  <>
                    <div className="flex gap-3 items-center">
                      <Badge className={priorityColor(ai.priority)}>{ai.priority}</Badge>
                      <span className="text-lg font-bold">Score: {ai.score}</span>
                      <Badge className={statusColor(ai.status)}>{ai.status}</Badge>
                    </div>
                    <p className="text-sm text-gray-600"><strong>Reason:</strong> {ai.reason}</p>
                    <p className="text-sm text-accentDark font-medium">{ai.next_best_action}</p>
                    {ai.outreach_message && (
                      <div className="p-3 bg-gray-50 rounded-lg text-sm">
                        <p className="font-medium mb-1">Outreach Message:</p>
                        <p className="whitespace-pre-wrap">{ai.outreach_message}</p>
                      </div>
                    )}
                    {ai.follow_up_suggestions?.length > 0 && (
                      <div>
                        <p className="font-medium text-sm mb-2">Follow-up Suggestions:</p>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {ai.follow_up_suggestions.map((s, i) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No AI analysis available</p>
            )}
          </div>

          {lead.activities?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-5">
              <h2 className="text-lg font-semibold mb-4">Activity History</h2>
              <div className="space-y-2">
                {lead.activities.map((a) => (
                  <div key={a.id} className="flex justify-between p-3 bg-gray-50 rounded-lg text-sm">
                    <div>
                      <span className="font-medium">{a.activity_type}</span> — {a.description}
                    </div>
                    <span className="text-xs text-gray-400">{new Date(a.created_at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-5">
            <h2 className="text-lg font-semibold mb-4">Status & Assignment</h2>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-500">Lead Status</label>
                <select value={lead.lead_status} onChange={(e) => handleStatusChange(e.target.value)}
                  className="w-full mt-1 px-3 py-2 border rounded-lg">
                  {LEAD_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-500">Assigned To</label>
                <select value={lead.assigned_to_id || ''} onChange={(e) => handleAssign(e.target.value)}
                  className="w-full mt-1 px-3 py-2 border rounded-lg">
                  <option value="">Unassigned</option>
                  {users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
                </select>
              </div>
              <div className="flex gap-2">
                <Badge className={statusColor(lead.lead_status)}>{lead.lead_status}</Badge>
                {ai && <Badge className={priorityColor(ai.priority)}>{ai.priority}</Badge>}
              </div>
            </div>
          </div>

          {lead.communications?.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-5">
              <h2 className="text-lg font-semibold mb-4">Communications</h2>
              <div className="space-y-2">
                {lead.communications.map((c) => (
                  <div key={c.id} className="p-3 bg-gray-50 rounded-lg text-sm">
                    <div className="flex justify-between">
                      <span className="font-medium">{c.message_type}</span>
                      <Badge className={statusColor(c.status)}>{c.status}</Badge>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{formatDate(c.sent_at || c.created_at)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <Modal isOpen={editMode} onClose={() => setEditMode(false)} title="Edit Lead" size="lg">
        {form && (
          <form onSubmit={handleUpdate} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {['name', 'location', 'contact_person', 'email', 'phone'].map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium mb-1">{field.replace('_', ' ')}</label>
                  <input value={form[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg" />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium mb-1">Student Strength</label>
                <input type="number" value={form.student_strength}
                  onChange={(e) => setForm({ ...form, student_strength: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Institution Type</label>
                <select value={form.institution_type} onChange={(e) => setForm({ ...form, institution_type: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg">
                  {INSTITUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Program Interest</label>
                <select value={form.program_interest} onChange={(e) => setForm({ ...form, program_interest: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg">
                  {PROGRAM_INTERESTS.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Lead Source</label>
                <select value={form.lead_source} onChange={(e) => setForm({ ...form, lead_source: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg">
                  {LEAD_SOURCES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Lead Status</label>
                <select value={form.lead_status} onChange={(e) => setForm({ ...form, lead_status: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg">
                  {LEAD_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Notes</label>
              <textarea value={form.notes || ''} onChange={(e) => setForm({ ...form, notes: e.target.value })}
                rows={3} className="w-full px-3 py-2 border rounded-lg" />
            </div>
            <div className="flex justify-end gap-3">
              <button type="button" onClick={() => setEditMode(false)} className="px-4 py-2 border rounded-lg">Cancel</button>
              <button type="submit" className="px-4 py-2 bg-sidebar text-white rounded-lg">Save Changes</button>
            </div>
          </form>
        )}
      </Modal>

      <Modal isOpen={showMessage} onClose={() => setShowMessage(false)} title="Review Outreach Message" size="lg">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <input value={messageSubject} onChange={(e) => setMessageSubject(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Message</label>
            <textarea value={messageBody} onChange={(e) => setMessageBody(e.target.value)} rows={10}
              className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="flex justify-between">
            <button onClick={handleRegenerateMessage} className="px-4 py-2 border rounded-lg text-sm">Regenerate</button>
            <div className="flex gap-3">
              <button onClick={() => setShowMessage(false)} className="px-4 py-2 border rounded-lg">Cancel</button>
              <button onClick={handleMarkSent} className="px-4 py-2 bg-sidebar text-white rounded-lg">Mark as Sent</button>
            </div>
          </div>
        </div>
      </Modal>

      <ConfirmDialog isOpen={showDelete} onClose={() => setShowDelete(false)}
        onConfirm={handleDelete} title="Delete Lead"
        message="This will permanently delete this lead and all related records."
        confirmText="Delete" />
    </div>
  )
}
