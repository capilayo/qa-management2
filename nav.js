// nav.js — builds the shared sidebar HTML
function buildSidebar(activePage) {
  const items = [
    { id: "dashboard",        href: "index.html",           section: "Overview",  label: "Dashboard",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>` },
    { id: "submit-request",   href: "#",                    section: "Requests",  label: "Submit Request",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 4v16m8-8H4"/></svg>` },
    { id: "request-queue",    href: "#",                    section: "Requests",  label: "Request Queue",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>` },
    { id: "audit-workloads",  href: "#",                    section: "Audits",   label: "Audit Workloads",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M9 17v-2m3 2v-4m3 4v-6M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>` },
    { id: "qa-availability",  href: "qa-availability.html", section: "Team",     label: "QA Availability",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>` },
    { id: "user-management",  href: "user-management.html", section: "Team",     label: "User Management",
      icon: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M17 20h5v-2a4 4 0 00-5-3.87M9 20H4v-2a4 4 0 015-3.87m6-4a4 4 0 11-8 0 4 4 0 018 0z"/></svg>` },
  ];

  let html = `
    <div class="sidebar-brand">
      <div class="app-name">QA System</div>
      <div class="app-sub">Quality Assurance Management</div>
    </div>`;

  let currentSection = "";
  items.forEach(item => {
    if (item.section !== currentSection) {
      currentSection = item.section;
      html += `<div class="sidebar-section"><div class="sidebar-section-label">${currentSection}</div>`;
    }
    const active = item.id === activePage ? " active" : "";
    html += `<a href="${item.href}" class="sidebar-item${active}">${item.icon}${item.label}</a>`;
  });
  html += `</div>`; // close last section

  html += `
    <div class="sidebar-bottom">
      <div class="avatar-sm" style="background:#4f46e5;">A</div>
      <div>
        <div class="name">Admin User</div>
        <div class="role">Administrator</div>
      </div>
    </div>`;

  return html;
}
