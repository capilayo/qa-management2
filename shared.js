// shared.js — shared state via localStorage

const DEFAULT_USERS = [
  { id: 1, name: "Maria Santos",      role: "QA Reviewer",   dept: "CX Hub",        status: "available",  task: "",                    tat: "",            updated: "Jun 10, 2025 08:30" },
  { id: 2, name: "Kevin Lim",         role: "QA Analyst",    dept: "Operations",    status: "busy",       task: "Post Audit QA",       tat: "0d 1h 14m",   updated: "Jun 10, 2025 07:28" },
  { id: 3, name: "Rose Buenaventura", role: "QA Analyst",    dept: "CX Hub",        status: "busy",       task: "Real-Time QA",        tat: "0d 3h 10m",   updated: "Jun 10, 2025 05:32" },
  { id: 4, name: "Diego Macaraeg",    role: "QA Specialist", dept: "Ground Svcs",   status: "available",  task: "",                    tat: "",            updated: "Jun 10, 2025 08:00" },
  { id: 5, name: "Sofia Abad",        role: "QA Analyst",    dept: "CX Hub",        status: "on-break",   task: "",                    tat: "",            updated: "Jun 10, 2025 08:15" },
  { id: 6, name: "Leo Pascual",       role: "QA Analyst",    dept: "MNL Hub",       status: "busy",       task: "Coaching Session",    tat: "0d 2h 55m",   updated: "Jun 10, 2025 05:47" },
  { id: 7, name: "Camille Navarro",   role: "QA Analyst",    dept: "Operations",    status: "on-leave",   task: "",                    tat: "",            updated: "Jun 9, 2025 17:30"  },
  { id: 8, name: "Noel Dizon",        role: "QA Specialist", dept: "Ground Svcs",   status: "available",  task: "",                    tat: "",            updated: "Jun 10, 2025 07:45" },
];

function getUsers() {
  const raw = localStorage.getItem("qa_users");
  if (!raw) {
    localStorage.setItem("qa_users", JSON.stringify(DEFAULT_USERS));
    return DEFAULT_USERS;
  }
  return JSON.parse(raw);
}

function saveUsers(users) {
  localStorage.setItem("qa_users", JSON.stringify(users));
}

function getInitials(name) {
  return name.trim().split(" ").map(w => w[0]).join("").substring(0, 2).toUpperCase();
}

const AVATAR_COLORS = [
  "#16a34a","#2563eb","#dc2626","#d97706","#7c3aed",
  "#0891b2","#059669","#0f766e","#9333ea","#db2777"
];

function avatarColor(id) {
  return AVATAR_COLORS[(id - 1) % AVATAR_COLORS.length];
}

const STATUS_META = {
  "available": { label: "Available",    dotClass: "green",  badgeClass: "available", borderClass: "available" },
  "busy":      { label: "Busy",         dotClass: "red",    badgeClass: "busy",      borderClass: "busy"      },
  "on-break":  { label: "On Break",     dotClass: "amber",  badgeClass: "on-break",  borderClass: "on-break"  },
  "on-leave":  { label: "On Leave",     dotClass: "purple", badgeClass: "on-leave",  borderClass: "on-leave"  },
};

function nowString() {
  const d = new Date();
  return d.toLocaleString("en-US", { month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit", hour12: false });
}
