# universe.py
# Edit this file whenever you want to change your watch universe.
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
    # ... (USA SECTION REMAINED UNCHANGED) ...
    # ============================================================
    # ============================ USA ============================
    # ============================================================

    # ETFs & Indexes (USA)
    {"ticker":"SPY","name":"SPDR S&P 500 ETF Trust","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("SPY","SPY ETF"),"market":"USA"},
    {"ticker":"QQQ","name":"Invesco QQQ Trust","sector":"ETFs & Indexes","tags":["ETF","Index","Nasdaq"],"links":_links("QQQ","QQQ ETF"),"market":"USA"},
    {"ticker":"DIA","name":"SPDR Dow Jones Industrial Average ETF Trust","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("DIA","DIA ETF"),"market":"USA"},
    {"ticker":"IWM","name":"iShares Russell 2000 ETF","sector":"ETFs & Indexes","tags":["ETF","Small Cap"],"links":_links("IWM","IWM ETF"),"market":"USA"},
    {"ticker":"VTI","name":"Vanguard Total Stock Market ETF","sector":"ETFs & Indexes","tags":["ETF","Total Market"],"links":_links("VTI","VTI ETF"),"market":"USA"},
    {"ticker":"VOO","name":"Vanguard S&P 500 ETF","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("VOO","VOO ETF"),"market":"USA"},
    {"ticker":"VXUS","name":"Vanguard Total International Stock ETF","sector":"ETFs & Indexes","tags":["ETF","International"],"links":_links("VXUS","VXUS ETF"),"market":"USA"},
    {"ticker":"TLT","name":"iShares 20+ Year Treasury Bond ETF","sector":"ETFs & Indexes","tags":["ETF","Bonds"],"links":_links("TLT","TLT ETF"),"market":"USA"},
    {"ticker":"IEF","name":"iShares 7-10 Year Treasury Bond ETF","sector":"ETFs & Indexes","tags":["ETF","Bonds"],"links":_links("IEF","IEF ETF"),"market":"USA"},
    {"ticker":"GLD","name":"SPDR Gold Shares","sector":"ETFs & Indexes","tags":["ETF","Gold"],"links":_links("GLD","GLD ETF"),"market":"USA"},
    {"ticker":"SLV","name":"iShares Silver Trust","sector":"ETFs & Indexes","tags":["ETF","Silver"],"links":_links("SLV","SLV ETF"),"market":"USA"},
    {"ticker":"USO","name":"United States Oil Fund","sector":"ETFs & Indexes","tags":["ETF","Oil"],"links":_links("USO","USO ETF"),"market":"USA"},
    {"ticker":"XLK","name":"Technology Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Tech"],"links":_links("XLK","XLK ETF"),"market":"USA"},
    {"ticker":"XLF","name":"Financial Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Financials"],"links":_links("XLF","XLF ETF"),"market":"USA"},
    {"ticker":"XLE","name":"Energy Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Energy"],"links":_links("XLE","XLE ETF"),"market":"USA"},
    {"ticker":"XLV","name":"Health Care Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Healthcare"],"links":_links("XLV","XLV ETF"),"market":"USA"},
    {"ticker":"XLI","name":"Industrial Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Industrials"],"links":_links("XLI","XLI ETF"),"market":"USA"},
    {"ticker":"XLP","name":"Consumer Staples Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Consumer"],"links":_links("XLP","XLP ETF"),"market":"USA"},
    {"ticker":"XLY","name":"Consumer Discretionary Select Sector SPDR Fund","sector":"ETFs & Indexes","tags":["ETF","Sector","Consumer"],"links":_links("XLY","XLY ETF"),"market":"USA"},

    # Big Tech (USA)
    {"ticker":"AAPL","name":"Apple Inc.","sector":"Big Tech","tags":["Mega-cap"],"links":_links("AAPL","Apple stock"),"market":"USA"},
    {"ticker":"MSFT","name":"Microsoft Corporation","sector":"Big Tech","tags":["Mega-cap"],"links":_links("MSFT","Microsoft stock"),"market":"USA"},
    {"ticker":"GOOGL","name":"Alphabet Inc. (Class A)","sector":"Big Tech","tags":["Mega-cap"],"links":_links("GOOGL","Alphabet GOOGL stock"),"market":"USA"},
    {"ticker":"AMZN","name":"Amazon.com, Inc.","sector":"Big Tech","tags":["Mega-cap"],"links":_links("AMZN","Amazon stock"),"market":"USA"},
    {"ticker":"META","name":"Meta Platforms, Inc.","sector":"Big Tech","tags":["Mega-cap"],"links":_links("META","Meta stock"),"market":"USA"},
    {"ticker":"TSLA","name":"Tesla, Inc.","sector":"Big Tech","tags":["Auto/Tech"],"links":_links("TSLA","Tesla stock"),"market":"USA"},
    {"ticker":"NFLX","name":"Netflix, Inc.","sector":"Big Tech","tags":["Streaming"],"links":_links("NFLX","Netflix stock"),"market":"USA"},
    {"ticker":"ORCL","name":"Oracle Corporation","sector":"Big Tech","tags":["Software"],"links":_links("ORCL","Oracle stock"),"market":"USA"},
    {"ticker":"ADBE","name":"Adobe Inc.","sector":"Big Tech","tags":["Software"],"links":_links("ADBE","Adobe stock"),"market":"USA"},
    {"ticker":"CRM","name":"Salesforce, Inc.","sector":"Big Tech","tags":["Software"],"links":_links("CRM","Salesforce stock"),"market":"USA"},
    {"ticker":"NOW","name":"ServiceNow, Inc.","sector":"Big Tech","tags":["Software"],"links":_links("NOW","ServiceNow stock"),"market":"USA"},
    {"ticker":"INTU","name":"Intuit Inc.","sector":"Big Tech","tags":["Software"],"links":_links("INTU","Intuit stock"),"market":"USA"},

    # Semiconductors (USA)
    {"ticker":"NVDA","name":"NVIDIA Corporation","sector":"Semiconductors","tags":["AI"],"links":_links("NVDA","NVIDIA stock"),"market":"USA"},
    {"ticker":"AMD","name":"Advanced Micro Devices, Inc.","sector":"Semiconductors","tags":["CPU/GPU"],"links":_links("AMD","AMD stock"),"market":"USA"},
    {"ticker":"INTC","name":"Intel Corporation","sector":"Semiconductors","tags":["CPU"],"links":_links("INTC","Intel stock"),"market":"USA"},
    {"ticker":"TSM","name":"Taiwan Semiconductor Manufacturing Company","sector":"Semiconductors","tags":["Foundry"],"links":_links("TSM","TSM stock"),"market":"USA"},
    {"ticker":"AVGO","name":"Broadcom Inc.","sector":"Semiconductors","tags":["Infra"],"links":_links("AVGO","Broadcom stock"),"market":"USA"},
    {"ticker":"QCOM","name":"Qualcomm Incorporated","sector":"Semiconductors","tags":["Mobile"],"links":_links("QCOM","Qualcomm stock"),"market":"USA"},
    {"ticker":"ASML","name":"ASML Holding N.V.","sector":"Semiconductors","tags":["Lithography"],"links":_links("ASML","ASML stock"),"market":"USA"},
    {"ticker":"MU","name":"Micron Technology, Inc.","sector":"Semiconductors","tags":["Memory"],"links":_links("MU","Micron stock"),"market":"USA"},
    {"ticker":"AMAT","name":"Applied Materials, Inc.","sector":"Semiconductors","tags":["Equipment"],"links":_links("AMAT","Applied Materials stock"),"market":"USA"},
    {"ticker":"LRCX","name":"Lam Research Corporation","sector":"Semiconductors","tags":["Equipment"],"links":_links("LRCX","Lam Research stock"),"market":"USA"},
    {"ticker":"KLAC","name":"KLA Corporation","sector":"Semiconductors","tags":["Equipment"],"links":_links("KLAC","KLA stock"),"market":"USA"},
    {"ticker":"MRVL","name":"Marvell Technology, Inc.","sector":"Semiconductors","tags":["Networking"],"links":_links("MRVL","Marvell stock"),"market":"USA"},

    # Financials (USA)
    {"ticker":"JPM","name":"JPMorgan Chase & Co.","sector":"Financials","tags":["Bank"],"links":_links("JPM","JPM stock"),"market":"USA"},
    {"ticker":"BAC","name":"Bank of America Corporation","sector":"Financials","tags":["Bank"],"links":_links("BAC","BAC stock"),"market":"USA"},
    {"ticker":"WFC","name":"Wells Fargo & Company","sector":"Financials","tags":["Bank"],"links":_links("WFC","WFC stock"),"market":"USA"},
    {"ticker":"GS","name":"Goldman Sachs Group, Inc.","sector":"Financials","tags":["Investment Bank"],"links":_links("GS","Goldman Sachs stock"),"market":"USA"},
    {"ticker":"MS","name":"Morgan Stanley","sector":"Financials","tags":["Investment Bank"],"links":_links("MS","Morgan Stanley stock"),"market":"USA"},
    {"ticker":"V","name":"Visa Inc.","sector":"Financials","tags":["Payments"],"links":_links("V","Visa stock"),"market":"USA"},
    {"ticker":"MA","name":"Mastercard Incorporated","sector":"Financials","tags":["Payments"],"links":_links("MA","Mastercard stock"),"market":"USA"},
    {"ticker":"AXP","name":"American Express Company","sector":"Financials","tags":["Payments"],"links":_links("AXP","American Express stock"),"market":"USA"},
    {"ticker":"BLK","name":"BlackRock, Inc.","sector":"Financials","tags":["Asset Mgmt"],"links":_links("BLK","BlackRock stock"),"market":"USA"},
    {"ticker":"SCHW","name":"Charles Schwab Corporation","sector":"Financials","tags":["Broker"],"links":_links("SCHW","Charles Schwab stock"),"market":"USA"},
    {"ticker":"C","name":"Citigroup Inc.","sector":"Financials","tags":["Bank"],"links":_links("C","Citigroup stock"),"market":"USA"},
    {"ticker":"BRK-B","name":"Berkshire Hathaway Inc. (Class B)","sector":"Financials","tags":["Conglomerate","Mega-cap"],"links":_links("BRK-B","Berkshire Hathaway stock"),"market":"USA"},

    # Consumer (USA)
    {"ticker":"WMT","name":"Walmart Inc.","sector":"Consumer","tags":["Retail"],"links":_links("WMT","Walmart stock"),"market":"USA"},
    {"ticker":"COST","name":"Costco Wholesale Corporation","sector":"Consumer","tags":["Retail"],"links":_links("COST","Costco stock"),"market":"USA"},
    {"ticker":"HD","name":"The Home Depot, Inc.","sector":"Consumer","tags":["Retail"],"links":_links("HD","Home Depot stock"),"market":"USA"},
    {"ticker":"NKE","name":"NIKE, Inc.","sector":"Consumer","tags":["Apparel"],"links":_links("NKE","Nike stock"),"market":"USA"},
    {"ticker":"MCD","name":"McDonald's Corporation","sector":"Consumer","tags":["Restaurants"],"links":_links("MCD","McDonalds stock"),"market":"USA"},
    {"ticker":"SBUX","name":"Starbucks Corporation","sector":"Consumer","tags":["Restaurants"],"links":_links("SBUX","Starbucks stock"),"market":"USA"},
    {"ticker":"DIS","name":"The Walt Disney Company","sector":"Consumer","tags":["Media"],"links":_links("DIS","Disney stock"),"market":"USA"},
    {"ticker":"TGT","name":"Target Corporation","sector":"Consumer","tags":["Retail"],"links":_links("TGT","Target stock"),"market":"USA"},
    {"ticker":"LOW","name":"Lowe's Companies, Inc.","sector":"Consumer","tags":["Retail"],"links":_links("LOW","Lowes stock"),"market":"USA"},
    {"ticker":"KO","name":"The Coca-Cola Company","sector":"Consumer","tags":["Beverages"],"links":_links("KO","Coca Cola stock"),"market":"USA"},
    {"ticker":"PEP","name":"PepsiCo, Inc.","sector":"Consumer","tags":["Beverages"],"links":_links("PEP","Pepsi stock"),"market":"USA"},
    {"ticker":"PG","name":"Procter & Gamble Company","sector":"Consumer","tags":["Staples"],"links":_links("PG","Procter Gamble stock"),"market":"USA"},

    # Healthcare (USA)
    {"ticker":"JNJ","name":"Johnson & Johnson","sector":"Healthcare","tags":["Pharma"],"links":_links("JNJ","Johnson and Johnson stock"),"market":"USA"},
    {"ticker":"PFE","name":"Pfizer Inc.","sector":"Healthcare","tags":["Pharma"],"links":_links("PFE","Pfizer stock"),"market":"USA"},
    {"ticker":"MRK","name":"Merck & Co., Inc.","sector":"Healthcare","tags":["Pharma"],"links":_links("MRK","Merck stock"),"market":"USA"},
    {"ticker":"LLY","name":"Eli Lilly and Company","sector":"Healthcare","tags":["Pharma"],"links":_links("LLY","Eli Lilly stock"),"market":"USA"},
    {"ticker":"UNH","name":"UnitedHealth Group Incorporated","sector":"Healthcare","tags":["Insurance"],"links":_links("UNH","UnitedHealth stock"),"market":"USA"},
    {"ticker":"ABBV","name":"AbbVie Inc.","sector":"Healthcare","tags":["Pharma"],"links":_links("ABBV","AbbVie stock"),"market":"USA"},
    {"ticker":"TMO","name":"Thermo Fisher Scientific Inc.","sector":"Healthcare","tags":["Tools"],"links":_links("TMO","Thermo Fisher stock"),"market":"USA"},
    {"ticker":"DHR","name":"Danaher Corporation","sector":"Healthcare","tags":["Tools"],"links":_links("DHR","Danaher stock"),"market":"USA"},
    {"ticker":"ISRG","name":"Intuitive Surgical, Inc.","sector":"Healthcare","tags":["MedTech"],"links":_links("ISRG","Intuitive Surgical stock"),"market":"USA"},
    {"ticker":"MDT","name":"Medtronic plc","sector":"Healthcare","tags":["MedTech"],"links":_links("MDT","Medtronic stock"),"market":"USA"},

    # Energy (USA)
    {"ticker":"XOM","name":"Exxon Mobil Corporation","sector":"Energy","tags":["Oil & Gas"],"links":_links("XOM","Exxon stock"),"market":"USA"},
    {"ticker":"CVX","name":"Chevron Corporation","sector":"Energy","tags":["Oil & Gas"],"links":_links("CVX","Chevron stock"),"market":"USA"},
    {"ticker":"COP","name":"ConocoPhillips","sector":"Energy","tags":["Oil & Gas"],"links":_links("COP","ConocoPhillips stock"),"market":"USA"},
    {"ticker":"SLB","name":"Schlumberger Limited","sector":"Energy","tags":["Services"],"links":_links("SLB","Schlumberger stock"),"market":"USA"},
    {"ticker":"EOG","name":"EOG Resources, Inc.","sector":"Energy","tags":["E&P"],"links":_links("EOG","EOG Resources stock"),"market":"USA"},
    {"ticker":"OXY","name":"Occidental Petroleum Corporation","sector":"Energy","tags":["Oil & Gas"],"links":_links("OXY","Occidental stock"),"market":"USA"},

    # Industrials (USA)
    {"ticker":"CAT","name":"Caterpillar Inc.","sector":"Industrials","tags":["Machinery"],"links":_links("CAT","Caterpillar stock"),"market":"USA"},
    {"ticker":"DE","name":"Deere & Company","sector":"Industrials","tags":["Machinery"],"links":_links("DE","Deere stock"),"market":"USA"},
    {"ticker":"BA","name":"The Boeing Company","sector":"Industrials","tags":["Aerospace"],"links":_links("BA","Boeing stock"),"market":"USA"},
    {"ticker":"GE","name":"GE Aerospace","sector":"Industrials","tags":["Aerospace"],"links":_links("GE","GE Aerospace stock"),"market":"USA"},
    {"ticker":"HON","name":"Honeywell International Inc.","sector":"Industrials","tags":["Conglomerate"],"links":_links("HON","Honeywell stock"),"market":"USA"},
    {"ticker":"UPS","name":"United Parcel Service, Inc.","sector":"Industrials","tags":["Logistics"],"links":_links("UPS","UPS stock"),"market":"USA"},
    {"ticker":"FDX","name":"FedEx Corporation","sector":"Industrials","tags":["Logistics"],"links":_links("FDX","FedEx stock"),"market":"USA"},
    {"ticker":"LMT","name":"Lockheed Martin Corporation","sector":"Industrials","tags":["Defense"],"links":_links("LMT","Lockheed Martin stock"),"market":"USA"},
    {"ticker":"NOC","name":"Northrop Grumman Corporation","sector":"Industrials","tags":["Defense"],"links":_links("NOC","Northrop Grumman stock"),"market":"USA"},
    {"ticker":"RTX","name":"RTX Corporation","sector":"Industrials","tags":["Defense"],"links":_links("RTX","RTX stock"),"market":"USA"},

    # ============================================================
    # =========================== INDIA ==========================
    # ============================================================

    # Index / ETFs (India)
    {"ticker":"^NSEI","name":"NIFTY 50 Index","sector":"ETFs & Indexes","tags":["Index"],"links":{"yahoo":"https://finance.yahoo.com/quote/%5ENSEI","google":"https://www.google.com/search?q=NIFTY+50+index"},"market":"INDIA"},
    {"ticker":"^NSEBANK","name":"NIFTY BANK Index","sector":"ETFs & Indexes","tags":["Index"],"links":{"yahoo":"https://finance.yahoo.com/quote/%5ENSEBANK","google":"https://www.google.com/search?q=NIFTY+BANK+index"},"market":"INDIA"},
    {"ticker":"NIFTYBEES.NS","name":"Nippon India ETF Nifty 50 BeES","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("NIFTYBEES.NS","NIFTYBEES ETF"),"market":"INDIA"},
    {"ticker":"BANKBEES.NS","name":"Nippon India ETF Bank BeES","sector":"ETFs & Indexes","tags":["ETF","Index","Bank"],"links":_links("BANKBEES.NS","BANKBEES ETF"),"market":"INDIA"},
    {"ticker":"JUNIORBEES.NS","name":"Nippon India ETF Nifty Next 50 Junior BeES","sector":"ETFs & Indexes","tags":["ETF","Index"],"links":_links("JUNIORBEES.NS","JUNIORBEES ETF"),"market":"INDIA"},

    # Big Indian Conglomerates / Core
    {"ticker":"RELIANCE.NS","name":"Reliance Industries","sector":"Energy","tags":["Mega-cap","Oil & Gas","Retail"],"links":_links("RELIANCE.NS","Reliance Industries stock"),"market":"INDIA"},
    
    # --- FIX: Changed TATAMOTORS.NS to TMCV.NS based on Yahoo availability ---
    {"ticker":"TMCV.NS","name":"Tata Motors","sector":"Industrials","tags":["Auto"],"links":_links("TMCV.NS","Tata Motors stock"),"market":"INDIA"},
    
    {"ticker":"TATASTEEL.NS","name":"Tata Steel","sector":"Industrials","tags":["Materials"],"links":_links("TATASTEEL.NS","Tata Steel stock"),"market":"INDIA"},
    {"ticker":"TCS.NS","name":"Tata Consultancy Services","sector":"Big Tech","tags":["IT","Mega-cap"],"links":_links("TCS.NS","TCS stock"),"market":"INDIA"},
    {"ticker":"INFY.NS","name":"Infosys","sector":"Big Tech","tags":["IT"],"links":_links("INFY.NS","Infosys stock"),"market":"INDIA"},
    {"ticker":"WIPRO.NS","name":"Wipro","sector":"Big Tech","tags":["IT"],"links":_links("WIPRO.NS","Wipro stock"),"market":"INDIA"},
    {"ticker":"HCLTECH.NS","name":"HCL Technologies","sector":"Big Tech","tags":["IT"],"links":_links("HCLTECH.NS","HCLTech stock"),"market":"INDIA"},
    {"ticker":"TECHM.NS","name":"Tech Mahindra","sector":"Big Tech","tags":["IT"],"links":_links("TECHM.NS","Tech Mahindra stock"),"market":"INDIA"},

    # Financials (India)
    {"ticker":"HDFCBANK.NS","name":"HDFC Bank","sector":"Financials","tags":["Bank","Mega-cap"],"links":_links("HDFCBANK.NS","HDFC Bank stock"),"market":"INDIA"},
    {"ticker":"ICICIBANK.NS","name":"ICICI Bank","sector":"Financials","tags":["Bank"],"links":_links("ICICIBANK.NS","ICICI Bank stock"),"market":"INDIA"},
    {"ticker":"SBIN.NS","name":"State Bank of India","sector":"Financials","tags":["Bank"],"links":_links("SBIN.NS","SBI stock"),"market":"INDIA"},
    {"ticker":"AXISBANK.NS","name":"Axis Bank","sector":"Financials","tags":["Bank"],"links":_links("AXISBANK.NS","Axis Bank stock"),"market":"INDIA"},
    {"ticker":"KOTAKBANK.NS","name":"Kotak Mahindra Bank","sector":"Financials","tags":["Bank"],"links":_links("KOTAKBANK.NS","Kotak Bank stock"),"market":"INDIA"},
    {"ticker":"INDUSINDBK.NS","name":"IndusInd Bank","sector":"Financials","tags":["Bank"],"links":_links("INDUSINDBK.NS","IndusInd Bank stock"),"market":"INDIA"},
    {"ticker":"BAJFINANCE.NS","name":"Bajaj Finance","sector":"Financials","tags":["NBFC"],"links":_links("BAJFINANCE.NS","Bajaj Finance stock"),"market":"INDIA"},
    {"ticker":"BAJAJFINSV.NS","name":"Bajaj Finserv","sector":"Financials","tags":["NBFC"],"links":_links("BAJAJFINSV.NS","Bajaj Finserv stock"),"market":"INDIA"},
    {"ticker":"HDFCLIFE.NS","name":"HDFC Life Insurance","sector":"Financials","tags":["Insurance"],"links":_links("HDFCLIFE.NS","HDFC Life stock"),"market":"INDIA"},
    {"ticker":"SBILIFE.NS","name":"SBI Life Insurance","sector":"Financials","tags":["Insurance"],"links":_links("SBILIFE.NS","SBI Life stock"),"market":"INDIA"},
    {"ticker":"LICI.NS","name":"Life Insurance Corporation (LIC)","sector":"Financials","tags":["Insurance"],"links":_links("LICI.NS","LIC stock India"),"market":"INDIA"},

    # Consumer (India)
    {"ticker":"ITC.NS","name":"ITC","sector":"Consumer","tags":["FMCG"],"links":_links("ITC.NS","ITC stock"),"market":"INDIA"},
    {"ticker":"HINDUNILVR.NS","name":"Hindustan Unilever","sector":"Consumer","tags":["FMCG"],"links":_links("HINDUNILVR.NS","HUL stock"),"market":"INDIA"},
    {"ticker":"NESTLEIND.NS","name":"Nestle India","sector":"Consumer","tags":["FMCG"],"links":_links("NESTLEIND.NS","Nestle India stock"),"market":"INDIA"},
    {"ticker":"BRITANNIA.NS","name":"Britannia Industries","sector":"Consumer","tags":["FMCG"],"links":_links("BRITANNIA.NS","Britannia stock"),"market":"INDIA"},
    {"ticker":"TATACONSUM.NS","name":"Tata Consumer Products","sector":"Consumer","tags":["FMCG"],"links":_links("TATACONSUM.NS","Tata Consumer stock"),"market":"INDIA"},
    {"ticker":"ASIANPAINT.NS","name":"Asian Paints","sector":"Consumer","tags":["Home"],"links":_links("ASIANPAINT.NS","Asian Paints stock"),"market":"INDIA"},
    {"ticker":"MARICO.NS","name":"Marico","sector":"Consumer","tags":["FMCG"],"links":_links("MARICO.NS","Marico stock"),"market":"INDIA"},
    {"ticker":"DABUR.NS","name":"Dabur India","sector":"Consumer","tags":["FMCG"],"links":_links("DABUR.NS","Dabur stock"),"market":"INDIA"},
    {"ticker":"TITAN.NS","name":"Titan Company","sector":"Consumer","tags":["Retail"],"links":_links("TITAN.NS","Titan stock"),"market":"INDIA"},
    {"ticker":"DMART.NS","name":"Avenue Supermarts (DMart)","sector":"Consumer","tags":["Retail"],"links":_links("DMART.NS","DMart stock"),"market":"INDIA"},
    {"ticker":"BHARTIARTL.NS","name":"Bharti Airtel","sector":"Consumer","tags":["Telecom"],"links":_links("BHARTIARTL.NS","Bharti Airtel stock"),"market":"INDIA"},

    # Healthcare / Pharma (India)
    {"ticker":"SUNPHARMA.NS","name":"Sun Pharmaceutical","sector":"Healthcare","tags":["Pharma"],"links":_links("SUNPHARMA.NS","Sun Pharma stock"),"market":"INDIA"},
    {"ticker":"DRREDDY.NS","name":"Dr. Reddy's Laboratories","sector":"Healthcare","tags":["Pharma"],"links":_links("DRREDDY.NS","Dr Reddy stock"),"market":"INDIA"},
    {"ticker":"CIPLA.NS","name":"Cipla","sector":"Healthcare","tags":["Pharma"],"links":_links("CIPLA.NS","Cipla stock"),"market":"INDIA"},
    {"ticker":"DIVISLAB.NS","name":"Divi's Laboratories","sector":"Healthcare","tags":["Pharma"],"links":_links("DIVISLAB.NS","Divis Labs stock"),"market":"INDIA"},
    {"ticker":"APOLLOHOSP.NS","name":"Apollo Hospitals","sector":"Healthcare","tags":["Hospitals"],"links":_links("APOLLOHOSP.NS","Apollo Hospitals stock"),"market":"INDIA"},
    {"ticker":"MAXHEALTH.NS","name":"Max Healthcare","sector":"Healthcare","tags":["Hospitals"],"links":_links("MAXHEALTH.NS","Max Healthcare stock"),"market":"INDIA"},

    # Industrials / Infra (India)
    {"ticker":"LT.NS","name":"Larsen & Toubro","sector":"Industrials","tags":["Infra","Mega-cap"],"links":_links("LT.NS","Larsen and Toubro stock"),"market":"INDIA"},
    {"ticker":"ULTRACEMCO.NS","name":"UltraTech Cement","sector":"Industrials","tags":["Cement"],"links":_links("ULTRACEMCO.NS","UltraTech Cement stock"),"market":"INDIA"},
    {"ticker":"GRASIM.NS","name":"Grasim Industries","sector":"Industrials","tags":["Materials"],"links":_links("GRASIM.NS","Grasim stock"),"market":"INDIA"},
    {"ticker":"ADANIPORTS.NS","name":"Adani Ports & SEZ","sector":"Industrials","tags":["Logistics"],"links":_links("ADANIPORTS.NS","Adani Ports stock"),"market":"INDIA"},
    {"ticker":"ADANIENT.NS","name":"Adani Enterprises","sector":"Industrials","tags":["Conglomerate"],"links":_links("ADANIENT.NS","Adani Enterprises stock"),"market":"INDIA"},
    {"ticker":"SIEMENS.NS","name":"Siemens India","sector":"Industrials","tags":["Electrical"],"links":_links("SIEMENS.NS","Siemens India stock"),"market":"INDIA"},
    {"ticker":"ABB.NS","name":"ABB India","sector":"Industrials","tags":["Electrical"],"links":_links("ABB.NS","ABB India stock"),"market":"INDIA"},

    # Auto (India)
    {"ticker":"MARUTI.NS","name":"Maruti Suzuki","sector":"Industrials","tags":["Auto"],"links":_links("MARUTI.NS","Maruti Suzuki stock"),"market":"INDIA"},
    {"ticker":"M&M.NS","name":"Mahindra & Mahindra","sector":"Industrials","tags":["Auto"],"links":_links("M&M.NS","Mahindra and Mahindra stock"),"market":"INDIA"},
    {"ticker":"EICHERMOT.NS","name":"Eicher Motors","sector":"Industrials","tags":["Auto","2W"],"links":_links("EICHERMOT.NS","Eicher Motors stock"),"market":"INDIA"},
    {"ticker":"BAJAJ-AUTO.NS","name":"Bajaj Auto","sector":"Industrials","tags":["Auto","2W"],"links":_links("BAJAJ-AUTO.NS","Bajaj Auto stock"),"market":"INDIA"},
    {"ticker":"HEROMOTOCO.NS","name":"Hero MotoCorp","sector":"Industrials","tags":["Auto","2W"],"links":_links("HEROMOTOCO.NS","Hero MotoCorp stock"),"market":"INDIA"},

    # Energy (India)
    {"ticker":"ONGC.NS","name":"Oil and Natural Gas Corporation (ONGC)","sector":"Energy","tags":["Oil & Gas"],"links":_links("ONGC.NS","ONGC stock"),"market":"INDIA"},
    {"ticker":"IOC.NS","name":"Indian Oil Corporation","sector":"Energy","tags":["Oil & Gas"],"links":_links("IOC.NS","Indian Oil stock"),"market":"INDIA"},
    {"ticker":"BPCL.NS","name":"Bharat Petroleum (BPCL)","sector":"Energy","tags":["Oil & Gas"],"links":_links("BPCL.NS","BPCL stock"),"market":"INDIA"},
    {"ticker":"POWERGRID.NS","name":"Power Grid Corporation","sector":"Energy","tags":["Utilities"],"links":_links("POWERGRID.NS","PowerGrid stock"),"market":"INDIA"},
    {"ticker":"NTPC.NS","name":"NTPC","sector":"Energy","tags":["Utilities"],"links":_links("NTPC.NS","NTPC stock"),"market":"INDIA"},
    {"ticker":"TATAPOWER.NS","name":"Tata Power","sector":"Energy","tags":["Utilities"],"links":_links("TATAPOWER.NS","Tata Power stock"),"market":"INDIA"},

    # Materials / Metals (India)
    {"ticker":"HINDALCO.NS","name":"Hindalco Industries","sector":"Industrials","tags":["Materials"],"links":_links("HINDALCO.NS","Hindalco stock"),"market":"INDIA"},
    {"ticker":"JSWSTEEL.NS","name":"JSW Steel","sector":"Industrials","tags":["Materials"],"links":_links("JSWSTEEL.NS","JSW Steel stock"),"market":"INDIA"},
    {"ticker":"COALINDIA.NS","name":"Coal India","sector":"Energy","tags":["Commodities"],"links":_links("COALINDIA.NS","Coal India stock"),"market":"INDIA"},

    # “New age” / misc big names (India)
    {"ticker":"IRCTC.NS","name":"IRCTC","sector":"Consumer","tags":["Travel"],"links":_links("IRCTC.NS","IRCTC stock"),"market":"INDIA"},
    {"ticker":"HAL.NS","name":"Hindustan Aeronautics (HAL)","sector":"Industrials","tags":["Defense"],"links":_links("HAL.NS","HAL stock India"),"market":"INDIA"},
    {"ticker":"BEL.NS","name":"Bharat Electronics (BEL)","sector":"Industrials","tags":["Defense"],"links":_links("BEL.NS","BEL stock India"),"market":"INDIA"},
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

# ---- Derived Groups (no changes needed to COMPANIES) ----
GROUPS = [
    "All",
    "ETFs & Indexes",
    "Big Tech",
    "Semiconductors",
    "Financials",
    "Consumer",
    "Healthcare",
    "Energy",
    "Industrials",
    "Mega-cap",
    "AI / Chips",
    "Bonds",
    "Commodities",
    "Defense",
    "Logistics",
    "Pharma / MedTech",
    "India (NSE)",
    "USA (NYSE/Nasdaq)",
]

def infer_group(c: dict) -> str:
    tags = [str(t).lower() for t in c.get("tags", [])]
    sector = str(c.get("sector", "")).strip()
    market = str(c.get("market", "USA")).strip().upper()

    # market grouping (super useful for your switch later)
    if market == "INDIA":
        return "India (NSE)"
    if market == "USA":
        # don’t force USA if sector tag is more informative
        pass

    # tag-driven groups (strong signal)
    if any("ai" in t for t in tags) or c.get("sector") == "Semiconductors":
        return "AI / Chips"
    if any("mega" in t for t in tags):
        return "Mega-cap"
    if any("bond" in t for t in tags):
        return "Bonds"
    if any(t in ("gold", "oil", "commodities") for t in tags) or c.get("ticker") in ("GLD", "USO", "SLV"):
        return "Commodities"
    if any("defense" in t for t in tags):
        return "Defense"
    if any("logistics" in t for t in tags):
        return "Logistics"
    if any(t in ("pharma", "medtech", "tools", "insurance", "hospitals") for t in tags):
        return "Pharma / MedTech"

    # fallback: sector is a perfectly good group
    if sector:
        return sector

    return "Industrials"

# Add a 'group' field to each company (in-place, keeps your data)
for _c in COMPANIES:
    _c["group"] = infer_group(_c)