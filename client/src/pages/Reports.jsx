import { useState, useEffect } from 'react'
import { dashboardApi } from '../services'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line,
} from 'recharts'

const COLORS = ['#1a4d2e', '#2d6a4f', '#f4a261', '#e76f51', '#40916c', '#52b788', '#95d5b2', '#d8f3dc']
const PRIORITY_COLORS = { High: '#ef4444', Medium: '#f97316', Low: '#22c55e' }

export default function Reports() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi.reports()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Loading reports...</div>
  if (!data) return <div className="text-center py-12 text-red-500">Failed to load reports</div>

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Reports</h1>
        <div className="text-sm text-gray-500">
          Conversion Rate: <span className="font-bold text-sidebar text-lg">{data.conversion_rate}%</span>
          <span className="ml-4">Total Leads: <span className="font-bold">{data.total_leads}</span></span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Leads by Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.leads_by_status}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-20} textAnchor="end" height={60} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#1a4d2e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Leads by Priority</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={data.leads_by_priority} dataKey="value" nameKey="name" cx="50%" cy="50%"
                outerRadius={100} label>
                {data.leads_by_priority.map((entry) => (
                  <Cell key={entry.name} fill={PRIORITY_COLORS[entry.name] || COLORS[0]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Leads by Source</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.leads_by_source} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} width={120} />
              <Tooltip />
              <Bar dataKey="value" fill="#f4a261" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Leads by Institution Type</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={data.leads_by_type} dataKey="value" nameKey="name" cx="50%" cy="50%"
                outerRadius={100} label>
                {data.leads_by_type.map((entry, i) => (
                  <Cell key={entry.name} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Monthly Leads Added</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.monthly_leads}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#1a4d2e" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Closed-Won vs Closed-Lost</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={data.closed_won_vs_lost} dataKey="value" nameKey="name" cx="50%" cy="50%"
                outerRadius={100} label>
                <Cell fill="#22c55e" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-5">
        <h2 className="text-lg font-semibold mb-4">Sales Pipeline</h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={data.pipeline}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="status" tick={{ fontSize: 10 }} angle={-15} textAnchor="end" height={60} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#2d6a4f" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-sm border p-5 text-center">
          <p className="text-3xl font-bold text-blue-600">{data.meetings.scheduled}</p>
          <p className="text-sm text-gray-500 mt-1">Meetings Scheduled</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-5 text-center">
          <p className="text-3xl font-bold text-green-600">{data.meetings.completed}</p>
          <p className="text-sm text-gray-500 mt-1">Meetings Completed</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border p-5 text-center">
          <p className="text-3xl font-bold text-gray-500">{data.meetings.cancelled}</p>
          <p className="text-sm text-gray-500 mt-1">Meetings Cancelled</p>
        </div>
      </div>
    </div>
  )
}
