import React, { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import axios from './api';
import { DASHBOARD_REFRESH_EVENT } from './dashboardEvents';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const defaultStats = {
  total_activity: 0,
  total_scans: 0,
  malware_detected: 0,
  vulnerability_reports: 0,
  job_scam_checks: 0,
  fraud_detected: 0,
};

function Dashboard() {
  const [stats, setStats] = useState(defaultStats);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchStats = async ({ silent = false } = {}) => {
      try {
        if (!silent) {
          setLoading(true);
        }
        const res = await axios.get('/api/stats/summary');
        if (!cancelled) {
          setStats({ ...defaultStats, ...(res.data || {}) });
        }
      } catch {
        if (!cancelled) {
          setStats(defaultStats);
        }
      } finally {
        if (!silent && !cancelled) {
          setLoading(false);
        }
      }
    };

    fetchStats();

    const handleRefresh = () => fetchStats({ silent: true });
    window.addEventListener(DASHBOARD_REFRESH_EVENT, handleRefresh);
    const timer = window.setInterval(handleRefresh, 5000);

    return () => {
      cancelled = true;
      window.removeEventListener(DASHBOARD_REFRESH_EVENT, handleRefresh);
      window.clearInterval(timer);
    };
  }, []);

  const chartData = {
    labels: ['Total Activity', 'Malware Hits', 'Vulnerability Reports', 'Job Scam Checks'],
    datasets: [
      {
        label: 'Events',
        data: [stats.total_activity, stats.malware_detected, stats.vulnerability_reports, stats.job_scam_checks],
        backgroundColor: ['#6d8fe5', '#ef7d7d', '#e6b46b', '#74c8bf'],
        borderRadius: 12,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
    },
    scales: {
      x: {
        grid: { display: false },
      },
      y: {
        beginAtZero: true,
        ticks: { precision: 0 },
      },
    },
  };

  return (
    <div className="dashboard-shell">
      <section className="dashboard-hero">
        <div className="dashboard-hero-copy">
          <span className="eyebrow soft">SOC Workspace</span>
          <h1>Security Dashboard</h1>
          <p>Run malware scans, inspect websites, and screen suspicious job offers from one clean command center.</p>
        </div>
        <div className="dashboard-overview-card">
          <strong>Live overview</strong>
          <span>{loading ? 'Refreshing telemetry...' : 'Telemetry ready'}</span>
        </div>
      </section>

      <section className="dashboard-metric-grid">
        <div className="dashboard-metric-card">
          <span>Total Activity</span>
          <strong>{stats.total_activity}</strong>
        </div>
        <div className="dashboard-metric-card">
          <span>Malware Hits</span>
          <strong>{stats.malware_detected}</strong>
        </div>
        <div className="dashboard-metric-card">
          <span>Vulnerability Reports</span>
          <strong>{stats.vulnerability_reports}</strong>
        </div>
        <div className="dashboard-metric-card">
          <span>Job Scam Checks</span>
          <strong>{stats.job_scam_checks}</strong>
        </div>
      </section>

      <section className="dashboard-content-grid">
        <div className="dashboard-panel chart-panel">
          <h3>Trend Overview</h3>
          <div className="chart-frame">
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>

        <div className="dashboard-panel workflow-panel">
          <h3>Included Workflows</h3>
          <div className="workflow-stack">
            <div className="workflow-card">
              <strong>Malware Lab</strong>
              <p>Inspect suspicious files with hash checks, entropy analysis, and downloadable reports.</p>
            </div>
            <div className="workflow-card">
              <strong>Website Scanner</strong>
              <p>Review headers, exposure paths, open ports, and common web attack indicators.</p>
            </div>
            <div className="workflow-card">
              <strong>Job Scam Checker</strong>
              <p>Flag fake hiring patterns like payment requests, pressure tactics, and suspicious recruiter behavior.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
