import * as JEQL from "../../../../../JEQL/JEQL.js"

let APPLICATION_NAME = "sentinel";

let ID_ERROR_TABLE = "error-list";
let ID_CHECK_TABLE = "check-list";
let ID_SERVICES = "services";
let ID_CHECK_CHART = "check-chart";

let KEY_ID = "id";
let KEY_SOURCE_FILE = "source_file";
let KEY_ERROR_CONDENSED = "error_condensed";
let KEY_FILE_LINE_NUMBER = "file_line_number";
let KEY_VERSION = "version";
let KEY_SOURCE_SYSTEM = "source_system";
let KEY_CREATED = "created";
let KEY_USER_AGENT = "user_agent";
let KEY_IP_ADDRESS = "ip_address"
let KEY_STACKTRACE = "stacktrace";
let KEY_CHECK_AT = "check_at";
let KEY_RESPONSE_TIME_MS = "response_time_ms";
let KEY_PASSED = "passed";
let KEY_RESPONSE_CODE = "response_code";
let KEY_RAW_RESULT = "raw_result";
let KEY_NAME = "name";
let KEY_CHECK_EVERY_MS = "check_every_ms";
let KEY_URL = "url";
let KEY_ALERT_THRESHOLD_MS = "response_time_alert_threshold_ms";
let KEY_MOST_RECENT_CHECKS = "most_recent_checks";

let ACTION_FETCH_ERRORS = "GET /sentinel/errors";
let ACTION_FETCH_ERROR = "GET /sentinel/error";
let ACTION_FETCH_MANAGED_SERVICES = "GET /sentinel/managed-services";
let ACTION_FETCH_CHECKS = "GET /sentinel/managed-services/checks";
let ACTION_FETCH_CHECK = "GET /sentinel/managed-services/check";

let PARAM_MANAGED_CHECK_ID = "managed_check_id";
let PARAM_ERROR_ID = "error_id";

let MAX_CHECKS_VISIBLE = 20;

function renderCheckModal(modal, check) {
    modal.buildHTML(`
        <h3>Details about Check</h3>
        Id: <span>${check[KEY_ID]}</span><br>
        Passed: <span>${check[KEY_PASSED]}</span><br>
        Checked At: <span>${check[KEY_CHECK_AT]}</span><br>
        Response Time: <span>${check[KEY_RESPONSE_TIME_MS]}</span><br>
        Response Code: <span>${check[KEY_RESPONSE_CODE]}</span><br>
        Raw Result: <pre>${check[KEY_RAW_RESULT]}</pre>
    `);
}

function fetchAndRenderCheckModal(id) {
    let data = {};
    data[KEY_ID] = id;
    JEQL.requests.makeBody(window.JEQL_CONFIG, ACTION_FETCH_CHECK, function(data) {
        JEQL.renderModal(function(modal) { renderCheckModal(modal, data); }, true, JEQL.CLS_MODAL_WIDE);
    }, data);
}

function checkTableRowRenderer(rowElem, data, idx, superRowRenderer) {
    superRowRenderer();
    let rowObj = JEQL.tupleToObject(data[JEQL.KEY_ROWS][idx], data[JEQL.KEY_COLUMNS]);

    rowElem.buildChild("td").buildChild("button").buildText("Select").buildEventListener("click", function() {
        fetchAndRenderCheckModal(rowObj[KEY_ID]);
    });
}

function refreshCheckTable(page, size, search, sort) {
    JEQL.requests.makeBody(window.JEQL_CONFIG,
        ACTION_FETCH_CHECKS,
        function(data) {
            let checkTable = document.getElementById(ID_CHECK_TABLE);
            JEQL.pagedTableUpdate(checkTable, data);
            JEQL.tableRenderer(JEQL.objectsToTuples(data[JEQL.KEY_DATA]), checkTable, checkTableRowRenderer, [KEY_NAME]);
        },
        JEQL.getSearchObj(page, size, search, sort)
    );
}

function handleChartClick(data, evt) {
    let points = window.check_chart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);

    if (points.length) {
        fetchAndRenderCheckModal(data[points[0].index][KEY_ID]);
    }
}

function renderServiceModal(modal, service) {
    modal.buildHTML(`
        <h3>${service[KEY_NAME]}</h3>
        <canvas id="${ID_CHECK_CHART}"></canvas>
        <table id="${ID_CHECK_TABLE}"></table>
    `);
    let checkSearchFunc = function(searchText) {
        let preSearch = JEQL.KEY_NAME + "='" + service[KEY_NAME] + "'";
        let search = JEQL.simpleSearchTransformer([KEY_ID, KEY_CHECK_AT, KEY_RESPONSE_TIME_MS, KEY_PASSED])(searchText);
        if (search !== '') {
            preSearch += " AND " + search;
        }
        return preSearch;
    };
    JEQL.pagedSearchingTable(document.getElementById(ID_CHECK_TABLE), refreshCheckTable, checkSearchFunc);

    let barData = [];
    let barColours = [];
    let checks = service[KEY_MOST_RECENT_CHECKS].slice().reverse();
    for (let i = 0; i < checks.length; i ++) {
        barData.push({
            y: checks[i][KEY_RESPONSE_TIME_MS],
            x: checks[i][KEY_CHECK_AT]
        });
        barColours.push(checks[i][KEY_PASSED] ? "green" : "red");
    }

    let chartConfig = {
        type: 'bar',
        plugins: [{
            afterDraw: chart => {
                const ctx = chart.ctx;
                ctx.save();
                const xAxis = chart.scales['x'];
                const yAxis = chart.scales['y'];
                const y = yAxis.getPixelForValue(service[KEY_ALERT_THRESHOLD_MS]);
                ctx.beginPath();
                ctx.setLineDash([10, 5]);
                ctx.moveTo(xAxis.left, y);
                ctx.lineTo(xAxis.right, y);
                ctx.lineWidth = 1;
                ctx.strokeStyle = 'blue';
                ctx.stroke();
                ctx.restore();
            }
        }],
        data: {
            datasets: [{
                label: "Response Time",
                data: barData,
                backgroundColor: barColours
            }],
        },
        options: {
            scales: {
                x: {
                    min: '2021-11-07 00:00:00',
                }
            },
            onClick: function(evt) { handleChartClick(checks, evt); },
            onHover: (event, chartElement) => {
                event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
            }
        }
    };

    window.check_chart = new Chart(document.getElementById(ID_CHECK_CHART).getContext("2d"), chartConfig);
}

function renderManagedServices(data) {
    let table = JEQL.elemBuilder("table").buildHTML(`
        <tr>
            <th>Name</th>
            <th>Check Every (ms)</th>
            <th>URL</th>
            <th>Alert Threshold (ms)</th>
            <th>Checks</th>
        </th>
    `).buildForeach(data, function(service, elem) {
        let checks = service[KEY_MOST_RECENT_CHECKS].slice(0, Math.min(service[KEY_MOST_RECENT_CHECKS].length, MAX_CHECKS_VISIBLE)).reverse();

        elem.buildChild("tr").buildHTML(`
            <td>${service[KEY_NAME]}</td>
            <td>${service[KEY_CHECK_EVERY_MS]}</td>
            <td>${service[KEY_URL]}</td>
            <td>${service[KEY_ALERT_THRESHOLD_MS]}</td>
        `).buildChild("td").buildForeach(checks, function(check, td) {
            td.buildChild("span")
                .buildAttr("style", "cursor: pointer; margin-left: 0.5em; background-color: " + (check[KEY_PASSED] ? "green" : "red"))
                .buildText(check[KEY_PASSED] ? "Y" : "N")
                .buildEventListener("click", function() { fetchAndRenderCheckModal(check[KEY_ID]); });
        }).buildChild("button").buildText("Select").buildEventListener("click", function() {
            JEQL.renderModal(function(modal) { renderServiceModal(modal, service); }, true, JEQL.CLS_MODAL_WIDE);
        });
    });
    document.getElementById(ID_SERVICES).appendChild(table);
}

function renderErrorModal(modal, error) {
    modal.buildHTML(`
        <h3>Details about Error</h3>
        Id: <span>${error[KEY_ID]}</span><br>
        Source File: <span>${error[KEY_SOURCE_FILE]}</span><br>
        Line Number: <span>${error[KEY_FILE_LINE_NUMBER]}</span><br>
        Error Condensed: <span>${error[KEY_ERROR_CONDENSED]}</span><br>
        Source System: <span>${error[KEY_SOURCE_SYSTEM]}</span><br>
        Version: <span>${error[KEY_VERSION]}</span><br>
        Occurred: <span>${error[KEY_CREATED]}</span><br>
        User Agent: <span>${error[KEY_USER_AGENT]}</span><br>
        Ip Address: <span>${error[KEY_IP_ADDRESS]}</span><br>
        Stack trace: <pre>${error[KEY_STACKTRACE]}</pre>
    `);
}

function fetchAndRenderErrorModal(id) {
    let data = {};
    data[KEY_ID] = id;
    JEQL.requests.makeBody(window.JEQL_CONFIG, ACTION_FETCH_ERROR, function(data) {
        JEQL.renderModal(function(modal) { renderErrorModal(modal, data); }, true, JEQL.CLS_MODAL_WIDE);
    }, data);
}

function errorTableRowRenderer(rowElem, data, idx, superRowRenderer) {
    superRowRenderer();
    let rowObj = JEQL.tupleToObject(data[JEQL.KEY_ROWS][idx], data[JEQL.KEY_COLUMNS]);

    rowElem.buildChild("td").buildChild("button").buildText("Select").buildEventListener("click", function() {
        fetchAndRenderErrorModal(rowObj[KEY_ID]);
    });
}

function refreshErrorTable(page, size, search, sort) {
    JEQL.requests.makeBody(window.JEQL_CONFIG,
        ACTION_FETCH_ERRORS,
        function(data) {
            let errorTable = document.getElementById(ID_ERROR_TABLE);
            JEQL.pagedTableUpdate(errorTable, data);
            JEQL.tableRenderer(JEQL.objectsToTuples(data[JEQL.KEY_DATA]), errorTable, errorTableRowRenderer);
        },
        JEQL.getSearchObj(page, size, search, sort)
    );
}

window.onload = function() {
    JEQL.init(APPLICATION_NAME, function(config) {
         JEQL.pagedSearchingTable(document.getElementById(ID_ERROR_TABLE), refreshErrorTable, JEQL.simpleSearchTransformer(
            [KEY_ID, KEY_SOURCE_FILE, KEY_ERROR_CONDENSED, KEY_FILE_LINE_NUMBER, KEY_VERSION, KEY_SOURCE_SYSTEM, KEY_CREATED]
         ));
         JEQL.requests.makeEmpty(config, ACTION_FETCH_MANAGED_SERVICES, renderManagedServices);
         if (JEQL.findGetParameter(PARAM_MANAGED_CHECK_ID)) {
            fetchAndRenderCheckModal(JEQL.findGetParameter(PARAM_MANAGED_CHECK_ID));
         } else if (JEQL.findGetParameter(PARAM_ERROR_ID)) {
            fetchAndRenderErrorModal(JEQL.findGetParameter(PARAM_ERROR_ID));
         }
    });
};