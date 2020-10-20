import pandas as pd
import numpy as np
from flask import render_template, request
from webapp import app


@app.route("/")
def index():
    return render_template("Helsinki Rent Market.html");


@app.route("/search")
def search():
    return render_template("search.html", message = "" );


@app.route("/search", methods=["POST"])
def search_create():

    ###################################################################################################################
    # käyttäjä painaa nappia 'hae', ja muuttujiin tallennetaan nappien tilanne

    # montako huonetta (jos esim. kaikki, huoneet = '123' )
    huoneet = ''

    if(request.form.get("1room") == "1"): huoneet += str(1)
    if(request.form.get("2rooms") == "2"): huoneet += str(2)
    if(request.form.get("3rooms") == "3"): huoneet += str(3)
    if(len(huoneet) < 1): 
        return render_template("search.html", message = "Please select number of rooms.");

    # järjestyksessä esim. 0 = keskivuokran, 1 = kuukausivuokran ja 2 = etäisyyden perusteella
    jarjestys = 0
    if(request.form.get("sort") == "1"): jarjestys = 1
    if(request.form.get("sort") == "2"): jarjestys = 2
    
    # mitkä kaikki vuokrat valitaan
    kvARA, kvV, kvU =  0, 0, 0
    kkARA, kkV, kkU = 0, 0, 0

    ns = 0
    s = 0
    old = 0
    new = 0
    if(request.form.get("ns") == "1"): ns = 1
    if(request.form.get("s") == "1"): s = 1
    if(request.form.get("old") == "1"): old = 1
    if(request.form.get("new") == "1"): new = 1

    if(ns == 1 and old == 1): kvV, kkV = 1, 1
    if(ns == 1 and new == 1): kvU, kkU = 1, 1
    if(s == 1): kkARA, kvARA = 1, 1

    # mitkä kulkuneuvot valitaan
    dw, dt, db, dd = 0, 0, 0, 0
    if(request.form.get("dw") == "1"): dw = 1
    if(request.form.get("dt") == "1"): dt = 1
    if(request.form.get("db") == "1"): db = 1
    if(request.form.get("dd") == "1"): dd = 1


    temp = pd.read_csv("postalcodes.csv")

    ###################################################################################################################
    # taulun rajaus parametreillä
    for i in range(4):
        if ((str(i) in huoneet) == False):
            temp = temp.loc[temp['Huoneet'] != (str(i)) + 'h']
            temp = temp.loc[temp['Huoneet'] != (str(i)) + 'h+']

    temp.reset_index(drop=True, inplace=True)

    ################################################################################################################

    def pienempi(x, y):
        numbx = []
        numby = []
        
        for word in x. split():
            if word. isdigit():
                numbx. append(int(word))
        for word in y. split():
            if word. isdigit():
                numby. append(int(word))
        
        if(len(numbx) < len(numby)): 
            return True
        if(len(numbx) > len(numby)): 
            return False
        i = 0;
        while i < len(numbx):
            if(numbx[i] < numby[i]): 
                return True
            if(numbx[i] > numby[i]): 
                return False
            i += 1
        return True

    #################################################################################################################
    # lasketaan minimit

    temp['Min. keskivuokra'] = 0.0
    temp['Min. kuukausivuokra'] = 0.0
    temp['Min. etäisyys'] = '0'

    (n,m) = temp.shape

    for i in range(n):
        minkv = 1000000
        if ((kvARA == 1) and temp.iloc[i]['Keskivuokra - ARA-vuokra'] < minkv): 
            minkv = temp.iloc[i]['Keskivuokra - ARA-vuokra']
        if ((kvV == 1) and temp.iloc[i]['Keskivuokra - Vapaarah. vanhat'] < minkv): 
            minkv = temp.iloc[i]['Keskivuokra - Vapaarah. vanhat']
        if ((kvU == 1) and temp.iloc[i]['Keskivuokra - Vapaarah. uudet'] < minkv): 
            minkv = temp.iloc[i]['Keskivuokra - Vapaarah. uudet']
        temp.at[i, 'Min. keskivuokra'] = minkv

        minkk = 1000000
        if ((kkARA == 1) and temp.iloc[i]['Kuukausivuokra - ARA-vuokra'] < minkk): 
            minkk = temp.iloc[i]['Kuukausivuokra - ARA-vuokra']
        if ((kkV == 1) and temp.iloc[i]['Kuukausivuokra - Vapaarah. vanhat'] < minkk): 
            minkk = temp.iloc[i]['Kuukausivuokra - Vapaarah. vanhat']
        if ((kkU == 1) and temp.iloc[i]['Kuukausivuokra - Vapaarah. uudet'] < minkk): 
            minkk = temp.iloc[i]['Kuukausivuokra - Vapaarah. uudet']
        temp.at[i, 'Min. kuukausivuokra'] = minkk

        mind = '10 hours 00 mins'
        if ((dw == 1) and pienempi(temp.iloc[i]['duration-w'],mind)): 
            mind = temp.iloc[i]['duration-w']
        if ((dt == 1) and pienempi(temp.iloc[i]['duration-t'],mind)): 
            mind = temp.iloc[i]['duration-t']
        if ((dd == 1) and pienempi(temp.iloc[i]['duration-d'],mind)): 
            mind = temp.iloc[i]['duration-d']
        if ((db == 1) and pienempi(temp.iloc[i]['duration-b'],mind)): 
            mind = temp.iloc[i]['duration-b']
        temp.iloc[i, temp.columns.get_loc('Min. etäisyys')] = mind


    #################################################################################################################
    # taulun rajaus parametreillä 2.0

    if(request.form.get("maxmonth") != None and len(request.form.get("maxmonth")) > 0):
        temp = temp.loc[temp['Min. kuukausivuokra'] <= int(request.form.get("maxmonth"))]
    if(request.form.get("maxavg") != None and len(request.form.get("maxmonth")) > 0):
        temp = temp.loc[temp['Min. keskivuokra'] <= int(request.form.get("maxavg"))]

    #################################################################################################################
    # järjestetään

    if (jarjestys == 0):
        temp = temp.sort_values(by=['Min. keskivuokra'])
    if (jarjestys == 1):
        temp = temp.sort_values(by=['Min. kuukausivuokra'])
    if (jarjestys == 2):
        temp = temp.sort_values(by=['Min. etäisyys'])

    # palautetaan tulokset
    temp.reset_index(drop=True, inplace=True)

    (n,m) = temp.shape

    values = np.array([0,0,0,0,0])
    postalcodes = np.array(['0','0','0','0','0'], dtype=object)
    i = 0
    j = 0

    while((0 in values) and (i < n)):
        a = 0
        for k in range(j):
            if(temp.iloc[i]['Postalcode'] == values[k]):
                k = j
                a = 1

        if(a == 0):
            values[j] = temp.iloc[i]['Postalcode']
            postalcodes[j] = str(temp.iloc[i]['Name'])
            j += 1 
        i += 1

    if(values[0] == 0):
        message = "No postalcodes found."
        return render_template("search.html", message = message);

    message = "Recommended postalcodes: "  + "\n\n"

    for i in range(5):
        s = str(values[i])
        if(s != "0"):
            while(len(s) < 5):
                s = "0" + s
            message += s + "\t" + str(postalcodes[i]) +  "\n"

    
    #message = str(int(request.form.get("maxmonth")))
    return render_template("search.html", message = message);


@app.route("/walking_maps/00100_walk.html")
def m00100_walk():
    return render_template("/walking_maps/00100_walk.html");

@app.route("/walking_maps/00120_walk.html")
def m00120_walk():
    return render_template("/walking_maps/00120_walk.html");

@app.route("/walking_maps/00130_walk.html")
def m00130_walk():
    return render_template("/walking_maps/00130_walk.html");

@app.route("/walking_maps/00140_walk.html")
def m00140_walk():
    return render_template("/walking_maps/00140_walk.html");

@app.route("/walking_maps/00150_walk.html")
def m00150_walk():
    return render_template("/walking_maps/00150_walk.html");

@app.route("/walking_maps/00160_walk.html")
def m00160_walk():
    return render_template("/walking_maps/00160_walk.html");

@app.route("/walking_maps/00170_walk.html")
def m00170_walk():
    return render_template("/walking_maps/00170_walk.html");

@app.route("/walking_maps/00180_walk.html")
def m00180_walk():
    return render_template("/walking_maps/00180_walk.html");

@app.route("/walking_maps/00190_walk.html")
def m00190_walk():
    return render_template("/walking_maps/00190_walk.html");

@app.route("/walking_maps/00200_walk.html")
def m00200_walk():
    return render_template("/walking_maps/00200_walk.html");

@app.route("/walking_maps/00210_walk.html")
def m00210_walk():
    return render_template("/walking_maps/00210_walk.html");

@app.route("/walking_maps/00220_walk.html")
def m00220_walk():
    return render_template("/walking_maps/00220_walk.html");

@app.route("/walking_maps/00230_walk.html")
def m00230_walk():
    return render_template("/walking_maps/00230_walk.html");

@app.route("/walking_maps/00240_walk.html")
def m00240_walk():
    return render_template("/walking_maps/00240_walk.html");

@app.route("/walking_maps/00250_walk.html")
def m00250_walk():
    return render_template("/walking_maps/00250_walk.html");

@app.route("/walking_maps/00260_walk.html")
def m00260_walk():
    return render_template("/walking_maps/00260_walk.html");

@app.route("/walking_maps/00270_walk.html")
def m00270_walk():
    return render_template("/walking_maps/00270_walk.html");

@app.route("/walking_maps/00280_walk.html")
def m00280_walk():
    return render_template("/walking_maps/00280_walk.html");

@app.route("/walking_maps/00290_walk.html")
def m00290_walk():
    return render_template("/walking_maps/00290_walk.html");

@app.route("/walking_maps/00300_walk.html")
def m00300_walk():
    return render_template("/walking_maps/00300_walk.html");

@app.route("/walking_maps/00310_walk.html")
def m00310_walk():
    return render_template("/walking_maps/00310_walk.html");

@app.route("/walking_maps/00320_walk.html")
def m00320_walk():
    return render_template("/walking_maps/00320_walk.html");

@app.route("/walking_maps/00530_walk.html")
def m00530_walk():
    return render_template("/walking_maps/00530_walk.html");

@app.route("/walking_maps/00330_walk.html")
def m00330_walk():
    return render_template("/walking_maps/00330_walk.html");

@app.route("/walking_maps/00340_walk.html")
def m00340_walk():
    return render_template("/walking_maps/00340_walk.html");

@app.route("/walking_maps/00350_walk.html")
def m00350_walk():
    return render_template("/walking_maps/00350_walk.html");

@app.route("/walking_maps/00360_walk.html")
def m00360_walk():
    return render_template("/walking_maps/00360_walk.html");

@app.route("/walking_maps/00370_walk.html")
def m00370_walk():
    return render_template("/walking_maps/00370_walk.html");

@app.route("/walking_maps/00380_walk.html")
def m00380_walk():
    return render_template("/walking_maps/00380_walk.html");

@app.route("/walking_maps/00540_walk.html")
def m00540_walk():
    return render_template("/walking_maps/00540_walk.html");

@app.route("/walking_maps/00390_walk.html")
def m00390_walk():
    return render_template("/walking_maps/00390_walk.html");

@app.route("/walking_maps/00400_walk.html")
def m00400_walk():
    return render_template("/walking_maps/00400_walk.html");

@app.route("/walking_maps/00410_walk.html")
def m00410_walk():
    return render_template("/walking_maps/00410_walk.html");

@app.route("/walking_maps/00550_walk.html")
def m00550_walk():
    return render_template("/walking_maps/00550_walk.html");

@app.route("/walking_maps/00420_walk.html")
def m00420_walk():
    return render_template("/walking_maps/00420_walk.html");

@app.route("/walking_maps/00430_walk.html")
def m00430_walk():
    return render_template("/walking_maps/00430_walk.html");

@app.route("/walking_maps/00440_walk.html")
def m00440_walk():
    return render_template("/walking_maps/00440_walk.html");

@app.route("/walking_maps/00500_walk.html")
def m00500_walk():
    return render_template("/walking_maps/00500_walk.html");

@app.route("/walking_maps/00510_walk.html")
def m00510_walk():
    return render_template("/walking_maps/00510_walk.html");

@app.route("/walking_maps/00520_walk.html")
def m00520_walk():
    return render_template("/walking_maps/00520_walk.html");

@app.route("/walking_maps/00560_walk.html")
def m00560_walk():
    return render_template("/walking_maps/00560_walk.html");

@app.route("/walking_maps/00570_walk.html")
def m00570_walk():
    return render_template("/walking_maps/00570_walk.html");

@app.route("/walking_maps/00580_walk.html")
def m00580_walk():
    return render_template("/walking_maps/00580_walk.html");

@app.route("/walking_maps/00590_walk.html")
def m00590_walk():
    return render_template("/walking_maps/00590_walk.html");

@app.route("/walking_maps/00600_walk.html")
def m00600_walk():
    return render_template("/walking_maps/00600_walk.html");

@app.route("/walking_maps/00610_walk.html")
def m00610_walk():
    return render_template("/walking_maps/00610_walk.html");

@app.route("/walking_maps/00620_walk.html")
def m00620_walk():
    return render_template("/walking_maps/00620_walk.html");

@app.route("/walking_maps/00840_walk.html")
def m00840_walk():
    return render_template("/walking_maps/00840_walk.html");

@app.route("/walking_maps/00630_walk.html")
def m00630_walk():
    return render_template("/walking_maps/00630_walk.html");

@app.route("/walking_maps/00640_walk.html")
def m00640_walk():
    return render_template("/walking_maps/00640_walk.html");

@app.route("/walking_maps/00650_walk.html")
def m00650_walk():
    return render_template("/walking_maps/00650_walk.html");

@app.route("/walking_maps/00660_walk.html")
def m00660_walk():
    return render_template("/walking_maps/00660_walk.html");

@app.route("/walking_maps/00850_walk.html")
def m00850_walk():
    return render_template("/walking_maps/00850_walk.html");

@app.route("/walking_maps/00670_walk.html")
def m00670_walk():
    return render_template("/walking_maps/00670_walk.html");

@app.route("/walking_maps/00680_walk.html")
def m00680_walk():
    return render_template("/walking_maps/00680_walk.html");

@app.route("/walking_maps/00690_walk.html")
def m00690_walk():
    return render_template("/walking_maps/00690_walk.html");

@app.route("/walking_maps/00860_walk.html")
def m00860_walk():
    return render_template("/walking_maps/00860_walk.html");

@app.route("/walking_maps/00700_walk.html")
def m00700_walk():
    return render_template("/walking_maps/00700_walk.html");

@app.route("/walking_maps/00710_walk.html")
def m00710_walk():
    return render_template("/walking_maps/00710_walk.html");

@app.route("/walking_maps/00720_walk.html")
def m00720_walk():
    return render_template("/walking_maps/00720_walk.html");

@app.route("/walking_maps/00730_walk.html")
def m00730_walk():
    return render_template("/walking_maps/00730_walk.html");

@app.route("/walking_maps/00740_walk.html")
def m00740_walk():
    return render_template("/walking_maps/00740_walk.html");

@app.route("/walking_maps/00750_walk.html")
def m00750_walk():
    return render_template("/walking_maps/00750_walk.html");

@app.route("/walking_maps/00760_walk.html")
def m00760_walk():
    return render_template("/walking_maps/00760_walk.html");

@app.route("/walking_maps/00770_walk.html")
def m00770_walk():
    return render_template("/walking_maps/00770_walk.html");

@app.route("/walking_maps/00780_walk.html")
def m00780_walk():
    return render_template("/walking_maps/00780_walk.html");

@app.route("/walking_maps/00790_walk.html")
def m00790_walk():
    return render_template("/walking_maps/00790_walk.html");

@app.route("/walking_maps/00800_walk.html")
def m00800_walk():
    return render_template("/walking_maps/00800_walk.html");

@app.route("/walking_maps/00810_walk.html")
def m00810_walk():
    return render_template("/walking_maps/00810_walk.html");

@app.route("/walking_maps/00820_walk.html")
def m00820_walk():
    return render_template("/walking_maps/00820_walk.html");

@app.route("/walking_maps/00830_walk.html")
def m00830_walk():
    return render_template("/walking_maps/00830_walk.html");

@app.route("/walking_maps/00870_walk.html")
def m00870_walk():
    return render_template("/walking_maps/00870_walk.html");

@app.route("/walking_maps/00880_walk.html")
def m00880_walk():
    return render_template("/walking_maps/00880_walk.html");

@app.route("/walking_maps/00920_walk.html")
def m00920_walk():
    return render_template("/walking_maps/00920_walk.html");

@app.route("/walking_maps/00930_walk.html")
def m00930_walk():
    return render_template("/walking_maps/00930_walk.html");

@app.route("/walking_maps/00940_walk.html")
def m00940_walk():
    return render_template("/walking_maps/00940_walk.html");

@app.route("/walking_maps/00890_walk.html")
def m00890_walk():
    return render_template("/walking_maps/00890_walk.html");

@app.route("/walking_maps/00900_walk.html")
def m00900_walk():
    return render_template("/walking_maps/00900_walk.html");

@app.route("/walking_maps/00910_walk.html")
def m00910_walk():
    return render_template("/walking_maps/00910_walk.html");

@app.route("/walking_maps/00950_walk.html")
def m00950_walk():
    return render_template("/walking_maps/00950_walk.html");

@app.route("/walking_maps/00960_walk.html")
def m00960_walk():
    return render_template("/walking_maps/00960_walk.html");

@app.route("/walking_maps/00970_walk.html")
def m00970_walk():
    return render_template("/walking_maps/00970_walk.html");

@app.route("/walking_maps/00980_walk.html")
def m00980_walk():
    return render_template("/walking_maps/00980_walk.html");

@app.route("/walking_maps/00990_walk.html")
def m00990_walk():
    return render_template("/walking_maps/00990_walk.html");

@app.route("/walking_maps/01200_walk.html")
def m01200_walk():
    return render_template("/walking_maps/01200_walk.html");

@app.route("/walking_maps/01230_walk.html")
def m01230_walk():
    return render_template("/walking_maps/01230_walk.html");

@app.route("/walking_maps/01720_walk.html")
def m01720_walk():
    return render_template("/walking_maps/01720_walk.html");

@app.route("/walking_maps/01260_walk.html")
def m01260_walk():
    return render_template("/walking_maps/01260_walk.html");

@app.route("/walking_maps/01280_walk.html")
def m01280_walk():
    return render_template("/walking_maps/01280_walk.html");

@app.route("/walking_maps/01300_walk.html")
def m01300_walk():
    return render_template("/walking_maps/01300_walk.html");

@app.route("/walking_maps/01340_walk.html")
def m01340_walk():
    return render_template("/walking_maps/01340_walk.html");

@app.route("/walking_maps/01400_walk.html")
def m01400_walk():
    return render_template("/walking_maps/01400_walk.html");

@app.route("/walking_maps/01350_walk.html")
def m01350_walk():
    return render_template("/walking_maps/01350_walk.html");

@app.route("/walking_maps/01360_walk.html")
def m01360_walk():
    return render_template("/walking_maps/01360_walk.html");

@app.route("/walking_maps/01370_walk.html")
def m01370_walk():
    return render_template("/walking_maps/01370_walk.html");

@app.route("/walking_maps/01380_walk.html")
def m01380_walk():
    return render_template("/walking_maps/01380_walk.html");

@app.route("/walking_maps/01390_walk.html")
def m01390_walk():
    return render_template("/walking_maps/01390_walk.html");

@app.route("/walking_maps/01420_walk.html")
def m01420_walk():
    return render_template("/walking_maps/01420_walk.html");

@app.route("/walking_maps/01450_walk.html")
def m01450_walk():
    return render_template("/walking_maps/01450_walk.html");

@app.route("/walking_maps/01480_walk.html")
def m01480_walk():
    return render_template("/walking_maps/01480_walk.html");

@app.route("/walking_maps/01490_walk.html")
def m01490_walk():
    return render_template("/walking_maps/01490_walk.html");

@app.route("/walking_maps/01650_walk.html")
def m01650_walk():
    return render_template("/walking_maps/01650_walk.html");

@app.route("/walking_maps/01510_walk.html")
def m01510_walk():
    return render_template("/walking_maps/01510_walk.html");

@app.route("/walking_maps/01520_walk.html")
def m01520_walk():
    return render_template("/walking_maps/01520_walk.html");

@app.route("/walking_maps/01530_walk.html")
def m01530_walk():
    return render_template("/walking_maps/01530_walk.html");

@app.route("/walking_maps/01600_walk.html")
def m01600_walk():
    return render_template("/walking_maps/01600_walk.html");

@app.route("/walking_maps/01610_walk.html")
def m01610_walk():
    return render_template("/walking_maps/01610_walk.html");

@app.route("/walking_maps/01620_walk.html")
def m01620_walk():
    return render_template("/walking_maps/01620_walk.html");

@app.route("/walking_maps/01630_walk.html")
def m01630_walk():
    return render_template("/walking_maps/01630_walk.html");

@app.route("/walking_maps/01640_walk.html")
def m01640_walk():
    return render_template("/walking_maps/01640_walk.html");

@app.route("/walking_maps/01660_walk.html")
def m01660_walk():
    return render_template("/walking_maps/01660_walk.html");

@app.route("/walking_maps/01670_walk.html")
def m01670_walk():
    return render_template("/walking_maps/01670_walk.html");

@app.route("/walking_maps/01680_walk.html")
def m01680_walk():
    return render_template("/walking_maps/01680_walk.html");

@app.route("/walking_maps/01690_walk.html")
def m01690_walk():
    return render_template("/walking_maps/01690_walk.html");

@app.route("/walking_maps/01700_walk.html")
def m01700_walk():
    return render_template("/walking_maps/01700_walk.html");

@app.route("/walking_maps/01710_walk.html")
def m01710_walk():
    return render_template("/walking_maps/01710_walk.html");

@app.route("/walking_maps/01730_walk.html")
def m01730_walk():
    return render_template("/walking_maps/01730_walk.html");

@app.route("/walking_maps/01740_walk.html")
def m01740_walk():
    return render_template("/walking_maps/01740_walk.html");

@app.route("/walking_maps/01750_walk.html")
def m01750_walk():
    return render_template("/walking_maps/01750_walk.html");

@app.route("/walking_maps/01760_walk.html")
def m01760_walk():
    return render_template("/walking_maps/01760_walk.html");

@app.route("/walking_maps/01770_walk.html")
def m01770_walk():
    return render_template("/walking_maps/01770_walk.html");

@app.route("/walking_maps/01800_walk.html")
def m01800_walk():
    return render_template("/walking_maps/01800_walk.html");

@app.route("/walking_maps/02100_walk.html")
def m02100_walk():
    return render_template("/walking_maps/02100_walk.html");

@app.route("/walking_maps/02110_walk.html")
def m02110_walk():
    return render_template("/walking_maps/02110_walk.html");

@app.route("/walking_maps/02120_walk.html")
def m02120_walk():
    return render_template("/walking_maps/02120_walk.html");

@app.route("/walking_maps/02130_walk.html")
def m02130_walk():
    return render_template("/walking_maps/02130_walk.html");

@app.route("/walking_maps/02140_walk.html")
def m02140_walk():
    return render_template("/walking_maps/02140_walk.html");

@app.route("/walking_maps/02150_walk.html")
def m02150_walk():
    return render_template("/walking_maps/02150_walk.html");

@app.route("/walking_maps/02660_walk.html")
def m02660_walk():
    return render_template("/walking_maps/02660_walk.html");

@app.route("/walking_maps/02160_walk.html")
def m02160_walk():
    return render_template("/walking_maps/02160_walk.html");

@app.route("/walking_maps/02170_walk.html")
def m02170_walk():
    return render_template("/walking_maps/02170_walk.html");

@app.route("/walking_maps/02230_walk.html")
def m02230_walk():
    return render_template("/walking_maps/02230_walk.html");

@app.route("/walking_maps/02180_walk.html")
def m02180_walk():
    return render_template("/walking_maps/02180_walk.html");

@app.route("/walking_maps/02680_walk.html")
def m02680_walk():
    return render_template("/walking_maps/02680_walk.html");

@app.route("/walking_maps/02200_walk.html")
def m02200_walk():
    return render_template("/walking_maps/02200_walk.html");

@app.route("/walking_maps/02210_walk.html")
def m02210_walk():
    return render_template("/walking_maps/02210_walk.html");

@app.route("/walking_maps/02240_walk.html")
def m02240_walk():
    return render_template("/walking_maps/02240_walk.html");

@app.route("/walking_maps/02250_walk.html")
def m02250_walk():
    return render_template("/walking_maps/02250_walk.html");

@app.route("/walking_maps/02260_walk.html")
def m02260_walk():
    return render_template("/walking_maps/02260_walk.html");

@app.route("/walking_maps/02280_walk.html")
def m02280_walk():
    return render_template("/walking_maps/02280_walk.html");

@app.route("/walking_maps/02290_walk.html")
def m02290_walk():
    return render_template("/walking_maps/02290_walk.html");

@app.route("/walking_maps/02720_walk.html")
def m02720_walk():
    return render_template("/walking_maps/02720_walk.html");

@app.route("/walking_maps/02270_walk.html")
def m02270_walk():
    return render_template("/walking_maps/02270_walk.html");

@app.route("/walking_maps/02300_walk.html")
def m02300_walk():
    return render_template("/walking_maps/02300_walk.html");

@app.route("/walking_maps/02320_walk.html")
def m02320_walk():
    return render_template("/walking_maps/02320_walk.html");

@app.route("/walking_maps/02330_walk.html")
def m02330_walk():
    return render_template("/walking_maps/02330_walk.html");

@app.route("/walking_maps/02340_walk.html")
def m02340_walk():
    return render_template("/walking_maps/02340_walk.html");

@app.route("/walking_maps/02620_walk.html")
def m02620_walk():
    return render_template("/walking_maps/02620_walk.html");

@app.route("/walking_maps/02360_walk.html")
def m02360_walk():
    return render_template("/walking_maps/02360_walk.html");

@app.route("/walking_maps/02380_walk.html")
def m02380_walk():
    return render_template("/walking_maps/02380_walk.html");

@app.route("/walking_maps/02510_walk.html")
def m02510_walk():
    return render_template("/walking_maps/02510_walk.html");

@app.route("/walking_maps/02600_walk.html")
def m02600_walk():
    return render_template("/walking_maps/02600_walk.html");

@app.route("/walking_maps/02610_walk.html")
def m02610_walk():
    return render_template("/walking_maps/02610_walk.html");

@app.route("/walking_maps/02630_walk.html")
def m02630_walk():
    return render_template("/walking_maps/02630_walk.html");

@app.route("/walking_maps/02650_walk.html")
def m02650_walk():
    return render_template("/walking_maps/02650_walk.html");

@app.route("/walking_maps/02700_walk.html")
def m02700_walk():
    return render_template("/walking_maps/02700_walk.html");

@app.route("/walking_maps/02710_walk.html")
def m02710_walk():
    return render_template("/walking_maps/02710_walk.html");

@app.route("/walking_maps/02730_walk.html")
def m02730_walk():
    return render_template("/walking_maps/02730_walk.html");

@app.route("/walking_maps/02740_walk.html")
def m02740_walk():
    return render_template("/walking_maps/02740_walk.html");

@app.route("/walking_maps/02750_walk.html")
def m02750_walk():
    return render_template("/walking_maps/02750_walk.html");

@app.route("/walking_maps/02760_walk.html")
def m02760_walk():
    return render_template("/walking_maps/02760_walk.html");

@app.route("/walking_maps/02770_walk.html")
def m02770_walk():
    return render_template("/walking_maps/02770_walk.html");

@app.route("/walking_maps/02780_walk.html")
def m02780_walk():
    return render_template("/walking_maps/02780_walk.html");

@app.route("/walking_maps/02810_walk.html")
def m02810_walk():
    return render_template("/walking_maps/02810_walk.html");

@app.route("/walking_maps/02820_walk.html")
def m02820_walk():
    return render_template("/walking_maps/02820_walk.html");

@app.route("/walking_maps/02920_walk.html")
def m02920_walk():
    return render_template("/walking_maps/02920_walk.html");

@app.route("/walking_maps/02940_walk.html")
def m02940_walk():
    return render_template("/walking_maps/02940_walk.html");

@app.route("/walking_maps/02970_walk.html")
def m02970_walk():
    return render_template("/walking_maps/02970_walk.html");

@app.route("/walking_maps/02860_walk.html")
def m02860_walk():
    return render_template("/walking_maps/02860_walk.html");

@app.route("/walking_maps/02980_walk.html")
def m02980_walk():
    return render_template("/walking_maps/02980_walk.html");

@app.route("/walking_maps/04260_walk.html")
def m04260_walk():
    return render_template("/walking_maps/04260_walk.html");

@app.route("/walking_maps/04320_walk.html")
def m04320_walk():
    return render_template("/walking_maps/04320_walk.html");