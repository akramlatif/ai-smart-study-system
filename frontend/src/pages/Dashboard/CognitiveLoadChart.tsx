import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { Card } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const data = {
  labels,
  datasets: [
    {
      label: 'Study Sessions',
      data: [3, 5, 2, 7, 4, 6, 3],
      backgroundColor: '#7c3aed',
      borderRadius: 6,
    },
    {
      label: 'Quiz Questions',
      data: [5, 8, 3, 10, 6, 9, 4],
      backgroundColor: '#06b6d4',
      borderRadius: 6,
    },
  ],
}

const options = {
  responsive: true,
  plugins: {
    legend: { position: 'top' as const },
    title: { display: false },
  },
  scales: {
    y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
    x: { grid: { display: false } },
  },
}

export function CognitiveLoadChart() {
  return (
    <Card className="p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900">Weekly Activity</h2>
        <Badge variant="synthesized">OPTIMAL</Badge>
      </div>
      <Bar data={data} options={options} />
    </Card>
  )
}
