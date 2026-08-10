// EduSense Interactive Dashboard & Modal Handlers

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Mobile Navigation Drawer Toggle
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.querySelector('.app-sidebar');
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener('click', () => {
      sidebar.classList.toggle('active');
    });
  }

  // Initialize Performance Donut Chart
  const perfCanvas = document.getElementById('performanceChart');
  if (perfCanvas) {
    const good = parseInt(perfCanvas.dataset.good || 0);
    const warning = parseInt(perfCanvas.dataset.warning || 0);
    const risk = parseInt(perfCanvas.dataset.risk || 0);

    new Chart(perfCanvas, {
      type: 'doughnut',
      data: {
        labels: ['Good Standing', 'Warning Status', 'At Risk'],
        datasets: [{
          data: [good, warning, risk],
          backgroundColor: ['#34C759', '#FF9500', '#FF3B30'],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              font: { family: '-apple-system, sans-serif', size: 12 },
              padding: 16
            }
          }
        }
      }
    });
  }

  // Initialize Attendance Distribution Bar Chart
  const attCanvas = document.getElementById('attendanceChart');
  if (attCanvas) {
    const counts = JSON.parse(attCanvas.dataset.counts || '[0,0,0,0,0]');

    new Chart(attCanvas, {
      type: 'bar',
      data: {
        labels: ['< 50%', '50–60%', '60–75%', '75–90%', '90–100%'],
        datasets: [{
          label: 'Students Count',
          data: counts,
          backgroundColor: ['#FF3B30', '#FF9500', '#FFCC00', '#34C759', '#0071E3'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { stepSize: 1 } }
        }
      }
    });
  }

  // Initialize Marks Score Ranges Bar Chart
  const marksCanvas = document.getElementById('marksChart');
  if (marksCanvas) {
    const counts = JSON.parse(marksCanvas.dataset.counts || '[0,0,0,0,0]');

    new Chart(marksCanvas, {
      type: 'bar',
      data: {
        labels: ['0–40 Marks', '40–50 Marks', '50–70 Marks', '70–85 Marks', '85–100 Marks'],
        datasets: [{
          label: 'Students Count',
          data: counts,
          backgroundColor: '#0071E3',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(0,0,0,0.04)' }, ticks: { stepSize: 1 } }
        }
      }
    });
  }

  // Student Registry Filtering (Search, Status, Department)
  const searchInput = document.getElementById('studentSearch');
  const statusFilter = document.getElementById('statusFilter');
  const deptFilter = document.getElementById('deptFilter');

  if (searchInput || statusFilter || deptFilter) {
    const filterRows = () => {
      const query = (searchInput?.value || '').toLowerCase().trim();
      const selectedStatus = (statusFilter?.value || 'all').toLowerCase();
      const selectedDept = (deptFilter?.value || 'all').toLowerCase();

      document.querySelectorAll('.student-row').forEach(row => {
        const name = (row.dataset.name || '').toLowerCase();
        const id = (row.dataset.id || '').toLowerCase();
        const status = (row.dataset.status || '').toLowerCase();
        const dept = (row.dataset.dept || '').toLowerCase();

        const matchesQuery = !query || name.includes(query) || id.includes(query);
        const matchesStatus = selectedStatus === 'all' || status === selectedStatus;
        const matchesDept = selectedDept === 'all' || dept === selectedDept;

        if (matchesQuery && matchesStatus && matchesDept) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    };

    if (searchInput) searchInput.addEventListener('input', filterRows);
    if (statusFilter) statusFilter.addEventListener('change', filterRows);
    if (deptFilter) deptFilter.addEventListener('change', filterRows);
  }
});

// Student Detail Modal Fetch & Display
function openStudentModal(studentId) {
  const modal = document.getElementById('studentDetailModal');
  const modalContent = document.getElementById('modalContent');
  if (!modal || !modalContent) return;

  modalContent.innerHTML = `
    <div style="text-align:center; padding:40px;">
      <p style="color:var(--text-secondary);">Loading student details...</p>
    </div>
  `;
  modal.classList.add('active');

  fetch(`/student/${studentId}`)
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        modalContent.innerHTML = `<p style="color:var(--color-risk);">${data.error}</p>`;
        return;
      }

      const statusBadge = data.Status === 'Good' ? 'badge-good' : (data.Status === 'Warning' ? 'badge-warning' : 'badge-risk');
      const reasonsList = (data.Reasons || []).map(r => `<li>${r}</li>`).join('');

      modalContent.innerHTML = `
        <div style="margin-bottom:20px;">
          <span class="badge-status ${statusBadge}" style="margin-bottom:10px;">
            <span class="dot"></span> ${data.Status}
          </span>
          <h2 style="font-size:24px; font-weight:700; margin-bottom:2px;">${data.Name}</h2>
          <p style="font-size:13px; color:var(--text-secondary);">${data['Student ID']} • ${data.Department} • ${data.Year}</p>
          <p style="font-size:13px; color:var(--text-muted);">${data.Email}</p>
        </div>

        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-bottom:24px;">
          <div style="background:var(--bg-primary); padding:12px; border-radius:12px; text-align:center;">
            <span style="font-size:11px; color:var(--text-secondary); display:block;">Attendance</span>
            <strong style="font-size:18px; color:${data.Attendance < 75 ? 'var(--color-risk)' : 'var(--text-primary)'};">${data.Attendance}%</strong>
          </div>
          <div style="background:var(--bg-primary); padding:12px; border-radius:12px; text-align:center;">
            <span style="font-size:11px; color:var(--text-secondary); display:block;">Marks</span>
            <strong style="font-size:18px; color:${data.Marks < 50 ? 'var(--color-risk)' : 'var(--text-primary)'};">${data.Marks}/100</strong>
          </div>
          <div style="background:var(--bg-primary); padding:12px; border-radius:12px; text-align:center;">
            <span style="font-size:11px; color:var(--text-secondary); display:block;">Assignment</span>
            <strong style="font-size:18px;">${data.Assignment}%</strong>
          </div>
        </div>

        <div style="margin-bottom:20px;">
          <h4 style="font-size:14px; font-weight:600; margin-bottom:8px;">Evaluation Reasons</h4>
          <ul style="font-size:13px; color:var(--text-secondary); padding-left:20px; line-height:1.6;">
            ${reasonsList}
          </ul>
        </div>

        <div style="background:var(--color-accent-bg); border:1px solid rgba(0,113,227,0.15); padding:14px; border-radius:14px; margin-bottom:24px;">
          <h4 style="font-size:13px; font-weight:600; color:var(--color-accent); margin-bottom:4px;">Recommended Action</h4>
          <p style="font-size:13px; color:var(--text-primary); margin:0;">${data.Recommendation}</p>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:10px;">
          <button class="btn-apple btn-secondary-apple" onclick="closeStudentModal()">Close</button>
          <button class="btn-apple btn-primary-apple" onclick="sendIndividualEmail('${data['Student ID']}')">
            Send Alert Email
          </button>
        </div>
      `;
    })
    .catch(err => {
      modalContent.innerHTML = `<p style="color:var(--color-risk);">Failed to load student details.</p>`;
    });
}

function closeStudentModal() {
  const modal = document.getElementById('studentDetailModal');
  if (modal) modal.classList.remove('active');
}

// 1-Click Sample Demo Loader
function loadSampleData() {
  fetch('/api/load-sample', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = '/dashboard';
      } else {
        alert(data.message || 'Error loading sample dataset.');
      }
    });
}

// Single Email Dispatch Trigger
function sendIndividualEmail(studentId) {
  fetch('/api/send-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: studentId })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  })
  .catch(() => alert('Network error sending email.'));
}

// Bulk Email Dispatch Trigger
function sendBulkAlerts() {
  if (!confirm('Are you sure you want to send academic alert emails to all Warning and At-Risk students?')) return;

  fetch('/api/send-bulk-emails', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  })
  .catch(() => alert('Network error sending bulk emails.'));
}
