console.log("SVMS Started");

const API = "/data";

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
    alert("Relay ON");
}

function relayOff()
{
    alert("Relay OFF");
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