# -*- coding: utf-8 -*-
#!/usr/bin/env python
from random import randrange
import psycopg2
import sys

course_code = ""
mp_code = ""
mp_name = ""
comment_caption = ""

table_columns = ["evaluation_id","timestamp","year","level","department","degree","group","subject_code","subject_name","trainer","topic","question_sort","question_type","question_statement","value"]
global_data = []
legend_text = []
total_data = []
table_rows = []
legend_colors = []
legend_summary = []
legend_list = []
total_graph = []

def load_data(subject_id):
    global course_code, mp_code, mp_name, global_data, legend_text, total_data, table_rows, comment_caption, table_columns
    
    conn = psycopg2.connect(user="postgres", password="postgres", host="127.0.0.1", port="5432", database="enquestes-real")
    cursor = conn.cursor()

    #LOADING MAIN COURSE DATA    
    query = f"""
                SELECT sub.code AS subject_code, sub.name AS subject_name, deg.code AS degree_code, deg.name AS degree_name 
                FROM master.subject sub
	                LEFT JOIN master.degree deg ON deg.id = sub.degree_id
	            WHERE sub.id= {subject_id}
            """

    cursor.execute(query)
    data = cursor.fetchone()

    course_code = data[2]
    mp_code = data[0]
    mp_name = data[1]

    #LOADING GLOBAL SCORING DATA (score average per question)
    query = f"""
            SELECT question_statement, SUM(CAST(value AS INTEGER))/COUNT(question_statement) AS "value", question_sort FROM reports.answer
            WHERE degree='{course_code}' AND subject_code='{mp_code}' AND question_type='Numeric'
            GROUP BY question_statement, question_sort
            ORDER BY question_sort
        """

    cursor.execute(query)
    data = cursor.fetchall()    
    
    legend_text = []
    global_data = []

    for row in data:
        legend_text.append(row[0])
        global_data.append(row[1])                

    query = f"SELECT DISTINCT question_statement FROM reports.answer WHERE degree='{course_code}' AND subject_code='{mp_code}' AND question_type='Text'"
    cursor.execute(query)
    comment_caption = cursor.fetchone()[0]

    #LOADING TOTAL DATA (amount of scores per question)
    total_data = []
    question_sort = 1
    question_scores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    query = f"""
            SELECT question_sort, COUNT("value") AS count, "value"::integer FROM reports.answer
            WHERE degree='{course_code}' AND subject_code='{mp_code}' AND question_type='Numeric'
            GROUP BY question_sort, "value"
            ORDER BY question_sort, "value"
        """

    cursor.execute(query)
    data = cursor.fetchall()
    for row in data:
        if row[0] != question_sort:
            total_data.append(f"[{', '.join([str(x) for x in question_scores])}]")
            question_sort = row[0]
            question_scores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        question_scores[row[2]-1] = row[1]

    total_data.append(question_scores)   
    
    #LOADING ANSWER DETAILS (datatable display)
    #WARNING: place \\ before any single quote for row values and set '' for NULL
    query = f"""
            SELECT evaluation_id, timestamp, year, level, department, degree, "group", subject_code, subject_name, trainer, topic, question_sort, question_type, question_statement, 
                CASE 
		            WHEN TRIM("value") = '' THEN ''
		        ELSE TRIM("value")
	            END
            FROM reports.answer
            WHERE degree='{course_code}' AND subject_code='{mp_code}'
            ORDER BY degree, subject_code, question_sort
        """

    cursor.execute(query)
    data = cursor.fetchall()
    replace = "\\'"
    for row in data:           
        table_rows.append(f"""
            '{table_columns[0]}': '{row[0]}',
            '{table_columns[1]}': '{row[1]}',
            '{table_columns[2]}': '{row[2]}',
            '{table_columns[3]}': '{row[3].replace("'", replace)}',
            '{table_columns[4]}': '{row[4].replace("'", replace)}',
            '{table_columns[5]}': '{row[5].replace("'", replace)}',
            '{table_columns[6]}': '{row[6].replace("'", replace)}',
            '{table_columns[7]}': '{row[7].replace("'", replace)}',
            '{table_columns[8]}': '{row[8].replace("'", replace)}',
            '{table_columns[9]}': '{row[9]}',
            '{table_columns[10]}': '{row[10]}',
            '{table_columns[11]}': '{row[11]}',
            '{table_columns[12]}': '{row[12]}',
            '{table_columns[13]}': '{row[13].replace("'", replace)}',
            '{table_columns[14]}': '{row[14].replace("'", replace)}',
        """.replace("'None'", "''").replace('\r', '').replace('\n', ''))

def setup_data():
    global table_columns, legend_colors, legend_summary, legend_list, total_graph
    
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

    #total data graph
    total_graph = []
    for i in range(len(total_data)):
        total_graph.append(f"""
            'label': '{legend_summary[i]}',
            'data':  {total_data[i]},
            'backgroundColor': '{legend_colors[i]}',
            'borderColor': '{legend_colors[i]}'
        """)

def generate_file():    
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard for {mp_code}</title>

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

                .box li{{
                    cursor: pointer;
                }}

                .box li:hover{{
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
                                data:  [{(', '.join("'" + str(item) + "'" for item in global_data))}],
                                backgroundColor: [{(', '.join('"' + item + '"' for item in legend_colors))}]
                            }}
                        ]
                    }};

                    const totalData = {{
                        labels:  [{(', '.join("'" + str(item) + "'" for item in range(10)))}],
                        datasets:  [{(', '.join('{' + item + '}' for item in total_graph))}]
                    }};

                    var fullData = [{(', '.join('{' + item + '}' for item in table_rows))}];
                
                    var globalChart = new Chart(document.getElementById('globalChart'), {{
                        type: 'polarArea',
                        data: globalData,                
                        options: {{                    
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{
                                    //position: 'left'
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
                        buttons: ['copy', 'excel', 'pdf']            
                    }});
                    
                    var legendItems = document.querySelector('#legend').getElementsByTagName('li');

                    for (var i = 0; i < legendItems.length; i++) {{
                        legendItems[i].addEventListener("click", legendClickCallback.bind(this,i), false);
                    }}

                    function legendClickCallback(legendItemIndex){{
                        var legendItem = document.querySelector('#legend').getElementsByTagName('li')[legendItemIndex];
                        legendItem.classList.toggle("cross");

                        document.querySelectorAll('canvas').forEach((chartItem,index)=>{{
                            var chart = Chart.instances[index];
                            if(chart.config.type == "polarArea") chart.toggleDataVisibility(legendItemIndex);
                            else  chart.data.datasets[legendItemIndex].hidden = !(chart.data.datasets[legendItemIndex].hidden ?? false);                    
                            chart.update();                    
                        }});  
                    }}
                }};         
            </script>
        <head>
        
        <body>
            <header>
                <h1>{course_code}</h1>
                <h2>{mp_code}: {mp_name}</h2>
            </header>

            <div class="box full">
                <h3>Preguntes</h3>
                <ol id="legend">
                    {(''.join('<li>' + item + '</li>' for item in legend_list))}                
                </ol>
            </div>

            <div class="content">    
                <div class="box left">
                    <h3>Valoracions totals</h3>
                    <div class="canvas">
                        <canvas id="totalChart"></canvas>
                    </div>
                </div>

                <div class="box right">
                    <h3>Valoracions globals</h3>
                    <div class="canvas">
                        <canvas id="globalChart"></canvas>
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

    with open(f"dashboard_{mp_code}.html", "w", encoding="utf-8") as f:
        sys.stdout = f
        print(template)
        sys.stdout = original_stdout

#loading bbdd data
load_data(31) #DAM MP04

#setting up extra data
setup_data()

#creating the HTML file
generate_file()