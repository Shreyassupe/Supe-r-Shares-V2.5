# universe.py
# Expanded Watch Universe (~160+ Tickers)
# Format: {"ticker": "...", "name": "...", "sector": "...", "tags": [...], "links": {...}, "market": "USA"/"INDIA"}

def _links(ticker: str, query: str):
    from urllib.parse import quote_plus
    t = quote_plus(ticker)
    q = quote_plus(query)
    return {
        "yahoo": f"https://finance.yahoo.com/quote/{t}",
        "google": f"https://www.google.com/search?q={q}",
    }

MARKETS = ["USA", "INDIA"]

COMPANIES = [
    # ============================================================
    # ============================ USA ============================
    # ============================================================

    # --- ETFs & Indexes ---
    {"ticker":"SPY","name":"SPDR S&P 500 ETF","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("SPY","SPY ETF"),"market":"USA"},
    {"ticker":"QQQ","name":"Invesco QQQ Trust","sector":"ETFs & Indexes","tags":["ETF","Index","Nasdaq"],"links":_links("QQQ","QQQ ETF"),"market":"USA"},
    {"ticker":"DIA","name":"SPDR Dow Jones ETF","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("DIA","DIA ETF"),"market":"USA"},
    {"ticker":"IWM","name":"iShares Russell 2000","sector":"ETFs & Indexes","tags":["ETF","Small Cap"],"links":_links("IWM","IWM ETF"),"market":"USA"},
    {"ticker":"VTI","name":"Vanguard Total Stock","sector":"ETFs & Indexes","tags":["ETF","Total Market"],"links":_links("VTI","VTI ETF"),"market":"USA"},
    {"ticker":"VOO","name":"Vanguard S&P 500","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("VOO","VOO ETF"),"market":"USA"},
    {"ticker":"TLT","name":"iShares 20+ Year Treasury","sector":"ETFs & Indexes","tags":["ETF","Bonds"],"links":_links("TLT","TLT ETF"),"market":"USA"},
    {"ticker":"GLD","name":"SPDR Gold Shares","sector":"ETFs & Indexes","tags":["ETF","Gold"],"links":_links("GLD","GLD ETF"),"market":"USA"},
    {"ticker":"SLV","name":"iShares Silver Trust","sector":"ETFs & Indexes","tags":["ETF","Silver"],"links":_links("SLV","SLV ETF"),"market":"USA"},
    {"ticker":"USO","name":"United States Oil Fund","sector":"ETFs & Indexes","tags":["ETF","Oil"],"links":_links("USO","USO ETF"),"market":"USA"},
    {"ticker":"SMH","name":"VanEck Semiconductor ETF","sector":"ETFs & Indexes","tags":["ETF","Sector","Chips"],"links":_links("SMH","SMH ETF"),"market":"USA"},
    {"ticker":"XLE","name":"Energy Select Sector SPDR","sector":"ETFs & Indexes","tags":["ETF","Sector","Energy"],"links":_links("XLE","XLE ETF"),"market":"USA"},
    {"ticker":"XLK","name":"Technology Select Sector","sector":"ETFs & Indexes","tags":["ETF","Sector","Tech"],"links":_links("XLK","XLK ETF"),"market":"USA"},
    {"ticker":"XLV","name":"Health Care Select Sector","sector":"ETFs & Indexes","tags":["ETF","Sector","Healthcare"],"links":_links("XLV","XLV ETF"),"market":"USA"},
    {"ticker":"XLF","name":"Financial Select Sector","sector":"ETFs & Indexes","tags":["ETF","Sector","Financials"],"links":_links("XLF","XLF ETF"),"market":"USA"},
    {"ticker":"ARKK","name":"ARK Innovation ETF","sector":"ETFs & Indexes","tags":["ETF","Growth"],"links":_links("ARKK","ARKK ETF"),"market":"USA"},

    # --- Magnificent 7 & Big Tech ---
    {"ticker":"AAPL","name":"Apple Inc.","sector":"Big Tech","tags":["Mega-cap","Hardware"],"links":_links("AAPL","Apple stock"),"market":"USA"},
    {"ticker":"MSFT","name":"Microsoft Corporation","sector":"Big Tech","tags":["Mega-cap","Software"],"links":_links("MSFT","Microsoft stock"),"market":"USA"},
    {"ticker":"GOOGL","name":"Alphabet Inc.","sector":"Big Tech","tags":["Mega-cap","Search"],"links":_links("GOOGL","Google stock"),"market":"USA"},
    {"ticker":"AMZN","name":"Amazon.com, Inc.","sector":"Big Tech","tags":["Mega-cap","E-comm"],"links":_links("AMZN","Amazon stock"),"market":"USA"},
    {"ticker":"META","name":"Meta Platforms","sector":"Big Tech","tags":["Mega-cap","Social"],"links":_links("META","Meta stock"),"market":"USA"},
    {"ticker":"TSLA","name":"Tesla, Inc.","sector":"Big Tech","tags":["Auto","AI"],"links":_links("TSLA","Tesla stock"),"market":"USA"},
    {"ticker":"NVDA","name":"NVIDIA Corporation","sector":"Semiconductors","tags":["Mega-cap","AI","Chips"],"links":_links("NVDA","NVIDIA stock"),"market":"USA"},

    # --- Software, Cloud & AI ---
    {"ticker":"ORCL","name":"Oracle Corporation","sector":"Big Tech","tags":["Software","Cloud"],"links":_links("ORCL","Oracle stock"),"market":"USA"},
    {"ticker":"ADBE","name":"Adobe Inc.","sector":"Big Tech","tags":["Software","Creative"],"links":_links("ADBE","Adobe stock"),"market":"USA"},
    {"ticker":"CRM","name":"Salesforce, Inc.","sector":"Big Tech","tags":["Software","SaaS"],"links":_links("CRM","Salesforce stock"),"market":"USA"},
    {"ticker":"INTU","name":"Intuit Inc.","sector":"Big Tech","tags":["Software","Fintech"],"links":_links("INTU","Intuit stock"),"market":"USA"},
    {"ticker":"NOW","name":"ServiceNow","sector":"Big Tech","tags":["Software","SaaS"],"links":_links("NOW","ServiceNow stock"),"market":"USA"},
    {"ticker":"PLTR","name":"Palantir Technologies","sector":"Big Tech","tags":["AI","Data"],"links":_links("PLTR","Palantir stock"),"market":"USA"},
    {"ticker":"SNOW","name":"Snowflake Inc.","sector":"Big Tech","tags":["Cloud","Data"],"links":_links("SNOW","Snowflake stock"),"market":"USA"},
    {"ticker":"UBER","name":"Uber Technologies","sector":"Consumer","tags":["App","Transport"],"links":_links("UBER","Uber stock"),"market":"USA"},
    {"ticker":"ABNB","name":"Airbnb, Inc.","sector":"Consumer","tags":["App","Travel"],"links":_links("ABNB","Airbnb stock"),"market":"USA"},
    {"ticker":"PANW","name":"Palo Alto Networks","sector":"Big Tech","tags":["Cybersecurity"],"links":_links("PANW","Palo Alto Networks stock"),"market":"USA"},
    {"ticker":"CRWD","name":"CrowdStrike Holdings","sector":"Big Tech","tags":["Cybersecurity"],"links":_links("CRWD","CrowdStrike stock"),"market":"USA"},
    {"ticker":"NET","name":"Cloudflare","sector":"Big Tech","tags":["Cloud","Security"],"links":_links("NET","Cloudflare stock"),"market":"USA"},
    {"ticker":"SQ","name":"Block, Inc.","sector":"Financials","tags":["Fintech"],"links":_links("SQ","Square stock"),"market":"USA"},
    {"ticker":"PYPL","name":"PayPal Holdings","sector":"Financials","tags":["Fintech"],"links":_links("PYPL","PayPal stock"),"market":"USA"},
    {"ticker":"COIN","name":"Coinbase Global","sector":"Financials","tags":["Crypto"],"links":_links("COIN","Coinbase stock"),"market":"USA"},

    # --- Semiconductors ---
    {"ticker":"AMD","name":"Advanced Micro Devices","sector":"Semiconductors","tags":["Chips","AI"],"links":_links("AMD","AMD stock"),"market":"USA"},
    {"ticker":"INTC","name":"Intel Corporation","sector":"Semiconductors","tags":["Chips","Foundry"],"links":_links("INTC","Intel stock"),"market":"USA"},
    {"ticker":"TSM","name":"Taiwan Semi (TSMC)","sector":"Semiconductors","tags":["Foundry"],"links":_links("TSM","TSM stock"),"market":"USA"},
    {"ticker":"AVGO","name":"Broadcom Inc.","sector":"Semiconductors","tags":["Chips","Networking"],"links":_links("AVGO","Broadcom stock"),"market":"USA"},
    {"ticker":"QCOM","name":"Qualcomm","sector":"Semiconductors","tags":["Mobile","Chips"],"links":_links("QCOM","Qualcomm stock"),"market":"USA"},
    {"ticker":"MU","name":"Micron Technology","sector":"Semiconductors","tags":["Memory"],"links":_links("MU","Micron stock"),"market":"USA"},
    {"ticker":"AMAT","name":"Applied Materials","sector":"Semiconductors","tags":["Equipment"],"links":_links("AMAT","Applied Materials stock"),"market":"USA"},
    {"ticker":"LRCX","name":"Lam Research","sector":"Semiconductors","tags":["Equipment"],"links":_links("LRCX","Lam Research stock"),"market":"USA"},
    {"ticker":"TXN","name":"Texas Instruments","sector":"Semiconductors","tags":["Analog"],"links":_links("TXN","Texas Instruments stock"),"market":"USA"},
    {"ticker":"ARM","name":"Arm Holdings","sector":"Semiconductors","tags":["Design"],"links":_links("ARM","Arm stock"),"market":"USA"},

    # --- Financials ---
    {"ticker":"JPM","name":"JPMorgan Chase","sector":"Financials","tags":["Bank"],"links":_links("JPM","JPM stock"),"market":"USA"},
    {"ticker":"BAC","name":"Bank of America","sector":"Financials","tags":["Bank"],"links":_links("BAC","Bank of America stock"),"market":"USA"},
    {"ticker":"WFC","name":"Wells Fargo","sector":"Financials","tags":["Bank"],"links":_links("WFC","Wells Fargo stock"),"market":"USA"},
    {"ticker":"GS","name":"Goldman Sachs","sector":"Financials","tags":["Inv Bank"],"links":_links("GS","Goldman Sachs stock"),"market":"USA"},
    {"ticker":"MS","name":"Morgan Stanley","sector":"Financials","tags":["Inv Bank"],"links":_links("MS","Morgan Stanley stock"),"market":"USA"},
    {"ticker":"V","name":"Visa Inc.","sector":"Financials","tags":["Payments"],"links":_links("V","Visa stock"),"market":"USA"},
    {"ticker":"MA","name":"Mastercard","sector":"Financials","tags":["Payments"],"links":_links("MA","Mastercard stock"),"market":"USA"},
    {"ticker":"AXP","name":"American Express","sector":"Financials","tags":["Credit"],"links":_links("AXP","American Express stock"),"market":"USA"},
    {"ticker":"BLK","name":"BlackRock","sector":"Financials","tags":["Asset Mgmt"],"links":_links("BLK","BlackRock stock"),"market":"USA"},
    {"ticker":"BRK-B","name":"Berkshire Hathaway","sector":"Financials","tags":["Conglomerate"],"links":_links("BRK-B","Berkshire Hathaway stock"),"market":"USA"},

    # --- Consumer & Retail ---
    {"ticker":"WMT","name":"Walmart","sector":"Consumer","tags":["Retail"],"links":_links("WMT","Walmart stock"),"market":"USA"},
    {"ticker":"COST","name":"Costco","sector":"Consumer","tags":["Retail"],"links":_links("COST","Costco stock"),"market":"USA"},
    {"ticker":"TGT","name":"Target","sector":"Consumer","tags":["Retail"],"links":_links("TGT","Target stock"),"market":"USA"},
    {"ticker":"HD","name":"Home Depot","sector":"Consumer","tags":["Retail"],"links":_links("HD","Home Depot stock"),"market":"USA"},
    {"ticker":"NKE","name":"Nike","sector":"Consumer","tags":["Apparel"],"links":_links("NKE","Nike stock"),"market":"USA"},
    {"ticker":"SBUX","name":"Starbucks","sector":"Consumer","tags":["Coffee"],"links":_links("SBUX","Starbucks stock"),"market":"USA"},
    {"ticker":"MCD","name":"McDonald's","sector":"Consumer","tags":["Fast Food"],"links":_links("MCD","McDonalds stock"),"market":"USA"},
    {"ticker":"CMG","name":"Chipotle","sector":"Consumer","tags":["Fast Food"],"links":_links("CMG","Chipotle stock"),"market":"USA"},
    {"ticker":"KO","name":"Coca-Cola","sector":"Consumer","tags":["Beverage"],"links":_links("KO","Coca Cola stock"),"market":"USA"},
    {"ticker":"PEP","name":"PepsiCo","sector":"Consumer","tags":["Beverage"],"links":_links("PEP","Pepsi stock"),"market":"USA"},
    {"ticker":"PG","name":"Procter & Gamble","sector":"Consumer","tags":["Staples"],"links":_links("PG","Procter Gamble stock"),"market":"USA"},
    {"ticker":"DIS","name":"Disney","sector":"Consumer","tags":["Media"],"links":_links("DIS","Disney stock"),"market":"USA"},
    {"ticker":"NFLX","name":"Netflix","sector":"Consumer","tags":["Streaming"],"links":_links("NFLX","Netflix stock"),"market":"USA"},

    # --- Healthcare ---
    {"ticker":"LLY","name":"Eli Lilly","sector":"Healthcare","tags":["Pharma"],"links":_links("LLY","Eli Lilly stock"),"market":"USA"},
    {"ticker":"NVO","name":"Novo Nordisk","sector":"Healthcare","tags":["Pharma"],"links":_links("NVO","Novo Nordisk stock"),"market":"USA"},
    {"ticker":"UNH","name":"UnitedHealth","sector":"Healthcare","tags":["Insurance"],"links":_links("UNH","UnitedHealth stock"),"market":"USA"},
    {"ticker":"JNJ","name":"Johnson & Johnson","sector":"Healthcare","tags":["Pharma"],"links":_links("JNJ","JNJ stock"),"market":"USA"},
    {"ticker":"PFE","name":"Pfizer","sector":"Healthcare","tags":["Pharma"],"links":_links("PFE","Pfizer stock"),"market":"USA"},
    {"ticker":"MRK","name":"Merck","sector":"Healthcare","tags":["Pharma"],"links":_links("MRK","Merck stock"),"market":"USA"},
    {"ticker":"ABBV","name":"AbbVie","sector":"Healthcare","tags":["Pharma"],"links":_links("ABBV","AbbVie stock"),"market":"USA"},
    {"ticker":"ISRG","name":"Intuitive Surgical","sector":"Healthcare","tags":["MedTech"],"links":_links("ISRG","Intuitive Surgical stock"),"market":"USA"},
    {"ticker":"TMO","name":"Thermo Fisher","sector":"Healthcare","tags":["MedTech"],"links":_links("TMO","Thermo Fisher stock"),"market":"USA"},

    # --- Energy & Industrials ---
    {"ticker":"XOM","name":"Exxon Mobil","sector":"Energy","tags":["Oil & Gas"],"links":_links("XOM","Exxon stock"),"market":"USA"},
    {"ticker":"CVX","name":"Chevron","sector":"Energy","tags":["Oil & Gas"],"links":_links("CVX","Chevron stock"),"market":"USA"},
    {"ticker":"COP","name":"ConocoPhillips","sector":"Energy","tags":["Oil & Gas"],"links":_links("COP","ConocoPhillips stock"),"market":"USA"},
    {"ticker":"SLB","name":"Schlumberger","sector":"Energy","tags":["Services"],"links":_links("SLB","Schlumberger stock"),"market":"USA"},
    {"ticker":"OXY","name":"Occidental","sector":"Energy","tags":["Oil & Gas"],"links":_links("OXY","Occidental stock"),"market":"USA"},
    {"ticker":"GE","name":"GE Aerospace","sector":"Industrials","tags":["Aerospace"],"links":_links("GE","GE Aerospace stock"),"market":"USA"},
    {"ticker":"BA","name":"Boeing","sector":"Industrials","tags":["Aerospace"],"links":_links("BA","Boeing stock"),"market":"USA"},
    {"ticker":"CAT","name":"Caterpillar","sector":"Industrials","tags":["Machinery"],"links":_links("CAT","Caterpillar stock"),"market":"USA"},
    {"ticker":"DE","name":"Deere & Co","sector":"Industrials","tags":["Agriculture"],"links":_links("DE","Deere stock"),"market":"USA"},
    {"ticker":"LMT","name":"Lockheed Martin","sector":"Industrials","tags":["Defense"],"links":_links("LMT","Lockheed Martin stock"),"market":"USA"},
    {"ticker":"RTX","name":"RTX Corp","sector":"Industrials","tags":["Defense"],"links":_links("RTX","RTX stock"),"market":"USA"},
    {"ticker":"UPS","name":"UPS","sector":"Industrials","tags":["Logistics"],"links":_links("UPS","UPS stock"),"market":"USA"},
    {"ticker":"UNP","name":"Union Pacific","sector":"Industrials","tags":["Rail"],"links":_links("UNP","Union Pacific stock"),"market":"USA"},

    # ============================================================
    # =========================== INDIA ==========================
    # ============================================================

    # --- Indexes ---
    {"ticker":"^NSEI","name":"NIFTY 50","sector":"ETFs & Indexes","tags":["Index"],"links":_links("^NSEI","Nifty 50"),"market":"INDIA"},
    {"ticker":"^NSEBANK","name":"BANK NIFTY","sector":"ETFs & Indexes","tags":["Index"],"links":_links("^NSEBANK","Bank Nifty"),"market":"INDIA"},
    {"ticker":"^CNXIT","name":"NIFTY IT","sector":"ETFs & Indexes","tags":["Index"],"links":_links("^CNXIT","Nifty IT"),"market":"INDIA"},
    
    # --- Banking & Finance ---
    {"ticker":"HDFCBANK.NS","name":"HDFC Bank","sector":"Financials","tags":["Bank"],"links":_links("HDFCBANK.NS","HDFC Bank stock"),"market":"INDIA"},
    {"ticker":"ICICIBANK.NS","name":"ICICI Bank","sector":"Financials","tags":["Bank"],"links":_links("ICICIBANK.NS","ICICI Bank stock"),"market":"INDIA"},
    {"ticker":"SBIN.NS","name":"State Bank of India","sector":"Financials","tags":["PSU Bank"],"links":_links("SBIN.NS","SBI stock"),"market":"INDIA"},
    {"ticker":"KOTAKBANK.NS","name":"Kotak Bank","sector":"Financials","tags":["Bank"],"links":_links("KOTAKBANK.NS","Kotak Bank stock"),"market":"INDIA"},
    {"ticker":"AXISBANK.NS","name":"Axis Bank","sector":"Financials","tags":["Bank"],"links":_links("AXISBANK.NS","Axis Bank stock"),"market":"INDIA"},
    {"ticker":"BAJFINANCE.NS","name":"Bajaj Finance","sector":"Financials","tags":["NBFC"],"links":_links("BAJFINANCE.NS","Bajaj Finance stock"),"market":"INDIA"},
    {"ticker":"BAJAJFINSV.NS","name":"Bajaj Finserv","sector":"Financials","tags":["Fintech"],"links":_links("BAJAJFINSV.NS","Bajaj Finserv stock"),"market":"INDIA"},
    {"ticker":"JIOFIN.NS","name":"Jio Financial","sector":"Financials","tags":["NBFC"],"links":_links("JIOFIN.NS","Jio Financial stock"),"market":"INDIA"},
    {"ticker":"PFC.NS","name":"Power Finance Corp","sector":"Financials","tags":["PSU","NBFC"],"links":_links("PFC.NS","PFC stock"),"market":"INDIA"},
    {"ticker":"IREDA.NS","name":"IREDA","sector":"Financials","tags":["PSU","Green"],"links":_links("IREDA.NS","IREDA stock"),"market":"INDIA"},
    {"ticker":"LICI.NS","name":"LIC India","sector":"Financials","tags":["Insurance"],"links":_links("LICI.NS","LIC stock"),"market":"INDIA"},

    # --- IT Services ---
    {"ticker":"TCS.NS","name":"TCS","sector":"Big Tech","tags":["IT"],"links":_links("TCS.NS","TCS stock"),"market":"INDIA"},
    {"ticker":"INFY.NS","name":"Infosys","sector":"Big Tech","tags":["IT"],"links":_links("INFY.NS","Infosys stock"),"market":"INDIA"},
    {"ticker":"HCLTECH.NS","name":"HCL Tech","sector":"Big Tech","tags":["IT"],"links":_links("HCLTECH.NS","HCL Tech stock"),"market":"INDIA"},
    {"ticker":"WIPRO.NS","name":"Wipro","sector":"Big Tech","tags":["IT"],"links":_links("WIPRO.NS","Wipro stock"),"market":"INDIA"},
    {"ticker":"TECHM.NS","name":"Tech Mahindra","sector":"Big Tech","tags":["IT"],"links":_links("TECHM.NS","Tech Mahindra stock"),"market":"INDIA"},
    {"ticker":"LTIM.NS","name":"LTIMindtree","sector":"Big Tech","tags":["IT"],"links":_links("LTIM.NS","LTIMindtree stock"),"market":"INDIA"},
    
    # --- Auto & Mobility ---
    {"ticker":"TMCV.NS","name":"Tata Motors","sector":"Industrials","tags":["Auto","EV"],"links":_links("TMCV.NS","Tata Motors stock"),"market":"INDIA"},
    {"ticker":"M&M.NS","name":"Mahindra & Mahindra","sector":"Industrials","tags":["Auto","SUV"],"links":_links("M&M.NS","Mahindra stock"),"market":"INDIA"},
    {"ticker":"MARUTI.NS","name":"Maruti Suzuki","sector":"Industrials","tags":["Auto"],"links":_links("MARUTI.NS","Maruti stock"),"market":"INDIA"},
    {"ticker":"BAJAJ-AUTO.NS","name":"Bajaj Auto","sector":"Industrials","tags":["Auto","2W"],"links":_links("BAJAJ-AUTO.NS","Bajaj Auto stock"),"market":"INDIA"},
    {"ticker":"EICHERMOT.NS","name":"Eicher Motors","sector":"Industrials","tags":["Auto","Royal Enfield"],"links":_links("EICHERMOT.NS","Eicher Motors stock"),"market":"INDIA"},
    {"ticker":"TVSMOTOR.NS","name":"TVS Motor","sector":"Industrials","tags":["Auto","2W"],"links":_links("TVSMOTOR.NS","TVS Motor stock"),"market":"INDIA"},
    {"ticker":"HEROMOTOCO.NS","name":"Hero MotoCorp","sector":"Industrials","tags":["Auto","2W"],"links":_links("HEROMOTOCO.NS","Hero MotoCorp stock"),"market":"INDIA"},

    # --- Energy & Power ---
    {"ticker":"RELIANCE.NS","name":"Reliance Ind","sector":"Energy","tags":["Conglomerate","Oil"],"links":_links("RELIANCE.NS","Reliance Industries stock"),"market":"INDIA"},
    {"ticker":"NTPC.NS","name":"NTPC","sector":"Energy","tags":["Power","PSU"],"links":_links("NTPC.NS","NTPC stock"),"market":"INDIA"},
    {"ticker":"POWERGRID.NS","name":"Power Grid","sector":"Energy","tags":["Power","PSU"],"links":_links("POWERGRID.NS","PowerGrid stock"),"market":"INDIA"},
    {"ticker":"ONGC.NS","name":"ONGC","sector":"Energy","tags":["Oil","PSU"],"links":_links("ONGC.NS","ONGC stock"),"market":"INDIA"},
    {"ticker":"COALINDIA.NS","name":"Coal India","sector":"Energy","tags":["Coal","PSU"],"links":_links("COALINDIA.NS","Coal India stock"),"market":"INDIA"},
    {"ticker":"TATAPOWER.NS","name":"Tata Power","sector":"Energy","tags":["Power","EV"],"links":_links("TATAPOWER.NS","Tata Power stock"),"market":"INDIA"},
    {"ticker":"ADANIGREEN.NS","name":"Adani Green","sector":"Energy","tags":["Renewable"],"links":_links("ADANIGREEN.NS","Adani Green stock"),"market":"INDIA"},
    {"ticker":"ADANIPOWER.NS","name":"Adani Power","sector":"Energy","tags":["Power"],"links":_links("ADANIPOWER.NS","Adani Power stock"),"market":"INDIA"},
    {"ticker":"BPCL.NS","name":"BPCL","sector":"Energy","tags":["Oil","PSU"],"links":_links("BPCL.NS","BPCL stock"),"market":"INDIA"},
    {"ticker":"IOC.NS","name":"Indian Oil","sector":"Energy","tags":["Oil","PSU"],"links":_links("IOC.NS","Indian Oil stock"),"market":"INDIA"},
    {"ticker":"GAIL.NS","name":"GAIL","sector":"Energy","tags":["Gas","PSU"],"links":_links("GAIL.NS","GAIL stock"),"market":"INDIA"},

    # --- Consumer (FMCG, Retail) ---
    {"ticker":"ITC.NS","name":"ITC Ltd","sector":"Consumer","tags":["FMCG"],"links":_links("ITC.NS","ITC stock"),"market":"INDIA"},
    {"ticker":"HINDUNILVR.NS","name":"HUL","sector":"Consumer","tags":["FMCG"],"links":_links("HINDUNILVR.NS","HUL stock"),"market":"INDIA"},
    {"ticker":"NESTLEIND.NS","name":"Nestle India","sector":"Consumer","tags":["FMCG"],"links":_links("NESTLEIND.NS","Nestle India stock"),"market":"INDIA"},
    {"ticker":"TITAN.NS","name":"Titan Company","sector":"Consumer","tags":["Luxury"],"links":_links("TITAN.NS","Titan stock"),"market":"INDIA"},
    {"ticker":"ASIANPAINT.NS","name":"Asian Paints","sector":"Consumer","tags":["Home"],"links":_links("ASIANPAINT.NS","Asian Paints stock"),"market":"INDIA"},
    {"ticker":"TRENT.NS","name":"Trent Ltd","sector":"Consumer","tags":["Retail","Fashion"],"links":_links("TRENT.NS","Trent stock"),"market":"INDIA"},
    {"ticker":"DMART.NS","name":"DMart","sector":"Consumer","tags":["Retail"],"links":_links("DMART.NS","DMart stock"),"market":"INDIA"},
    {"ticker":"VBL.NS","name":"Varun Beverages","sector":"Consumer","tags":["Beverage"],"links":_links("VBL.NS","Varun Beverages stock"),"market":"INDIA"},
    {"ticker":"ZOMATO.NS","name":"Zomato","sector":"Consumer","tags":["Tech","Food"],"links":_links("ZOMATO.NS","Zomato stock"),"market":"INDIA"},

    # --- Defense, Rail & Infra (Public Sector) ---
    {"ticker":"HAL.NS","name":"HAL","sector":"Industrials","tags":["Defense","PSU"],"links":_links("HAL.NS","HAL stock"),"market":"INDIA"},
    {"ticker":"BEL.NS","name":"Bharat Electronics","sector":"Industrials","tags":["Defense","PSU"],"links":_links("BEL.NS","BEL stock"),"market":"INDIA"},
    {"ticker":"MAZDOCK.NS","name":"Mazagon Dock","sector":"Industrials","tags":["Defense","Ship"],"links":_links("MAZDOCK.NS","Mazagon Dock stock"),"market":"INDIA"},
    {"ticker":"COCHINSHIP.NS","name":"Cochin Shipyard","sector":"Industrials","tags":["Defense","Ship"],"links":_links("COCHINSHIP.NS","Cochin Shipyard stock"),"market":"INDIA"},
    {"ticker":"RVNL.NS","name":"RVNL","sector":"Industrials","tags":["Rail","PSU"],"links":_links("RVNL.NS","RVNL stock"),"market":"INDIA"},
    {"ticker":"IRFC.NS","name":"IRFC","sector":"Financials","tags":["Rail","PSU"],"links":_links("IRFC.NS","IRFC stock"),"market":"INDIA"},
    {"ticker":"LT.NS","name":"Larsen & Toubro","sector":"Industrials","tags":["Infra"],"links":_links("LT.NS","Larsen Toubro stock"),"market":"INDIA"},
    {"ticker":"ADANIENT.NS","name":"Adani Enterprises","sector":"Industrials","tags":["Conglomerate"],"links":_links("ADANIENT.NS","Adani Enterprises stock"),"market":"INDIA"},
    {"ticker":"ADANIPORTS.NS","name":"Adani Ports","sector":"Industrials","tags":["Infra"],"links":_links("ADANIPORTS.NS","Adani Ports stock"),"market":"INDIA"},

    # --- Pharma & Healthcare ---
    {"ticker":"SUNPHARMA.NS","name":"Sun Pharma","sector":"Healthcare","tags":["Pharma"],"links":_links("SUNPHARMA.NS","Sun Pharma stock"),"market":"INDIA"},
    {"ticker":"CIPLA.NS","name":"Cipla","sector":"Healthcare","tags":["Pharma"],"links":_links("CIPLA.NS","Cipla stock"),"market":"INDIA"},
    {"ticker":"DRREDDY.NS","name":"Dr. Reddy's","sector":"Healthcare","tags":["Pharma"],"links":_links("DRREDDY.NS","Dr Reddy stock"),"market":"INDIA"},
    {"ticker":"DIVISLAB.NS","name":"Divi's Labs","sector":"Healthcare","tags":["Pharma"],"links":_links("DIVISLAB.NS","Divis Lab stock"),"market":"INDIA"},
    {"ticker":"APOLLOHOSP.NS","name":"Apollo Hospitals","sector":"Healthcare","tags":["Hospital"],"links":_links("APOLLOHOSP.NS","Apollo Hospitals stock"),"market":"INDIA"},

    # --- Metals & Commodities ---
    {"ticker":"TATASTEEL.NS","name":"Tata Steel","sector":"Industrials","tags":["Steel"],"links":_links("TATASTEEL.NS","Tata Steel stock"),"market":"INDIA"},
    {"ticker":"JSWSTEEL.NS","name":"JSW Steel","sector":"Industrials","tags":["Steel"],"links":_links("JSWSTEEL.NS","JSW Steel stock"),"market":"INDIA"},
    {"ticker":"HINDALCO.NS","name":"Hindalco","sector":"Industrials","tags":["Aluminum"],"links":_links("HINDALCO.NS","Hindalco stock"),"market":"INDIA"},
    {"ticker":"VEDL.NS","name":"Vedanta","sector":"Industrials","tags":["Mining"],"links":_links("VEDL.NS","Vedanta stock"),"market":"INDIA"},
]

SECTORS = [
    "ETFs & Indexes",
    "Big Tech",
    "Semiconductors",
    "Financials",
    "Consumer",
    "Healthcare",
    "Energy",
    "Industrials",
]

def infer_group(c: dict) -> str:
    tags = [str(t).lower() for t in c.get("tags", [])]
    sector = str(c.get("sector", "")).strip()
    market = str(c.get("market", "USA")).strip().upper()

    if market == "INDIA": return "India (NSE)"
    
    # Tag-based grouping
    if any("ai" in t for t in tags) or sector == "Semiconductors": return "AI / Chips"
    if any("mega" in t for t in tags): return "Mega-cap"
    if any("oil" in t or "gas" in t for t in tags): return "Energy"
    if any("defense" in t for t in tags): return "Defense"
    if "pharma" in tags or "medtech" in tags: return "Pharma / MedTech"
    
    return sector

# Apply grouping
for _c in COMPANIES:
    _c["group"] = infer_group(_c)