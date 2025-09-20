class HTMLBuilder:
    @staticmethod
    def build_html(datasource_one: str, datasource_two: str):
        """Build Graph String with responsive 100% width and max 600px height"""
        return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Fund Performance Graphs</title>
                <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
                <style>
                body {{
                    margin: 0;
                    font-family: Arial, sans-serif;
                }}

                #page-container {{
                    max-width: 1280px;
                    max-height: 600px;
                    margin: 0 auto;
                    position: relative;
                }}

                #button-container {{
                    position: relative;
                    top: 90px;
                    width: 100%;
                    display: flexbox;
                    justify-content: flex-start;
                    gap: 10px;
                    padding: 10px;
                    box-sizing: border-box;
                    z-index: 1;
        }}

                #button-container button {{
                    padding: 8px 16px;
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                }}
                
                

                #button-container button:hover {{
                    background-color: #0056b3;
                }}

                #graph-wrapper {{
                    width: 100%;
                    box-sizing: border-box;
                    margin-top: 50px;
                }}

                #graph {{
                    width: 100% !important;
                    height: 600px;
                    max-height: 600px;
                }}

                @media (max-width: 700px) {{
                    #graph {{
                    height: 400px;
                    }}
                }}
                </style>
            </head>
            <body>
            <div id="page-container">
                <div id="button-container">
                <button onclick="loadGraph('regular')">Med udbytte</button>
                <button onclick="loadGraph('adjusted')">Totalafkast</button>
                </div>

                <div id="graph-wrapper">
                <div id="graph"></div>
                </div>
            </div>

            <script>
            const graphs = {{
                regular: {datasource_one},
                adjusted: {datasource_two}
            }};
            

            function resizeButtons() {{
                const width = window.innerWidth;
                let fontSize;

            if (width > 1000) {{
            fontSize = 18;
            }} else if (width > 700) {{
            fontSize = 14;
            }} else {{
            fontSize = 10;
            }}

                Plotly.relayout("graph", {{
                "updatemenus[0].font.size": fontSize,
                }});
                
                // Ensure buttons align with graph after resize
                alignButtonsWithGraph();
            }}

            function alignButtonsWithGraph() {{
                // Wait for Plotly to finish rendering
                setTimeout(() => {{
                const graphDiv = document.getElementById('graph');
                const buttonContainer = document.getElementById('button-container');
                
                if (graphDiv && buttonContainer) {{
                    // Get the actual plot area margins from Plotly
                    const fullLayout = graphDiv._fullLayout;
                    if (fullLayout && fullLayout.margin) {{
                    const leftMargin = fullLayout.margin.l || 80;
                    buttonContainer.style.paddingLeft = `${{leftMargin}}px`;
                    }}
                }}
                }}, 100);
            }}

            function loadGraph(view) {{
                window._lastView = view;
                const graphData = graphs[view];
                const layout = Object.assign({{}}, graphData.layout || {{}}, {{
                    autosize: true,
                    height: 600,
                    dragmode: false,
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    paper_bgcolor: 'rgba(0,0,0,0)'
                }});
                
                Plotly.newPlot(
                    'graph',
                    graphData.data,
                    layout,
                    {{
                        responsive: true,
                        displayModeBar: false, // hide toolbar
                        scrollZoom: false,     // disable wheel zoom
                        doubleClick: false     // prevent double-click zoom/reset
                    }}
                ).then(() => {{
                    resizeButtons();
                    alignButtonsWithGraph();
                }});
            }}

            // Event listeners
            window.addEventListener("resize", resizeButtons);
            loadGraph('adjusted');

            </script>
            </body>
            </html>
            """

    @staticmethod
    def create_box_html() -> str:
        return f"""
    <!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Document</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
        }}
      .rectangle {{
            width: 600px;
            height: 75px;
            border: 1px solid #F4F4F4;
            background-color: #F4F4F4;
            border-radius: 10px;
            display: flex;
            align-items: center;
            padding: 15px;
            box-sizing: border-box;
            justify-content: space-between;
        }}
      .group {{
        display: flex;
        align-items: center;
        gap: 10px;
      }}
      .left_info {{
        display: flex;
        flex-direction: column;
      }}
      .right_info {{
        display: flex;
        flex-direction: column;
        text-align: right;
      }}
      .percentage {{
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        color: #333;
      }}
      .image {{
        width: 40px !important;
        opacity: 70%;
      }}
      .amount {{
        font-size: 18px;
        font-weight: bold;
        margin: 0;
        color: #333;
      }}
      .date-info {{
        font-size: 12px;
        margin: 2px 0 0 0;
        color: #666;
      }}
      .return-info {{
        font-size: 12px;
        margin: 2px 0 0 0;
      }}

/* Tooltip container */
      .tooltip {{
        position: relative;
        display: inline-block;
        cursor: pointer;
      }}

      .tooltip .tooltiptext {{
        visibility: hidden;
        width: 250px;
        background-color: #555;
        color: #fff;
        text-align: left;
        padding: 5px 10px;
        border-radius: 5px;
        position: absolute;
        z-index: 1;
        top: 125%; /* below the button */
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        white-space: normal;
        word-wrap: break-word;
      }}

      /* Arrow pointing up */
      .tooltip .tooltiptext::before {{
        content: "";
        position: absolute;
        top: -5px; /* above the tooltip box */
        left: 50%;
        transform: translateX(-50%);
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #555 transparent; /* arrow pointing up */
      }}

      .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
      }}
    </style>
  </head>
  <body>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
      <div class="rectangle">
        <div class="group">
        <i class="fas fa-solid fa-calendar" style="font-size: 35px; opacity: 70%;;"></i>
          <div class="left_info">
            <h4 class="amount">38.9 DKK/andel</h4>
            <p class="date-info">X-dag 22. jan 2024</p>
          </div>
        </div>

        <div class="group">
          <div class="right_info">
            <h4 class="percentage">21%</h4>
            <p class="return-info">Udbytte</p>
          </div>
          <div class="tooltip">
        <i class="fas fa-solid fa-circle-info" style="font-size: 35px; opacity: 70%;;"></i>
            <span class="tooltiptext"> Udbyttet fragik kursen den 22. januar 2025. Udlodningen skete på baggrund af et samlet afkast i 2024 på 46 %, og er baseret på ligningslovens krav til minimumsudlodning. Udbyttet er opgjort til 38,90 kr./andel.</span>
          </div>
        </div>
      </div>
  </body>
</html>
    """
