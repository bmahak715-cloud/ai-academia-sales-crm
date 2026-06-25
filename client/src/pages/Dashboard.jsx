import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { dashboardApi } from '../services'
import Badge from '../components/Badge'
import { priorityColor, statusColor, formatDate } from '../utils/constants'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi.get()
      .then((res) => setData(res.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Loading dashboard...</div>
  if (!data) return <div className="text-center py-12 text-red-500">Failed to load dashboard</div>

  const { cards, stats, pipeline, upcoming_meetings, follow_ups_due_today,
    high_priority_leads, recent_activities, top_ai_insight } = data

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Institutions Contacted', value: cards.total_institutions_contacted, color: 'bg-blue-500' },
          { label: 'Active Leads', value: cards.active_leads, color: 'bg-green-500' },
          { label: 'Meetings Scheduled', value: cards.meetings_scheduled, color: 'bg-purple-500' },
          { label: 'Conversion Rate', value: cards.conversion_status, color: 'bg-accent' },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-xl shadow-sm border p-5">
            <div className={`w-10 h-10 ${card.color} rounded-lg flex items-center justify-center text-white text-lg mb-3`}>
              {card.label.charAt(0)}
            </div>
            <p className="text-2xl font-bold text-gray-800">{card.value}</p>
            <p className="text-sm text-gray-500 mt-1">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {[
          { label: 'Total Leads', value: stats.total_leads },
          { label: 'New Leads', value: stats.new_leads },
          { label: 'High Priority', value: stats.high_priority_leads },
          { label: 'Due Today', value: stats.follow_ups_due_today },
          { label: 'Overdue', value: stats.overdue_follow_ups },
          { label: 'Closed-Won', value: stats.closed_won },
          { label: 'Closed-Lost', value: stats.closed_lost },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-lg border p-3 text-center">
            <p className="text-lg font-bold text-gray-800">{s.value}</p>
            <p className="text-xs text-gray-500">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-5">
        <h2 className="text-lg font-semibold mb-4">Sales Pipeline</h2>
        <div className="flex flex-wrap gap-2">
          {pipeline.map((p) => (
            <div key={p.status} className="flex-1 min-w-[100px] bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xl font-bold text-sidebar">{p.count}</p>
              <p className="text-xs text-gray-500 mt-1">{p.status}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Upcoming Meetings</h2>
          {upcoming_meetings.length === 0 ? (
            <p className="text-gray-500 text-sm">No upcoming meetings</p>
          ) : (
            <div className="space-y-3">
              {upcoming_meetings.map((m) => (
                <div key={m.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{m.institution_name}</p>
                    <p className="text-xs text-gray-500">{formatDate(m.meeting_date)} at {m.meeting_time}</p>
                  </div>
                  <Badge className={statusColor(m.status)}>{m.status}</Badge>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Follow-ups Due Today</h2>
          {follow_ups_due_today.length === 0 ? (
            <p className="text-gray-500 text-sm">No follow-ups due today</p>
          ) : (
            <div className="space-y-3">
              {follow_ups_due_today.map((f) => (
                <div key={f.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{f.title}</p>
                    <p className="text-xs text-gray-500">{f.institution_name}</p>
                  </div>
                  <Badge className={priorityColor(f.priority)}>{f.priority}</Badge>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">High-Priority Leads</h2>
          {high_priority_leads.length === 0 ? (
            <p className="text-gray-500 text-sm">No high-priority leads</p>
          ) : (
            <div className="space-y-3">
              {high_priority_leads.map((l) => (
                <Link key={l.id} to={`/leads/${l.id}`} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                  <div>
                    <p className="font-medium text-sm">{l.name}</p>
                    <p className="text-xs text-gray-500">{l.program_interest}</p>
                  </div>
                  <Badge className={priorityColor(l.ai_analysis?.priority)}>
                    Score: {l.ai_analysis?.score}
                  </Badge>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-5">
          <h2 className="text-lg font-semibold mb-4">Top AI Insight</h2>
          {top_ai_insight ? (
            <div className="p-4 bg-gradient-to-br from-sidebar/5 to-accent/10 rounded-lg">
              <p className="font-semibold text-sidebar">{top_ai_insight.institution_name}</p>
              <div className="flex gap-2 mt-2">
                <Badge className={priorityColor(top_ai_insight.priority)}>
                  {top_ai_insight.priority} ({top_ai_insight.score})
                </Badge>
              </div>
              <p className="text-sm text-gray-600 mt-3">{top_ai_insight.reason}</p>
              <p className="text-sm text-accentDark mt-2 font-medium">{top_ai_insight.next_best_action}</p>
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No AI insights available</p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-5">
        <h2 className="text-lg font-semibold mb-4">Recent Activities</h2>
        {recent_activities.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent activities</p>
        ) : (
          <div className="space-y-2">
            {recent_activities.map((a) => (
              <div key={a.id} className="flex justify-between items-start p-3 bg-gray-50 rounded-lg text-sm">
                <div>
                  <span className="font-medium">{a.activity_type}</span>
                  <span className="text-gray-500"> — {a.description}</span>
                </div>
                <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {new Date(a.created_at).toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
