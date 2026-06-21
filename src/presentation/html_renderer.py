class HTMLRenderer:
    """Renders Plotly JSON payloads into a self-contained HTML page."""

    # ------------------------------------------------------------------
    # Main chart page
    # ------------------------------------------------------------------

    @staticmethod
    def render_chart_page(regular_json: str, adjusted_json: str) -> str:
        """Return a full HTML document embedding two Plotly graphs."""
        return f"""\
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
      display: flex;
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
      #graph {{ height: 400px; }}
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
      regular:  {regular_json},
      adjusted: {adjusted_json}
    }};

    function getResponsiveFontSize() {{
      const w = window.innerWidth;
      if (w > 1000) return 18;
      if (w > 700)  return 14;
      return 10;
    }}

    function alignButtonsWithGraph() {{
      setTimeout(() => {{
        const graphDiv = document.getElementById("graph");
        const btnContainer = document.getElementById("button-container");
        if (!graphDiv || !btnContainer) return;
        const margin = graphDiv._fullLayout?.margin?.l ?? 80;
        btnContainer.style.paddingLeft = margin + "px";
      }}, 100);
    }}

    function loadGraph(view) {{
      window._lastView = view;
      const graphData = graphs[view];
      const layout = Object.assign({{}}, graphData.layout || {{}}, {{
        autosize: true,
        height: 600,
        dragmode: false,
        plot_bgcolor: "rgba(0,0,0,0)",
        paper_bgcolor: "rgba(0,0,0,0)",
        "updatemenus[0].font.size": getResponsiveFontSize()
      }});

      Plotly.newPlot("graph", graphData.data, layout, {{
        responsive:     true,
        displayModeBar: false,
        scrollZoom:     false,
        doubleClick:    false
      }}).then(alignButtonsWithGraph);
    }}

    window.addEventListener("resize", () => {{
      if (window._lastView) loadGraph(window._lastView);
    }});

    loadGraph("adjusted");
  </script>
</body>
</html>"""

    # ------------------------------------------------------------------
    # Dividend info box
    # ------------------------------------------------------------------

    @staticmethod
    def render_dividend_box(
        amount_per_share: str,
        ex_date: str,
        return_percentage: str,
        tooltip_text: str,
    ) -> str:
        """
        Render a standalone info box summarising a dividend event.

        All content is injected — nothing is hardcoded.
        """
        return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Udbytte</title>
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
  />
  <style>
    body {{ font-family: Arial, sans-serif; padding: 20px; }}

    .card {{
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
    .group  {{ display: flex; align-items: center; gap: 10px; }}
    .col    {{ display: flex; flex-direction: column; }}
    .col.right {{ text-align: right; }}

    .amount, .percentage {{
      font-size: 18px;
      font-weight: bold;
      margin: 0;
      color: #333;
    }}
    .meta {{ font-size: 12px; margin: 2px 0 0 0; color: #666; }}
    .label {{ font-size: 12px; margin: 2px 0 0 0; }}

    .tooltip {{ position: relative; display: inline-block; cursor: pointer; }}
    .tooltip .tip {{
      visibility: hidden;
      width: 250px;
      background-color: #555;
      color: #fff;
      text-align: left;
      padding: 5px 10px;
      border-radius: 5px;
      position: absolute;
      z-index: 1;
      top: 125%;
      left: 50%;
      transform: translateX(-50%);
      opacity: 0;
      transition: opacity 0.3s;
      white-space: normal;
      word-wrap: break-word;
    }}
    .tooltip .tip::before {{
      content: "";
      position: absolute;
      top: -5px;
      left: 50%;
      transform: translateX(-50%);
      border-width: 5px;
      border-style: solid;
      border-color: transparent transparent #555 transparent;
    }}
    .tooltip:hover .tip {{ visibility: visible; opacity: 1; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="group">
      <i class="fas fa-calendar" style="font-size:35px; opacity:70%;"></i>
      <div class="col">
        <h4 class="amount">{amount_per_share}</h4>
        <p class="meta">X-dag {ex_date}</p>
      </div>
    </div>

    <div class="group">
      <div class="col right">
        <h4 class="percentage">{return_percentage}</h4>
        <p class="label">Udbytte</p>
      </div>
      <div class="tooltip">
        <i class="fas fa-circle-info" style="font-size:35px; opacity:70%;"></i>
        <span class="tip">{tooltip_text}</span>
      </div>
    </div>
  </div>
</body>
</html>"""
