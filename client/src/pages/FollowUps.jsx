import { useState, useEffect } from 'react'
import { followUpsApi, institutionsApi, authApi } from '../services'
import { useToast } from '../context/ToastContext'
import Modal from '../components/Modal'
import ConfirmDialog from '../components/ConfirmDialog'
import Badge from '../components/Badge'
import { TASK_TYPES, PRIORITIES, priorityColor, statusColor, formatDate } from '../utils/constants'

const emptyForm = {
  institution_id: '', title: '', task_type: 'Phone Call', description: '',
  due_date: '', priority: 'Medium', assigned_to_id: '',
}

export default function FollowUps() {
  const [tasks, setTasks] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [view, setView] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [editId, setEditId] = useState(null)
  const [deleteId, setDeleteId] = useState(null)
  const { showToast } = useToast()

  const fetchTasks = async () => {
    try {
      const params = { search, view, status: statusFilter }
      const res = await followUpsApi.list(params)
      setTasks(res.data.follow_ups)
    } catch {
      showToast('Failed to load tasks', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
    institutionsApi.list().then((res) => setInstitutions(res.data.institutions)).catch(() => {})
    authApi.users().then((res) => setUsers(res.data.users)).catch(() => {})
  }, [search, view, statusFilter])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editId) {
        await followUpsApi.update(editId, form)
        showToast('Task updated')
      } else {
        await followUpsApi.create(form)
        showToast('Task created')
      }
      setShowModal(false)
      setEditId(null)
      setForm(emptyForm)
      fetchTasks()
    } catch (err) {
      showToast(err.response?.data?.error || 'Failed', 'error')
    }
  }

  const handleComplete = async (id) => {
    try {
      await followUpsApi.complete(id)
      showToast('Task completed')
      fetchTasks()
    } catch {
      showToast('Failed to complete', 'error')
    }
  }

  const handleDelete = async () => {
    try {
      await followUpsApi.delete(deleteId)
      showToast('Task deleted')
      setDeleteId(null)
      fetchTasks()
    } catch {
      showToast('Delete failed', 'error')
    }
  }

  const openEdit = (task) => {
    setEditId(task.id)
    setForm({
      institution_id: task.institution_id,
      title: task.title,
      task_type: task.task_type,
      description: task.description || '',
      due_date: task.due_date,
      priority: task.priority,
      assigned_to_id: task.assigned_to_id || '',
    })
    setShowModal(true)
  }

  const viewButtons = [
    { key: '', label: 'All' },
    { key: 'due_today', label: 'Due Today' },
    { key: 'overdue', label: 'Overdue' },
    { key: 'upcoming', label: 'Upcoming' },
    { key: 'completed', label: 'Completed' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-800">Follow-ups</h1>
        <button onClick={() => { setEditId(null); setForm(emptyForm); setShowModal(true) }}
          className="px-4 py-2 bg-sidebar text-white rounded-lg hover:bg-sidebarHover">
          + Add Task
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-4 space-y-3">
        <input type="text" placeholder="Search tasks..."
          value={search} onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-sidebar outline-none" />
        <div className="flex flex-wrap gap-2">
          {viewButtons.map((v) => (
            <button key={v.key} onClick={() => setView(v.key)}
              className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
                view === v.key ? 'bg-sidebar text-white border-sidebar' : 'hover:bg-gray-50'
              }`}>
              {v.label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Loading...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="text-left p-3 font-medium text-gray-600">Task</th>
                  <th className="text-left p-3 font-medium text-gray-600">Institution</th>
                  <th className="text-left p-3 font-medium text-gray-600">Type</th>
                  <th className="text-left p-3 font-medium text-gray-600">Due Date</th>
                  <th className="text-left p-3 font-medium text-gray-600">Priority</th>
                  <th className="text-left p-3 font-medium text-gray-600">Status</th>
                  <th className="text-left p-3 font-medium text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.length === 0 ? (
                  <tr><td colSpan={7} className="p-8 text-center text-gray-500">No tasks found</td></tr>
                ) : tasks.map((task) => (
                  <tr key={task.id} className="border-b hover:bg-gray-50">
                    <td className="p-3 font-medium">{task.title}</td>
                    <td className="p-3">{task.institution_name}</td>
                    <td className="p-3">{task.task_type}</td>
                    <td className="p-3">{formatDate(task.due_date)}</td>
                    <td className="p-3"><Badge className={priorityColor(task.priority)}>{task.priority}</Badge></td>
                    <td className="p-3"><Badge className={statusColor(task.status)}>{task.status}</Badge></td>
                    <td className="p-3">
                      <div className="flex gap-2">
                        {task.status !== 'Completed' && (
                          <button onClick={() => handleComplete(task.id)} className="text-green-600 hover:underline text-xs">Complete</button>
                        )}
                        <button onClick={() => openEdit(task)} className="text-sidebar hover:underline text-xs">Edit</button>
                        <button onClick={() => setDeleteId(task.id)} className="text-red-500 hover:underline text-xs">Delete</button>
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
        title={editId ? 'Edit Task' : 'Add Follow-up Task'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Institution *</label>
            <select value={form.institution_id} onChange={(e) => setForm({ ...form, institution_id: e.target.value })}
              required className="w-full px-3 py-2 border rounded-lg" disabled={editId}>
              <option value="">Select institution</option>
              {institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Title *</label>
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })}
              required className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Task Type *</label>
              <select value={form.task_type} onChange={(e) => setForm({ ...form, task_type: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg">
                {TASK_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Priority *</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className="w-full px-3 py-2 border rounded-lg">
                {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Due Date *</label>
            <input type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })}
              required className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Assigned To</label>
            <select value={form.assigned_to_id} onChange={(e) => setForm({ ...form, assigned_to_id: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg">
              <option value="">Auto-assign</option>
              {users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={3} className="w-full px-3 py-2 border rounded-lg" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border rounded-lg">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-sidebar text-white rounded-lg">
              {editId ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog isOpen={deleteId !== null} onClose={() => setDeleteId(null)}
        onConfirm={handleDelete} title="Delete Task" message="Are you sure you want to delete this task?"
        confirmText="Delete" />
    </div>
  )
}
