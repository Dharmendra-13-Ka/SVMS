console.log("SVMS Started");

const API = "https://svms-zgsx.onrender.com/data";

function searchDevice() {

    const device = document.getElementById("deviceId").value.trim();

   if (device === "") {

    document.getElementById("deviceName").innerHTML = "Device ID : --";

    document.getElementById("voltage").innerHTML =
        "Current Voltage : --";

    document.getElementById("minvoltage").innerHTML =
        "Minimum Voltage : --";

    document.getElementById("maxvoltage").innerHTML =
        "Maximum Voltage : --";

    document.getElementById("current").innerHTML =
        "Current : --";

    document.getElementById("mincurrent").innerHTML =
        "Minimum Current : --";

    document.getElementById("maxcurrent").innerHTML =
        "Maximum Current : --";

    document.getElementById("power").innerHTML =
        "Power : --";

    document.getElementById("relay").innerHTML =
        "Relay Status : --";

    document.getElementById("charger").innerHTML =
        "Charger Status : --";

    document.getElementById("alarm").innerHTML =
        "Alarm : --";

    return;
}

    fetch(API + "?device=" + encodeURIComponent(device))
    .then(res => res.json())
  .then(data => {

    if (Array.isArray(data) || !data.device_id) {

        document.getElementById("deviceName").innerHTML =
            "Device ID : --";

        document.getElementById("voltage").innerHTML =
            "Current Voltage : --";

        document.getElementById("minvoltage").innerHTML =
            "Minimum Voltage : --";

        document.getElementById("maxvoltage").innerHTML =
            "Maximum Voltage : --";

        document.getElementById("current").innerHTML =
            "Current : --";

        document.getElementById("mincurrent").innerHTML =
            "Minimum Current : --";

        document.getElementById("maxcurrent").innerHTML =
            "Maximum Current : --";

        document.getElementById("power").innerHTML =
            "Power : --";

        document.getElementById("relay").innerHTML =
            "Relay Status : --";

        document.getElementById("charger").innerHTML =
            "Charger Status : --";

        document.getElementById("alarm").innerHTML =
            "Alarm : --";

        return;
    }

    document.getElementById("deviceName").innerHTML =
        "Device ID : " + data.device_id;
    
        document.getElementById("voltage").innerHTML =
        "Current Voltage : " + data.voltage + " V";

        document.getElementById("minvoltage").innerHTML =
        "Minimum Voltage : " + data.min_voltage + " V";

        document.getElementById("maxvoltage").innerHTML =
        "Maximum Voltage : " + data.max_voltage + " V";

        document.getElementById("current").innerHTML =
        "Current : " + data.current + " A";

        document.getElementById("mincurrent").innerHTML =
        "Minimum Current : " + data.min_current + " A";

        document.getElementById("maxcurrent").innerHTML =
        "Maximum Current : " + data.max_current + " A";

        document.getElementById("power").innerHTML =
        "Power : " + data.power + " W";

        document.getElementById("relay").innerHTML =
        "Relay Status : " + data.relay;

        document.getElementById("charger").innerHTML =
        "Charger Status : " + data.charger;

        document.getElementById("alarm").innerHTML =
        "Alarm : " + data.alarm;

    })
    .catch(err => console.log(err));

}

function relayOn()
{
    fetch("/relay", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            device_id: document.getElementById("deviceId").value || "TVS001",
            relay: "ON"
        })
    })
        .then(data => {
        console.log("Relay ON:", data);
        alert("Power ON Successfully");
        searchDevice();
    })
    .catch(err => console.log(err));
}


function relayOff()
{
    fetch("/relay", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            device_id: document.getElementById("deviceId").value || "TVS001",
            relay: "OFF"
        })
    })
    .then(response => response.json())
    
    .catch(err => console.log(err));
}

setInterval(searchDevice,1000);

function exportExcel()
{
    window.open("/exportexcel","_blank");
}
function searchFaultLog()
{
    loadFaultLog();
}
function showLive() {
    document.getElementById("livePage").style.display = "block";
    document.getElementById("faultPage").style.display = "none";
    document.getElementById("powerPage").style.display = "none";
    document.getElementById("reportPage").style.display = "none";
}

function showFault() {
    document.getElementById("livePage").style.display = "none";
    document.getElementById("faultPage").style.display = "block";
    document.getElementById("powerPage").style.display = "none";
    document.getElementById("reportPage").style.display = "none";
}

function showPower() {
    document.getElementById("livePage").style.display = "none";
    document.getElementById("faultPage").style.display = "none";
    document.getElementById("powerPage").style.display = "block";
    document.getElementById("reportPage").style.display = "none";
}

function showReport() {
    document.getElementById("livePage").style.display = "none";
    document.getElementById("faultPage").style.display = "none";
    document.getElementById("powerPage").style.display = "none";
    document.getElementById("reportPage").style.display = "block";
}

function logout() {
    window.location.href = "login.html";
}
function getReportDeviceId() {

    const device =
        document
            .getElementById("reportDeviceId")
            .value
            .trim();

    if (device === "") {

        alert("Please Enter Device ID");

        return null;
    }

    return device;
}


function exportLiveData() {

    const device = getReportDeviceId();

    if (device === null) {
        return;
    }

    window.open(
        "/exportlivedata?device="
        + encodeURIComponent(device),
        "_blank"
    );
}


function exportFaultLog() {

    const device = getReportDeviceId();

    if (device === null) {
        return;
    }

    window.open(
        "/exportexcel?device="
        + encodeURIComponent(device),
        "_blank"
    );
}


function exportFullReport() {

    const device = getReportDeviceId();

    if (device === null) {
        return;
    }

    window.open(
        "/exportfullreport?device="
        + encodeURIComponent(device),
        "_blank"
    );
}
// ==================================================
// POWER HISTORY - TVS001
// ==================================================

function searchPowerHistory() {

    // Fixed Device ID
    const deviceId = "TVS001";

fetch(
    "/powerhistory?device="
    + encodeURIComponent(deviceId)
)

    .then(response => {

        if (!response.ok) {
            throw new Error("Server Error");
        }

        return response.json();
    })

    .then(data => {

        const table =
            document.getElementById("powerTable");

        // Keep header row
        while (table.rows.length > 1) {
            table.deleteRow(1);
        }

        // No data found
        if (data.length === 0) {

            alert(
                "No Power History Found for TVS001."
            );

            return;
        }

        // Add Power History
        data.forEach(session => {

            const row = table.insertRow();

            row.insertCell(0).innerText =
                session.date || "";

            row.insertCell(1).innerText =
                session.on_time || "";

            row.insertCell(2).innerText =
                session.off_time || "Running";

            row.insertCell(3).innerText =
                session.duration || "";

            row.insertCell(4).innerText =
                session.units_used !== undefined
                    ? session.units_used + " kWh"
                    : "";

            row.insertCell(5).innerText =
                session.min_voltage !== undefined
                    ? session.min_voltage + " V"
                    : "";

            row.insertCell(6).innerText =
                session.max_voltage !== undefined
                    ? session.max_voltage + " V"
                    : "";

            row.insertCell(7).innerText =
                session.avg_voltage !== undefined
                    ? session.avg_voltage + " V"
                    : "";

            row.insertCell(8).innerText =
                session.min_current !== undefined
                    ? session.min_current + " A"
                    : "";

            row.insertCell(9).innerText =
                session.max_current !== undefined
                    ? session.max_current + " A"
                    : "";

            row.insertCell(10).innerText =
                session.avg_current !== undefined
                    ? session.avg_current + " A"
                    : "";

            row.insertCell(11).innerText =
                session.max_load !== undefined
                    ? session.max_load + " W"
                    : "";

            row.insertCell(12).innerText =
                session.avg_load !== undefined
                    ? session.avg_load + " W"
                    : "";

            row.insertCell(13).innerText =
                session.status || "";

        });

    })

    .catch(error => {

        console.error(
            "Power History Error:",
            error
        );

        alert(
            "Power History load nahi ho paayi."
        );

    });
}