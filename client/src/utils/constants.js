export const INSTITUTION_TYPES = [
  'Private University', 'Government University', 'Engineering College',
  'Management College', 'Degree College', 'Training Institute', 'Other',
]

export const PROGRAM_INTERESTS = [
  'Artificial Intelligence', 'Machine Learning', 'Data Science',
  'Web Development', 'Cloud Computing', 'Cybersecurity',
  'Placement Training', 'Faculty Development Program', 'Workshop', 'Other',
]

export const LEAD_SOURCES = [
  'Website', 'Referral', 'LinkedIn', 'Education Conference',
  'Email Campaign', 'Existing Partner', 'Manual Research', 'Other',
]

export const LEAD_STATUSES = [
  'New Lead', 'Contacted', 'Meeting Scheduled', 'Proposal Sent',
  'Negotiation', 'Closed-Won', 'Closed-Lost',
]

export const TASK_TYPES = [
  'Phone Call', 'Email Follow-up', 'Send Brochure', 'Schedule Meeting',
  'Proposal Follow-up', 'Negotiation Follow-up', 'General Follow-up',
]

export const PRIORITIES = ['High', 'Medium', 'Low']

export const MEETING_MODES = ['Online', 'Offline']

export const MEETING_STATUSES = ['Scheduled', 'Completed', 'Cancelled']

export function priorityColor(priority) {
  switch (priority) {
    case 'High': return 'bg-red-100 text-red-700 border-red-200'
    case 'Medium': return 'bg-orange-100 text-orange-700 border-orange-200'
    case 'Low': return 'bg-green-100 text-green-700 border-green-200'
    default: return 'bg-gray-100 text-gray-700 border-gray-200'
  }
}

export function statusColor(status) {
  const map = {
    'New Lead': 'bg-blue-100 text-blue-700',
    'Contacted': 'bg-indigo-100 text-indigo-700',
    'Meeting Scheduled': 'bg-purple-100 text-purple-700',
    'Proposal Sent': 'bg-yellow-100 text-yellow-700',
    'Negotiation': 'bg-orange-100 text-orange-700',
    'Closed-Won': 'bg-green-100 text-green-700',
    'Closed-Lost': 'bg-red-100 text-red-700',
    'Pending': 'bg-yellow-100 text-yellow-700',
    'Completed': 'bg-green-100 text-green-700',
    'Overdue': 'bg-red-100 text-red-700',
    'Scheduled': 'bg-blue-100 text-blue-700',
    'Cancelled': 'bg-gray-100 text-gray-700',
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

export function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
}
