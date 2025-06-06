let selectedEvent = null;

function confirmDelete() {
    const code = document.getElementById("delete-code").value;
    fetch("/delete_reservation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: selectedEvent.startStr, code })
    })
    .then(async res => {
        if (res.status === 200) {
            location.reload();
        } else {
            const data = await res.json().catch(() => ({}));
            const msg = data.message || "❌ Code incorrect";
            const err = document.getElementById("delete-error");
            err.textContent = msg;
            err.style.display = "block";
        }
    });
}

function cancelDelete() {
    document.getElementById("delete-modal").style.display = "none";
    selectedEvent = null;
}

function closeConfirm() {
    document.getElementById("confirm-modal").style.display = "none";
    location.reload();
}

function printReceipt() {
    const href = document.getElementById("receipt-open").href;
    window.open(href + "?auto_print=1", "_blank");
}

function showError(message) {
    const box = document.getElementById("error-box");
    box.textContent = message;
    box.style.display = "block";
    setTimeout(() => { box.style.display = "none"; }, 5000);
}

function showConfirmation(reservation) {
    const details = `Chambre ${reservation.chambre}<br>Date : ${reservation.date}<br>Début : ${reservation.start.split('T')[1]}<br>Fin : ${reservation.end.split('T')[1]}<br>Code : ${reservation.code}`;
    document.getElementById("receipt-details").innerHTML = details;
    document.getElementById("receipt-open").href = `/receipt/${reservation.id}`;
    document.getElementById("receipt-download").href = `/receipt/${reservation.id}?pdf=1`;
    document.getElementById("confirm-modal").style.display = "flex";
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("darkToggle").onclick = () => {
        document.body.classList.toggle("dark-mode");
        document.getElementById("darkToggle").textContent =
            document.body.classList.contains("dark-mode") ? "☀️" : "🌘";
    };

    for (let i = 1; i <= 54; i++) {
        if (i === 13) continue; // la chambre 13 n'existe pas
        document.getElementById("chambre").add(new Option("Chambre " + i, i));
    }

    const heureSelect = document.getElementById("heure");
    function updateHeureOptions() {
        const dateInput = document.getElementById("date").value;
        const now = new Date();
        const todayStr = now.toISOString().split('T')[0];
        heureSelect.innerHTML = "";
        for (let h = 7; h <= 22; h++) {
            const heureStr = h.toString().padStart(2, '0') + ":00";
            if (dateInput > todayStr || (dateInput === todayStr && h > now.getHours())) {
                const opt = document.createElement("option");
                opt.value = heureStr;
                opt.text = heureStr;
                heureSelect.appendChild(opt);
            }
        }
    }
    document.getElementById("date").addEventListener("change", updateHeureOptions);
    updateHeureOptions();

    const calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
        initialView: 'timeGridDay',
        locale: 'fr',
        slotMinTime: '07:00:00',
        slotMaxTime: '23:00:00',
        height: 'auto',
        expandRows: true,
        events: '/get_reservations',
        eventDidMount: function(info) {
            const now = new Date();
            const eventEnd = new Date(info.event.end);
            if (eventEnd < now) {
                info.el.style.opacity = "0.5";
                info.el.style.backgroundColor = "#888";
                info.el.style.borderColor = "#666";
            } else if (info.event.extendedProps.machine === 'lave-linge') {
                info.el.style.backgroundColor = '#3498db';
            } else if (info.event.extendedProps.machine === 'sèche-linge') {
                info.el.style.backgroundColor = '#e67e22';
            }
        },
        eventClick: function(info) {
            selectedEvent = info.event;
            document.getElementById("delete-code").value = "";
            document.getElementById("delete-error").style.display = "none";
            document.getElementById("delete-modal").style.display = "flex";
        }
    });
    calendar.render();

    document.getElementById("reservation-form").addEventListener("submit", e => {
        e.preventDefault();

        const date = document.getElementById("date").value;
        const heure = document.getElementById("heure").value;
        const tournees = parseInt(document.getElementById("tournees").value);
        const fullStart = new Date(date + "T" + heure);
        const fullEnd = new Date(fullStart);
        fullEnd.setHours(fullEnd.getHours() + tournees);
        const now = new Date();

        if (fullStart < now) {
            showError("❌ Impossible de réserver dans le passé.");
            return;
        }

        if (fullEnd.getHours() > 23) {
            showError("❌ La buanderie ferme à 23h00. Veuillez choisir un créneau plus tôt.");
            return;
        }

        fetch("/reserver", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                chambre: document.getElementById("chambre").value,
                date: date,
                heure: heure,
                machine: document.getElementById("machine").value,
                tournees: tournees,
                code: document.getElementById("code").value
            })
        }).then(async res => {
            const data = await res.json();
            if (res.ok) {
                showConfirmation(data.reservation);
            } else {
                showError(data.message || "❌ Erreur lors de la réservation.");
            }
        }).catch(() => {
            showError("❌ Erreur de connexion.");
        });
    });
});
