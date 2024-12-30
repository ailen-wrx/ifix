//@ts-check

// This script will be run within the webview itself
// It cannot access the main VS Code APIs directly.
(function () {
    const vscode = acquireVsCodeApi();

    const oldState = vscode.getState() || { tableContents: [] };

    let tableContents = oldState.tableContents;
    updateTableList(tableContents);

    // Handle messages sent from the extension to the webview
    window.addEventListener('message', event => {
        const message = event.data; // The json data that the extension sent
        switch (message.type) {
            case 'initTables':
                {
                    tableContents = message.data;
                    updateTableList(tableContents);
                    break;
                }

        }
    });

    function changeTableCollapseState(index) {
        tableContents = vscode.getState().tableContents;
        tableContents[index].collapse = !tableContents[index].collapse;
        updateTableList(tableContents);
        vscode.setState({ tableContents: tableContents });
    }

    function changeVariableCollapseState(idx, var_idx, linestoAdd) {
        tableContents = vscode.getState().tableContents;
        var variable = tableContents[idx].variables[var_idx];
        if (variable.expand !== 0) {
            if (linestoAdd === 0) {
                variable.expand = 0;
            } else {
                variable.expand += linestoAdd;
                if (variable.expand < 0) {
                    variable.expand = 0;
                }
            }
        } else {
            variable.expand = 10;
        }
        updateTableList(tableContents);
        vscode.setState({ tableContents: tableContents });
    }


    function updateTableList(tableContents) {
        const ul = document.querySelector('.table-list');
        ul.textContent = '';
        tableContents.forEach(function(tableContent, idx) {

            const tb = document.createElement('table');
            tb.rules = 'all';

            const trHead = document.createElement('tr');
            const td = document.createElement('td');
            td.className = 'rowbutton';
            td.colSpan = tableContent.lines.length + 2;
            
            const expandButton = document.createElement('button');
            var collapseState = '';
            if (tableContent.collapse) {
                collapseState = '⏵   ';
            } else {
                collapseState = '⏷   ';
            }
            expandButton.textContent = collapseState + tableContent.title;
            expandButton.addEventListener('click', () => {
                changeTableCollapseState(idx);
            });
            td.appendChild(expandButton);
            trHead.appendChild(td);
            tb.appendChild(trHead);
            
            if (!tableContent.collapse) {
                const tr = document.createElement('tr');
                const tdLine = document.createElement('td');
                tdLine.className = 'headcol_number_bold';
                tdLine.textContent = "Line#Iter";
                tr.appendChild(tdLine); 
                const th = document.createElement('td');
                const adjustableDiv = document.createElement('div');
                adjustableDiv.className = 'adjustableDiv';
                adjustableDiv.textContent = 'Runtime Value';
                th.appendChild(adjustableDiv);
                th.className = 'adjustableDivCell';
                tr.appendChild(th);
                tableContent.lines.forEach(line => {
                    const th = document.createElement('th');
                    th.textContent = line;
                    tr.appendChild(th);
                });
                tb.appendChild(tr);

                tableContent.variables.forEach(function(variable, var_idx) {
                    const tr = document.createElement('tr');

                    const tdLine = document.createElement('td');
                    tdLine.className = 'headcol_number';
                    if (variable.position.iter <= 1) {
                        tdLine.textContent = variable.position.line.toString(); 
                    } else {
                        tdLine.textContent = variable.position.line.toString() + "#" + variable.position.iter.toString();
                    }
                    tr.appendChild(tdLine); 

                    const td = document.createElement('td');
                    if (variable.name.startsWith('##')) {
                        td.className = 'headcol_italic';
                        td.textContent = variable.name.replace("##", "");
                    } else {
                        td.className = 'headcol_bold';
                        td.textContent = variable.name;
                    }
                    td.addEventListener('click', () => {
                        vscode.postMessage({
                            command: 'jumpto',
                            url: variable.position.url,
                            line: variable.position.line
                        });
                    });
                    tr.appendChild(td); 
                    variable.values.forEach(function(value, i) {
                        if (variable.identical) {
                            const td = document.createElement('td');
                            td.className ='grid_color_' + value.color;
                            td.colSpan = value.merged_columns;
                            td.textContent = value.val;
                            if (variable.is_serialized) {
                                td.className ='grid_color_' + value.color + '_hplink';
                                td.addEventListener('dblclick', () => {
                                    changeVariableCollapseState(idx, var_idx, 0);
                                });
                            }
                            tr.appendChild(td);
                        } else {
                            const td = document.createElement('td');
                            td.colSpan = value.merged_columns;
                            td.textContent = value.val;
                            if (variable.is_serialized) {
                                td.className ='grid_hplink';
                                td.addEventListener('dblclick', () => {
                                    changeVariableCollapseState(idx, var_idx, 0);
                                });
                            }
                            tr.appendChild(td);
                        }
                    });
                    tb.appendChild(tr);
                    if (variable.is_serialized) {
                        if (variable.expand !== 0){
                            for (let i = 0; i < variable.expand; i++){
                                const tr = document.createElement('tr');
                                const tdLine = document.createElement('td');
                                tdLine.className = 'headcol_number_secondary';
                                tdLine.textContent = "‎";
                                tr.appendChild(tdLine); 
                                const td = document.createElement('td');
                                td.className = 'headcol_btn';
                                tr.appendChild(td); 
                                if (i === 0 && variable.expand > 10) {
                                    td.textContent = '-';
                                    td.addEventListener('click', () => {
                                        changeVariableCollapseState(idx, var_idx, -10);
                                    });
                                }
                                if (i === variable.expand - 1) {
                                    td.textContent = '+';
                                    td.addEventListener('click', () => {
                                        changeVariableCollapseState(idx, var_idx, 10);
                                    });
                                }
                                var breakSign = 1;
                                for (let j=0; j < variable.values.length; j++)
                                {
                                    var value = variable.values[j];
                                    const td = document.createElement('td');
                                    td.colSpan = value.merged_columns;
                                    if (i < value.serialized_val.split('\n').length - 2) {
                                        td.textContent = value.serialized_val.split('\n')[i+1];
                                        breakSign = 0;
                                    }
                                    td.className ='grid_color_hover';
                                    tr.appendChild(td);
                                }
                                tb.appendChild(tr);
                                if (breakSign) {
                                    break;
                                }
                            }
                        }
                    }
                });
            }
            ul.appendChild(tb);
        });
        vscode.setState({ tableContents: tableContents });
    }
}());


