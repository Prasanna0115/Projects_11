const dateInput = document.querySelector("#schedule-date");
const appointmentsBody = document.querySelector("#appointments-body");
const emptyState = document.querySelector("#empty-state");
const appointmentDialog = document.querySelector("#appointment-dialog");
const appointmentForm = document.querySelector("#appointment-form");
const formMessage = document.querySelector("#form-message");
const toast = document.querySelector("#toast");
let doctors = [];
let slots = [];
let appointments = [];

function localDateString(date = new Date()) {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 10);
}

function formatDate(value, options = { weekday: "long", month: "long", day: "numeric", year: "numeric" }) {
  return new Intl.DateTimeFormat(undefined, options).format(new Date(`${value}T12:00:00`));
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...options.headers },
  });
  if (!response.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const body = await response.json();
      if (body.error) message = body.error;
    } catch {
      // Keep the generic message if the server did not return JSON.
    }
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 2800);
}

function renderAppointments() {
  appointmentsBody.replaceChildren();
  emptyState.hidden = appointments.length !== 0;
  document.querySelector(".schedule-table-wrap table").hidden = appointments.length === 0;
  document.querySelector("#total-count").textContent = String(appointments.length).padStart(2, "0");
  document.querySelector("#appointment-count").textContent =
    `${appointments.length} ${appointments.length === 1 ? "APPOINTMENT" : "APPOINTMENTS"}`;
  document.querySelector("#selected-date-label").textContent =
    dateInput.value === localDateString() ? "Today" : formatDate(dateInput.value);
  document.querySelector("#schedule-description").textContent =
    formatDate(dateInput.value, { weekday: "long", month: "long", day: "numeric" });

  const next = appointments[0];
  document.querySelector("#next-up").textContent = next ? next.time : "—";
  document.querySelector("#next-up-doctor").textContent = next
    ? next.doctor_name
    : "No upcoming visits";

  for (const appointment of appointments) {
    const row = document.createElement("tr");
    const time = document.createElement("td");
    time.className = "time-cell";
    time.textContent = appointment.time;

    const patientCell = document.createElement("td");
    const patient = document.createElement("div");
    patient.className = "patient-cell";
    const avatar = document.createElement("span");
    avatar.className = "patient-avatar";
    avatar.textContent = appointment.patient_name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
    const patientInfo = document.createElement("span");
    patientInfo.className = "patient-info";
    const name = document.createElement("strong");
    name.textContent = appointment.patient_name;
    const email = document.createElement("small");
    email.textContent = appointment.patient_email;
    patientInfo.append(name, email);
    patient.append(avatar, patientInfo);
    patientCell.append(patient);

    const doctorCell = document.createElement("td");
    doctorCell.textContent = appointment.doctor_name;
    const specialtyCell = document.createElement("td");
    const specialty = document.createElement("span");
    specialty.className = "specialty-tag";
    specialty.textContent = appointment.specialty;
    specialtyCell.append(specialty);

    const actionCell = document.createElement("td");
    actionCell.className = "action-cell";
    const cancel = document.createElement("button");
    cancel.className = "cancel-button";
    cancel.type = "button";
    cancel.textContent = "Cancel";
    cancel.setAttribute("aria-label", `Cancel ${appointment.patient_name}'s appointment at ${appointment.time}`);
    cancel.addEventListener("click", () => cancelAppointment(appointment));
    actionCell.append(cancel);
    row.append(time, patientCell, doctorCell, specialtyCell, actionCell);
    appointmentsBody.append(row);
  }
}

async function loadAppointments() {
  appointments = await api(`/api/appointments?date=${encodeURIComponent(dateInput.value)}`);
  renderAppointments();
}

function fillSelect(select, items, placeholder) {
  select.replaceChildren();
  const first = document.createElement("option");
  first.value = "";
  first.textContent = placeholder;
  first.disabled = true;
  first.selected = true;
  select.append(first);
  for (const item of items) {
    const option = document.createElement("option");
    if (typeof item === "string") {
      option.value = item;
      option.textContent = item;
    } else {
      option.value = item.id;
      option.textContent = `${item.name} · ${item.specialty}`;
    }
    select.append(option);
  }
}

function openDialog() {
  appointmentForm.reset();
  formMessage.hidden = true;
  formMessage.textContent = "";
  document.querySelector("#appointment-date").value = dateInput.value;
  document.querySelector("#appointment-date").min = localDateString();
  fillSelect(document.querySelector("#doctor-select"), doctors, "Choose a doctor");
  fillSelect(document.querySelector("#time-select"), slots, "Choose a time");
  appointmentDialog.showModal();
}

async function cancelAppointment(appointment) {
  if (!window.confirm(`Cancel ${appointment.patient_name}'s appointment at ${appointment.time}?`)) return;
  try {
    await api(`/api/appointments/${appointment.id}`, { method: "DELETE" });
    await loadAppointments();
    showToast("Appointment cancelled.");
  } catch (error) {
    showToast(error.message);
  }
}

document.querySelector("#new-appointment-button").addEventListener("click", openDialog);
document.querySelector("#empty-add-button").addEventListener("click", openDialog);
document.querySelector("#close-dialog").addEventListener("click", () => appointmentDialog.close());
document.querySelector("#cancel-dialog").addEventListener("click", () => appointmentDialog.close());
document.querySelector("#today-button").addEventListener("click", () => {
  dateInput.value = localDateString();
  loadAppointments().catch((error) => showToast(error.message));
});
document.querySelector("#previous-day").addEventListener("click", () => {
  const day = new Date(`${dateInput.value}T12:00:00`);
  day.setDate(day.getDate() - 1);
  dateInput.value = localDateString(day);
  loadAppointments().catch((error) => showToast(error.message));
});
document.querySelector("#next-day").addEventListener("click", () => {
  const day = new Date(`${dateInput.value}T12:00:00`);
  day.setDate(day.getDate() + 1);
  dateInput.value = localDateString(day);
  loadAppointments().catch((error) => showToast(error.message));
});
dateInput.addEventListener("change", () => {
  loadAppointments().catch((error) => showToast(error.message));
});

appointmentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const saveButton = document.querySelector("#save-appointment");
  saveButton.disabled = true;
  formMessage.hidden = true;
  const form = new FormData(appointmentForm);
  const payload = Object.fromEntries(form.entries());
  try {
    await api("/api/appointments", { method: "POST", body: JSON.stringify(payload) });
    appointmentDialog.close();
    dateInput.value = payload.date;
    await loadAppointments();
    showToast("Appointment added to the schedule.");
  } catch (error) {
    formMessage.textContent = error.message;
    formMessage.hidden = false;
  } finally {
    saveButton.disabled = false;
  }
});

async function start() {
  dateInput.value = localDateString();
  try {
    [doctors, slots] = await Promise.all([api("/api/doctors"), api("/api/slots")]);
    document.querySelector("#doctor-count").textContent = String(doctors.length).padStart(2, "0");
    await loadAppointments();
  } catch (error) {
    showToast(error.message);
  }
}

start();
