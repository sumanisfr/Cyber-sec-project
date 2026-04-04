export const DASHBOARD_REFRESH_EVENT = 'cybershield-dashboard-refresh';

export function notifyDashboardRefresh() {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event(DASHBOARD_REFRESH_EVENT));
  }
}