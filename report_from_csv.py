# -*- coding: utf-8 -*-
#!/usr/bin/env python
from random import randrange
import sys
import csv
from statistics import mean


table_columns = ["timestamp","question_sort","question_type","question_statement","value"]

def read_data(filename):
    with open(filename, 'r', encoding='utf-8') as respostes:
        respostes_reader = csv.reader(respostes)

        question_list = []
        questions = next(respostes_reader)
        for question in questions:
            question_list.append(question)
        legend_text, comment_caption = arrange_questions(question_list)

        total_responses = 0
        questions_scores = {}
        table_rows = []
        for row in respostes_reader:
            total_responses += 1
            i = 0
            while i <= len(legend_text):
                if i == 0:
                    timestamp = row[i]
                else:
                    if i not in questions_scores.keys():
                        questions_scores[i] = []
                    questions_scores[i].append(row[i])
                    record_to_table(table_rows, timestamp, i, 'Numeric', question_list[i-1], row[i])
                i += 1
            
            table_rows = record_to_table(table_rows, timestamp, i, 'Text', comment_caption, row[i])

    return legend_text, questions_scores, comment_caption, table_rows, total_responses


def arrange_questions(question_list):
    # timestamp = question_list[0]
    legend_text = question_list[1:len(question_list)-1]
    comment_caption = question_list[len(question_list)-1]

    return legend_text, comment_caption


def record_to_table(table_rows, timestamp, question_sort, question_type, question_statement, value):
    replace = "\\'"
    table_rows.append(f"""
                        '{table_columns[0]}': '{timestamp}',
                        '{table_columns[1]}': '{question_sort}',
                        '{table_columns[2]}': '{question_type}',
                        '{table_columns[3]}': '{question_statement.replace("'", replace)}',
                        '{table_columns[4]}': '{value.replace("'", replace)}',
                      """.replace('\n', ' ').replace('\r', ''))
    return table_rows


# For const totalData
def obtain_total_data(question_scores):
    total_data = {}
    i = 0
    for question in question_scores.keys():
        if i not in total_data.keys():
            total_data[i] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for score in question_scores[question]:

            total_data[i][int(score)-1] += 1
        i += 1

    return total_data


# For const globalData
def obtain_global_data(question_scores):
    global_data = []
    for question in questions_scores.keys():
        global_data.append(round(mean([int(j) for j in question_scores[question]]), 2))

    return global_data


def setup_data(legend_text, total_data, global_data):
    #fixed legend colors
    legend_colors = [
        "rgb(255, 99, 132, 0.25)",
        "rgb(75, 192, 192, 0.25)",
        "rgb(255, 205, 86, 0.25)",
        "rgb(54, 162, 235, 0.25)"    
    ]

    #more random colors only if needed
    extra_questions = len(legend_text) - len(legend_colors)
    if extra_questions > 0:
        for i in range(extra_questions):
            legend_colors.append(f"rgb({randrange(255)}, {randrange(255)}, {randrange(255)}, 0.25)")

    #legend summary
    legend_summary = []
    for i in range(len(legend_text)):
        legend_summary.append(f"Pregunta {i+1}")

    #legend html list items
    legend_list = []
    for i in range(len(legend_text)):
        legend_list.append(f"<div class='icon' style='background-color: {legend_colors[i]};'></div>{legend_text[i]}")

    #legend means
    legend_means = []
    for i in range(len(legend_text)):
        legend_means.append(f"<div class='icon' style='background-color: {legend_colors[i]};'></div>{'{:.2f}'.format(global_data[i])}")

    #total data graph
    total_graph = []
    for i in range(len(legend_text)):
        total_graph.append(f"""
            'label': 'Quantitat de valoracions en {legend_summary[i].lower()}',
            'data':  {total_data[i]},
            'backgroundColor': '{legend_colors[i]}',
            'borderColor': '{legend_colors[i]}'
        """)

    return legend_colors, legend_summary, legend_list, legend_means, total_graph


def generate_file(filename, group, legend_colors, legend_summary, legend_list, total_data, legend_means, total_graph, global_data, comment_caption, table_rows, total_responses):    
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard de {group}</title>

            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/jq-3.3.1/jszip-2.5.0/dt-1.10.24/b-1.7.0/b-colvis-1.7.0/b-html5-1.7.0/b-print-1.7.0/cr-1.5.3/kt-2.6.1/r-2.2.7/sp-1.2.2/datatables.min.css"/>

            <style>
                body{{
                    background-color: whitesmoke;
                    padding-bottom: 10px;
                }}

                body, 
                h1{{            
                    margin: 0px;
                    font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', Arial, sans-serif;
                }}

                header{{
                    background-color: #ad0050;
                    color: white;
                    padding: 10px;
                }}

                h1{{
                    padding: 0px;
                }}
            
                h2{{
                    font-weight: normal;
                }}

                .canvas, 
                .table{{
                    position: relative; 
                    width:100%;          
                }}

                .canvas{{
                    padding-bottom: 20px;
                    height:400px !important;
                }}

                .box{{            
                    width: calc(50% - 36px);
                    border: solid 1px grey;
                    box-shadow: 1px 1px 10px #888888;
                    border-radius: 5px;
                    margin: 10px 10px 0px 10px;
                    padding: 0px 10px 10px 10px;
                    background-color: white;
                }}

                .left{{
                    float: left;            
                    margin-right: 5px;
                }}

                .right{{
                    float: right;
                    margin-left: 5px;
                }}

                .full{{
                    width: calc(100% - 42px);
                    padding: 0px 10px 10px 10px;
                }}

                .clear{{
                    clear: both;
                }}

                .content{{
                    width: 100%;
                    display: flex;
                }}

                .box h3{{
                    margin-top: 10px;
                }}

                .box ol{{
                    padding-left: 20px;
                    margin-left: 40px;
                }}

                .box.questions li{{
                    cursor: pointer;
                }}

                .box.questions li:hover{{
                    color: darkgray;
                }}

                .box li.cross{{
                    text-decoration: line-through;
                }}

                .box li .icon{{
                    width: 28px;
                    height: 10px;
                    background-color: red;
                    position: relative;
                    display: inline-block;
                    margin-left: -60px;
                    margin-right: 35px;
                }} 

                .hide table,
                .hide #export_filter,
                .hide #export_info,
                .hide #export_paginate{{
                    display: none;
                }}

                .hide .dt-buttons{{
                    margin-left: 10px;
                }} 

                @media only screen and (max-width: 800px) {{
                    .content{{
                        display: inline;
                    }}

                    .left,
                    .right {{
                        float: none;
                        display: block;
                        margin:10px;
                        width: calc(100% - 42px);
                    }}
                }}                       
            </style>

            <script src="https://cdn.jsdelivr.net/npm/chart.js@3.2.1/dist/chart.min.js"></script>    
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/pdfmake.min.js"></script>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.36/vfs_fonts.js"></script>
            <script type="text/javascript" src="https://cdn.datatables.net/v/dt/jq-3.3.1/jszip-2.5.0/dt-1.10.24/af-2.3.6/b-1.7.0/b-colvis-1.7.0/b-html5-1.7.0/b-print-1.7.0/cr-1.5.3/kt-2.6.1/r-2.2.7/sp-1.2.2/datatables.min.js"></script>

            <script type="text/javascript">
                window.onload = function () {{
                    $.fn.dataTable.ext.search.push(
                        //This function hides the numeric answers in the comments table but allows exporting
                        function (settings, searchData, index, rowData, counter) {{
                            if(settings.sTableId == "export") return true;
                            else return !(rowData["question_type"] === 'Numeric' || rowData["value"] === '');                    
                    }});
                                            
                    const globalData = {{
                        labels:  [{(', '.join('"' + item + '"' for item in legend_summary))}],
                        datasets: [
                            {{
                                label: 'Valoració mitjana',
                                data:  [{(', '.join("'" + str(round(item, 2)) + "'" for item in global_data))}],
                                backgroundColor: [{(', '.join('"' + item + '"' for item in legend_colors))}],
                                borderColor: [{(', '.join('"' + item + '"' for item in legend_colors))}]
                            }}
                        ]
                    }};

                    const totalData = {{
                        labels:  [{(', '.join("'" + str(item) + (" punt" if item == 1 else " punts") + "'" for item in range(1, 11)))}],
                        datasets:  [{(', '.join('{' + item + '}' for item in total_graph))}]
                    }};

                    var fullData = [{(', '.join('{' + item + '}' for item in table_rows))}];
                
                    var globalChart = new Chart(document.getElementById('globalChart'), {{
                        type: 'bar',
                        data: globalData,                
                        options: {{                    
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                x:{{
                                    title: {{
                                        display: true,
                                        text: 'Pregunta'
                                    }}
                                }},
                                y:{{
                                    suggestedMin: 0,
                                    suggestedMax: 10,
                                    title: {{
                                        display: true,
                                        text: 'Mitjana de valoracions'
                                    }}
                                }}
                            }},
                            plugins: {{
                                legend: {{
                                    display: false
                                }}
                            }}
                        }},
                    }});

                    var totalChart = new Chart(document.getElementById('totalChart'), {{
                        type: 'bar',
                        data: totalData,                
                        options: {{                    
                            responsive: true,
                            maintainAspectRatio: false,
                            scales: {{
                                x:{{
                                    title: {{
                                        display: true,
                                        text: 'Puntuació'
                                    }}
                                }},
                                y:{{
                                    title: {{
                                        display: true,
                                        text: 'Quantitat de valoracions'
                                    }}
                                }}
                            }},
                            plugins: {{
                                legend: {{
                                    //position: 'right'
                                    display: false
                                }}
                            }}
                        }},
                    }});

                    $('#comments').DataTable({{
                        data: fullData,
                        columns: [{{data: "value"}}]
                    }});

                    $('#export').DataTable({{
                        data: fullData,
                        columns: [{(', '.join('{data: "' + item + '"}' for item in table_columns))}],                   
                        dom: 'Bfrtip',
                        buttons: ['copy', 'excel'/*, 'pdf'*/]            
                    }});
                    
                    var legendItems = document.querySelector('#legend').getElementsByTagName('li');

                    for (var i = 0; i < legendItems.length; i++) {{
                        legendItems[i].addEventListener("click", legendClickCallback.bind(this,i), false);
                    }}

                    function legendClickCallback(legendItemIndex){{
                        var legendItem = document.querySelector('#legend').getElementsByTagName('li')[legendItemIndex];
                        legendItem.classList.toggle("cross");

                        var meanItem = document.querySelector('#means').getElementsByTagName('li')[legendItemIndex];
                        meanItem.classList.toggle("cross");

                        document.querySelectorAll('canvas').forEach((chartItem,index)=>{{
                            var chart = Chart.instances[index];
                            if(chart.canvas.id == "globalChart") chart.toggleDataVisibility(legendItemIndex);
                            else  chart.data.datasets[legendItemIndex].hidden = !(chart.data.datasets[legendItemIndex].hidden ?? false);                    
                            chart.update();                    
                        }});
                    }};
                }};         
            </script>
        <head>
        
        <body>
            <header>
                <h1>Enquesta de satisfacció del personal del centre</h1>
                <h2>{group}</h2>
            </header>

            <div class="box questions full">
                <h3>Preguntes</h3>
                <ol id="legend">
                    {(''.join('<li>' + item + '</li>' for item in legend_list))}
                </ol>
            </div>
            
            <div class="content">
                <div class="box left">
                    <h3>Mitjanes totals</h3>
                    <ol id="means">
                        {(''.join('<li>' + mean + '</li>' for mean in legend_means))}                
                    </ol>
                </div>
                <div class="box right">
                    <h3>Nombre de respostes</h3>
                    <h1 style="text-align:center;">{total_responses}</h1>           
                </div>
            </div>

            <div class="content">
                <div class="box left">
                    <h3>Gràfica de mitjanes totals</h3>
                    <div class="canvas">
                        <canvas id="globalChart"></canvas>
                    </div>
                </div>

                <div class="box right">
                    <h3>Distribució de puntuacions per pregunta</h3>
                    <div class="canvas">
                        <canvas id="totalChart"></canvas>
                    </div>
                </div>

            </div>

            <div class="clear"></div>
        
            <div class="box full">
                <h3>Comentaris</h3>
                <div class="table">
                    <table id="comments" style="width:100%">   <!-- inline needed to allow responsive behaviour -->
                        <thead>
                            <tr>              
                                <th>{comment_caption}</th>                    
                            </tr>                    
                        </thead>            
                    </table>
                </div>
            </div>  
            
            <div class="box hide full">
                <h3>Exportació de dades </h3>
                <table id="export">
                    <thead>
                        <tr>              
                            {(''.join('<th>' + item + '</th>' for item in table_columns))}
                        </tr>                    
                    </thead>            
                </table>
            </div>
            
        </body>
        
    </html>
    """

    original_stdout = sys.stdout

    filename = f"{filename.split('.')[0]}.html"

    with open(filename, "w", encoding="utf-8") as f:
        sys.stdout = f
        print(template)
        sys.stdout = original_stdout


if __name__ == "__main__":
    filename = sys.argv[1]
    group = sys.argv[2]

    legend_text, questions_scores, comment_caption, table_rows, total_responses = read_data(filename)
    total_data = obtain_total_data(questions_scores)
    global_data = obtain_global_data(questions_scores)
    legend_colors, legend_summary, legend_list, legend_means, total_graph = setup_data(legend_text, total_data, global_data)
    generate_file(filename, group, legend_colors, legend_summary,
                  legend_list, total_data, legend_means, total_graph,
                  global_data, comment_caption, table_rows, total_responses)
