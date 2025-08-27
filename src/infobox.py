from typing import List, Tuple
from src import DataCollector, FundReturn





def get_dividend_info(data: List[dict]) -> Tuple[float, str]:
    dividend = -1.0
    div_date = ""
    for k in reversed(data):
        if k.get("dividend", 0) > 0:
            dividend = k["dividend"]
            div_date = k["org_date"]
            break 
    
    return (dividend, div_date )

def create_box_html(div_date:str, div_amount:str, div_percent) -> str:
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
            border: 1px solid black;
            background-color: rgba(174, 172, 172, 0.658);
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
        width: 40px;
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

      /* Tooltip text */
      .tooltip .tooltiptext {{
        visibility: hidden;
        width: 160px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 6px;
        position: absolute;
        z-index: 1;
        bottom: 125%; /* position above the icon */
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 12px;
      }}

      /* Tooltip arrow */
      .tooltip .tooltiptext::after {{
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #333 transparent transparent transparent;
      }}

      /* Show on hover */
      .tooltip:hover .tooltiptext {{
        visibility: visible;
        opacity: 1;
      }}
    </style>
  </head>
  <body>
      <div class="rectangle">
        <div class="group">
          <img class="image" src="./calendar-solid-full.svg">
          <div class="left_info">
            <h4 class="amount">{div_amount} DKK/andel</h4>
            <p class="date-info">X-dag {div_date}</p>
          </div>
        </div>

        <div class="group">
          <div class="right_info">
            <h4 class="percentage">{div_percent}</h4>
            <p class="return-info">Direkte afkast</p>
          </div>
          <div class="tooltip">
            <img class="image" src="./circle-info-solid-full.svg">
            <span class="tooltiptext">Dette er en forklaring af afkastet.</span>
          </div>
        </div>
      </div>
  </body>
</html>
    """

with open("box.html", "w", encoding="utf-8") as f:
    f.write(create_box_html("22. jan","38.9", "25.5%"))
