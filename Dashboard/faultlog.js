async function loadFaultLog() {

    try {

        const device = document
            .getElementById("faultDeviceId")
            .value
            .trim();

        if (device === "") {
            return;
        }

        const response = await fetch(
            "/faultlog?device="
            + encodeURIComponent(device)
        );

        const faults = await response.json();

        const table =
            document.getElementById("faultTable");

        while (table.rows.length > 1) {
            table.deleteRow(1);
        }

        faults.forEach(function(item) {

            const row = table.insertRow();

            row.insertCell(0).innerHTML =
                item.date || "";

            row.insertCell(1).innerHTML =
                item.fault_start || "";

            row.insertCell(2).innerHTML =
                item.start_voltage !== undefined &&
                item.start_voltage !== ""
                    ? item.start_voltage + " V"
                    : "";

            row.insertCell(3).innerHTML =
                item.fault || "";

            row.insertCell(4).innerHTML =
                item.relay || "";

            row.insertCell(5).innerHTML =
                item.fault_resolve || "";

            row.insertCell(6).innerHTML =
                item.resolve_voltage !== undefined &&
                item.resolve_voltage !== ""
                    ? item.resolve_voltage + " V"
                    : "";

            row.insertCell(7).innerHTML =
                item.fault_duration || "";

            row.insertCell(8).innerHTML =
                item.status || "";

        });

    }

    catch(error) {

        console.log("Fault Log Error:", error);

    }
}


function searchFaultLog() {

    loadFaultLog();

}


function clearFaultLog() {

    const device = document
        .getElementById("faultDeviceId")
        .value
        .trim();

    if (device === "") {

        alert("Please Enter Device ID");
        return;

    }

    if (!confirm(
        "Clear Fault Log from screen for " + device + "?"
    )) {

        return;

    }

    fetch(
        "/clearfaultlog?device="
        + encodeURIComponent(device),
        {
            method: "POST"
        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.status === "OK") {

            alert("Fault Log Cleared");

            loadFaultLog();

        }

        else {

            alert(
                data.message ||
                "Unable to clear Fault Log"
            );

        }

    })

    .catch(error => {

        console.log(
            "Clear Fault Log Error:",
            error
        );

        alert("Server Error");

    });

}


setInterval(loadFaultLog, 1000);