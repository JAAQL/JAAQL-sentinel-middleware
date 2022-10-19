let APPLICATION_NAME = "sentinel";
let TENANT_NAME = "jaaql";
let CONFIGURATION_NAME = "live";

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


/****************************************************************************************************************************************************/
/*
* DEPRECATED FUNCTIONS TAKEN FROM OLD JEQL
 */

let ID_PAGING_REFRESH_BUTTON = "refresh";
let ID_PAGING_FILTERED = "filtered";
let ID_PAGING_TOTAL = "total";
let ID_PAGING_PAGES = "pages";
let ID_PAGING_SIZE = "size";
let ID_PAGING_FROM = "from";
let ID_PAGING_TO = "to";
let ID_PAGING_CUR_PAGE = "cur";
let ID_PAGING_SORT = "sort";
let ID_PAGING_SEARCH = "search";
let ID_PAGING_LAST_SEARCH = "last-search";

let KEY_RECORDS_TOTAL = "records_total";
let KEY_RECORDS_FILTERED = "records_filtered";
let KEY_SEARCH = "search";
let KEY_DATA = "data";
let KEY_SORT = "sort";
let KEY_SIZE = "size";
let KEY_PAGE = "page";

let SORT_DEFAULT = "&nbsp;-";
let SORT_ASC = "&nbsp;&#9650;";
let SORT_DESC = "&nbsp;&#9660;";

let ATTR_JEQL_PAGING_TABLE = "jeql-paging-table";
let ATTR_JEQL_SORT_DIRECTION = "jeql-sort-direction";

let CLS_JEQL_TABLE_HEADER = "jeql-table-header";
let CLS_JEQL_TABLE_HEADER_SORT = "jeql-table-header-sort";
let CLS_JEQL_TABLE_HEADER_SORT_SPAN = "jeql-table-header-sort-span";

function getPagedSearchingTableRefreshButton(tableId) {
    return document.getElementById(tableId + "-" + ID_PAGING_REFRESH_BUTTON);
}

function setPagedSearchingTableSortField(tableId, sort) {
    document.getElementById(tableId + "-" + ID_PAGING_SORT).innerText = sort;
}

function formatAsTableHeader(inStr) {
    let formatted = "";
    let lastChar = "_";
    for (let i = 0; i < inStr.length; i ++) {
        let char = inStr[i];
        formatted += lastChar === "_" ? char.toUpperCase() : char;
        lastChar = char;
    }
    return formatted.replace("_", " ");
}

function simpleSearchTransformer(cols) {
    return function(search) {
        if (search === "") { return search; }
        let simplified = "";
        for (let i = 0; i < cols.length; i ++) {
            if (i !== 0) { simplified += " OR "; }
            simplified += cols[i] + " LIKE '%" + search + "%'"
        }
        return simplified;
    }
}

function pagedTableUpdate(table, data) {
    let tableId = table.id;
    let refreshId = tableId + "-" + ID_PAGING_REFRESH_BUTTON;
    let totalId = tableId + "-" + ID_PAGING_TOTAL;
    let filteredId = tableId + "-" + ID_PAGING_FILTERED;
    let fromId = tableId + "-" + ID_PAGING_FROM;
    let toId = tableId + "-" + ID_PAGING_TO;
    let curPageElem = document.getElementById(tableId + "-" + ID_PAGING_CUR_PAGE);
    let curPage = parseInt(curPageElem.innerText);
    let pagesElem = document.getElementById(tableId + "-" + ID_PAGING_PAGES);
    let pageSize = parseInt(document.getElementById(tableId + "-" + ID_PAGING_SIZE).value);
    let numPages = Math.ceil(data[KEY_RECORDS_FILTERED] / pageSize);
    let pageButtonClickFunc = function(event) {
        curPageElem.innerText = event.target.innerHTML;
        document.getElementById(refreshId).click();
    };

    pagesElem.innerHTML = "";
    pagesElem.appendChild(JEQL.elemBuilder("button").buildText("1").buildBoolean("disabled",
        curPage === 1).buildEventListener("click", pageButtonClickFunc));
    if (curPage > 3) {
        if (numPages < 8 || curPage === 4) {
            pagesElem.appendChild(JEQL.elemBuilder("button").buildText("2").buildBoolean("disabled",
                curPage === 2).buildEventListener("click", pageButtonClickFunc));
        } else {
            pagesElem.appendChild(JEQL.elemBuilder("button").buildText("...").buildBoolean("disabled", true));
        }
    }
    if (numPages > 6 && numPages === curPage) {
        let curNum = curPage - 4;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 5 && numPages - curPage < 2 && curPage > 5) {
        let curNum = curPage - 3;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 4 && numPages - curPage < 3 && curPage > 4) {
        let curNum = curPage - 2;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 1 && curPage - 1 !== numPages) {
        let curNum = curPage > 2 ? curPage - 1 : 2;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 2 && curPage !== numPages) {
        let curNum = curPage > 3 ? curPage : 3;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 3 && curPage < numPages && (numPages !== curPage + 1 || numPages === 4)) {
        let curNum = curPage > 3 ? curPage + 1 : 4;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages > 6 && curPage < 4) {
        let curNum = 5;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }
    if (numPages - curPage > 2 && numPages > 5) {
        if (numPages < 8 || numPages - curPage < 4) {
            let curNum = numPages - 1;
            pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
                curPage === curNum).buildEventListener("click", pageButtonClickFunc));
        } else {
            pagesElem.appendChild(JEQL.elemBuilder("button").buildText("...").buildBoolean("disabled", true));
        }
    }
    if (numPages > 4 || (numPages === curPage && (curPage === 3 || curPage === 4))) {
        let curNum = numPages;
        pagesElem.appendChild(JEQL.elemBuilder("button").buildText(curNum.toString()).buildBoolean("disabled",
            curPage === curNum).buildEventListener("click", pageButtonClickFunc));
    }

    document.getElementById(totalId).innerText = data[KEY_RECORDS_TOTAL];
    document.getElementById(filteredId).innerText = data[KEY_RECORDS_FILTERED];
    if (data[KEY_RECORDS_FILTERED] === 0) {
        document.getElementById(fromId).innerText = "0";
    } else {
        document.getElementById(fromId).innerText = (curPage * pageSize - pageSize + 1).toString();
    }
    document.getElementById(toId).innerText = Math.min((curPage * pageSize), data[KEY_RECORDS_FILTERED]).toString();
}

function tableRenderer(data, table, rowRenderer, skipColumns) {
    if (!skipColumns) {
        skipColumns = [];
    }

    let oldSortCol = null;
    let oldSortDir = null;

    if (!table) {
        table = JEQL.elemBuilder(table);
        document.body.appendChild(table);
    } else {
        let oldHeaders = table.getElementsByClassName(CLS_JEQL_TABLE_HEADER_SORT);
        for (let i = 0; i < oldHeaders.length; i ++) {
            let span = oldHeaders[i].getElementsByClassName(CLS_JEQL_TABLE_HEADER_SORT_SPAN)[0];
            if (span.getAttribute(ATTR_JEQL_SORT_DIRECTION) !== SORT_DEFAULT) {
                oldSortCol = oldHeaders[i].childNodes[0].data;
                oldSortDir = span.getAttribute(ATTR_JEQL_SORT_DIRECTION);
            }
        }
        table.innerHTML = "";
        JEQL.makeBuildable(table);
    }
    let isPagingTable = table.getAttribute(ATTR_JEQL_PAGING_TABLE);
    let header = table.buildChild("tr");
    for (let idx in Object.keys(data[JEQL.KEY_COLUMNS])) {
        if (skipColumns.includes(data[JEQL.KEY_COLUMNS][idx])) {
            continue;
        }
        let headerText = formatAsTableHeader(data[JEQL.KEY_COLUMNS][idx]);
        let th = header.buildChild("th").buildClass(CLS_JEQL_TABLE_HEADER).buildText(headerText);
        if (isPagingTable) {
            th.buildClass(CLS_JEQL_TABLE_HEADER_SORT);
            let span = th.buildChild("span").buildClass(CLS_JEQL_TABLE_HEADER_SORT_SPAN).buildHTML(
                SORT_DEFAULT).buildAttr(ATTR_JEQL_SORT_DIRECTION, SORT_DEFAULT);
            if (headerText === oldSortCol) {
                span.buildAttr(ATTR_JEQL_SORT_DIRECTION, oldSortDir);
                span.innerHTML = oldSortDir;
            }
            th.buildEventListener().buildEventListener("click", function() {
                if (span.getAttribute(ATTR_JEQL_SORT_DIRECTION) === SORT_DEFAULT) {
                    span.innerHTML = SORT_ASC;
                    span.setAttribute(ATTR_JEQL_SORT_DIRECTION, SORT_ASC);
                    let sorts = table.getElementsByClassName(CLS_JEQL_TABLE_HEADER_SORT_SPAN);
                    for (let i = 0; i < sorts.length; i ++) {
                        if (sorts[i] !== span) {
                            sorts[i].setAttribute(ATTR_JEQL_SORT_DIRECTION, SORT_DEFAULT);
                            sorts[i].innerHTML = SORT_DEFAULT;
                        }
                    }
                    setPagedSearchingTableSortField(table.id, data[JEQL.KEY_COLUMNS][idx] + " ASC");
                } else if (span.getAttribute(ATTR_JEQL_SORT_DIRECTION) === SORT_ASC) {
                    span.innerHTML = SORT_DESC;
                    span.setAttribute(ATTR_JEQL_SORT_DIRECTION, SORT_DESC);
                    setPagedSearchingTableSortField(table.id, data[JEQL.KEY_COLUMNS][idx] + " DESC");
                } else /*if (span.getAttribute(ATTR_JEQL_SORT_DIRECTION) === SORT_DESC)*/ {
                    span.innerHTML = SORT_DEFAULT;
                    span.setAttribute(ATTR_JEQL_SORT_DIRECTION, SORT_DEFAULT);
                    setPagedSearchingTableSortField(table.id, "");
                }
                getPagedSearchingTableRefreshButton(table.id).click();
            });
        }
    }
    header.buildChild("th");
    for (let idx in data[JEQL.KEY_ROWS]) {
        let row = table.buildChild("tr");
        let defaultRowRenderer = function () {
            let iter = -1;
            for (let key in data[JEQL.KEY_ROWS][idx]) {
                iter += 1;
                if (skipColumns.includes(data[JEQL.KEY_COLUMNS][iter])) {
                    continue;
                }
                row.buildChild("td").buildText(data[JEQL.KEY_ROWS][idx][key]);
            }
        };
        if (rowRenderer) {
            rowRenderer(row, data, idx, defaultRowRenderer);
        } else {
            defaultRowRenderer();
        }
    }
}

function pagedSearchingTable(table, onChange, searchTransformer = null) {
    if (!searchTransformer) {
        searchTransformer = function(ret) { return ret; }
    }
    JEQL.makeBuildable(table);
    table.buildBoolean(ATTR_JEQL_PAGING_TABLE, true);
    let tableId = table.id;
    let refreshId = tableId + "-" + ID_PAGING_REFRESH_BUTTON;
    let totalId = tableId + "-" + ID_PAGING_TOTAL;
    let filteredId = tableId + "-" + ID_PAGING_FILTERED;
    let pagesId = tableId + "-" + ID_PAGING_PAGES;
    let sizeId = tableId + "-" + ID_PAGING_SIZE;
    let fromId = tableId + "-" + ID_PAGING_FROM;
    let searchId = tableId + "-" + ID_PAGING_SEARCH;
    let lastSearchId = tableId + "-" + ID_PAGING_LAST_SEARCH;
    let toId = tableId + "-" + ID_PAGING_TO;
    let curPageId = tableId + "-" + ID_PAGING_CUR_PAGE;
    let sortId = tableId + "-" + ID_PAGING_SORT;
    table.buildOlderSibling("div").buildHTML(`
        <label>
            Search: 
            <input type="text" id="${searchId}"/>
        </label>
        <label>
            Page Size:
            <select id="${sizeId}">
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
                <option value="250">250</option>
                <option value="999999999">All</option>
            </select>
        </label>
        <button id="${refreshId}">Search</button>
        <span id="${curPageId}" style="display:none">1</span>
        <span id="${sortId}" style="display:none"></span>
        <span id="${lastSearchId}" style="display:none"></span>
    `);
    table.buildSibling("div").buildHTML(`
        <div id="${pagesId}"></div><div>Showing <span id="${fromId}"></span> to <span id="${toId}"></span> of <span id="${filteredId}"></span>/<span id="${totalId}"> records</span></div>
    `);
    JEQL.makeBuildable(document.getElementById(pagesId));
    document.getElementById(sizeId).addEventListener("change", function() {
        document.getElementById(curPageId).innerText = "1";
        onChange(0, parseInt(document.getElementById(sizeId).value),
            searchTransformer(document.getElementById(searchId).value), document.getElementById(sortId).innerText);
    });
    document.getElementById(refreshId).addEventListener("click", function() {
        if (document.getElementById(lastSearchId).innerHTML !== document.getElementById(searchId).value) {
            document.getElementById(curPageId).innerText = "1";
        }
        document.getElementById(lastSearchId).value = document.getElementById(searchId).value;
        onChange(parseInt(document.getElementById(curPageId).innerText) - 1,
            parseInt(document.getElementById(sizeId).value), searchTransformer(document.getElementById(searchId).value),
            document.getElementById(sortId).innerText);
    });
    onChange(0, 10, searchTransformer(document.getElementById(searchId).value), "");
}

function getSearchObj(page, size, search, sort) {
    let obj = {};
    obj[KEY_PAGE] = page;
    obj[KEY_SIZE] = size;
    obj[KEY_SEARCH] = search;
    obj[KEY_SORT] = sort;
    return obj;
}

/*
* END DEPRECATED FUNCTIONS TAKEN FROM OLD JEQL
 */
/****************************************************************************************************************************************************/


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
    JEQL_REQUESTS.makeBody(window.JEQL__REQUEST_HELPER, ACTION_FETCH_CHECK, function(data) {
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
   JEQL_REQUESTS.makeBody(window.JEQL__REQUEST_HELPER,
        ACTION_FETCH_CHECKS,
        function(data) {
            let checkTable = document.getElementById(ID_CHECK_TABLE);
            pagedTableUpdate(checkTable, data);
            tableRenderer(JEQL.objectsToTuples(data[KEY_DATA]), checkTable, checkTableRowRenderer, [KEY_NAME]);
        },
        getSearchObj(page, size, search, sort)
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
        let search = simpleSearchTransformer([KEY_ID, KEY_CHECK_AT, KEY_RESPONSE_TIME_MS, KEY_PASSED])(searchText);
        if (search !== '') {
            preSearch += " AND " + search;
        }
        return preSearch;
    };
    pagedSearchingTable(document.getElementById(ID_CHECK_TABLE), refreshCheckTable, checkSearchFunc);

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
    JEQL_REQUESTS.makeBody(window.JEQL__REQUEST_HELPER, ACTION_FETCH_ERROR, function(data) {
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
    JEQL_REQUESTS.makeBody(window.JEQL__REQUEST_HELPER,
        ACTION_FETCH_ERRORS,
        function(data) {
            let errorTable = document.getElementById(ID_ERROR_TABLE);
            pagedTableUpdate(errorTable, data);
            tableRenderer(JEQL.objectsToTuples(data[KEY_DATA]), errorTable, errorTableRowRenderer);
        },
        getSearchObj(page, size, search, sort)
    );
}

window.onload = function() {
    JEQL.init(APPLICATION_NAME, TENANT_NAME, CONFIGURATION_NAME, function(config) {
         pagedSearchingTable(document.getElementById(ID_ERROR_TABLE), refreshErrorTable, simpleSearchTransformer(
            [KEY_ID, KEY_SOURCE_FILE, KEY_ERROR_CONDENSED, KEY_FILE_LINE_NUMBER, KEY_VERSION, KEY_SOURCE_SYSTEM, KEY_CREATED]
         ));
         JEQL_REQUESTS.makeEmpty(config, ACTION_FETCH_MANAGED_SERVICES, renderManagedServices);
         if (JEQL.findGetParameter(PARAM_MANAGED_CHECK_ID)) {
            fetchAndRenderCheckModal(JEQL.findGetParameter(PARAM_MANAGED_CHECK_ID));
         } else if (JEQL.findGetParameter(PARAM_ERROR_ID)) {
            fetchAndRenderErrorModal(JEQL.findGetParameter(PARAM_ERROR_ID));
         }
    });
};