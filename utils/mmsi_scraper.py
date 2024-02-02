import requests
import pandas as pd
from bs4 import BeautifulSoup
'''
 Andrew Pfau
 script to auto scrape ship data from internet
 site: www.vesselfinder.com/vessels?name= MMSI Number
 Data recorded is MMSI, Dead Weigth Tonnage, description, and Size in meters (length / beam)
 Not every vessel has all this data, smaller ships do not lsit DWT

 DWT is a measure of weight a ship can carry, site does not list ship tonnage 

 Arguments: mmsi csv, a csv file with all of the mmsis to retrieve information for
            mmsiDB csv file name of where to save the data

'''
def mmsi_scraper(mmsis, mmsi_meta_cache=None):
    # dataframe to save ship data from web in, will become output file later
    if mmsi_meta_cache: 
        print("Using MMSI metadata cache: {}".format(mmsi_meta_cache), flush=True)
        mmsi_db = pd.read_csv(mmsi_meta_cache)
        # mmsi_db = mmsi_db.loc[mmsi_db['MMSI'].isin(mmsis['MMSI'].values),:].reset_index()
        return mmsi_db


    base_html = "https://www.vesselfinder.com/vessels?name="
    # needed to fool server into thinking we're a browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    collection = []
    for i, mmsi_data in mmsis.iterrows():
        mmsi = mmsi_data['MMSI']

        print(f'{i}: scraping for {mmsi}')
        tgt = base_html + str(mmsi)
        # get the html and pass into the soup parser
        html = requests.get(tgt, headers=headers)
        # verify we get the page ok
        if html.status_code == 200:
            html_dom = BeautifulSoup(html.content, features="html.parser")
            # verfiy we did not get 'No Results'
            check = html_dom.find("section", attrs={'class',"listing"})

            if check is None or (not ("No results" in check.get_text())):
                # dead weight tonnage
                dwt = html_dom.find("td", attrs={'class':'v5 hidden-mobile'}).get_text()

                if dwt == '-':
                    dwt=-1
                # size in meters, length / beam
                size = html_dom.find("td", attrs={'class':'v6 hidden-mobile'}).get_text()
                # ship description
                #des = html_dom.find("td", attrs={'class':'v2'}).find('small').get_text()
                try:
                    des = html_dom.find("td", attrs={'class': 'v2'}).find("div", attrs={'class': 'slty'}).get_text()
                except:
                    print("issue with parser!", flush=True)
                    des = 'Unknown'
                # TODO: fix this this is extremely slow. Collect all entries as list of dicts and create new dataframe
                collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':dwt, 'SIZE':size,'DESIG':des})

            # try again with IMO number if we have one
            elif mmsi_data['IMO']:
                tgt = base_html + str(mmsi_data['IMO'])
                # get the html and pass into the soup parser
                html = requests.get(tgt, headers=headers)
                # verify we get the page ok
                if html.status_code == 200:
                    html_dom = BeautifulSoup(html.content, features="html.parser")
                    # verfiy we did not get 'No Results'
                    check = html_dom.find("section", attrs={'class',"listing"})

                    if check is None or (not ("No results" in check.get_text())):
                        # dead weight tonnage
                        dwt = html_dom.find("td", attrs={'class':'v5 hidden-mobile'}).get_text()
                        if dwt == '-':
                            dwt=-1
                        # size in meters, length / beam
                        size = html_dom.find("td", attrs={'class':'v6 hidden-mobile'}).get_text()
                        try:
                            des = html_dom.find("td", attrs={'class': 'v2'}).find("div",attrs={'class': 'slty'}).get_text()
                        except:
                            print("issue with parser!", flush=True)
                            des = 'Unknown'
                        collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':dwt, 'SIZE':size,'DESIG':des})

                    else:
                        print("Did not find MMSI and IMO: " + str(mmsi_data['MMSI']) + " " + str(mmsi_data['IMO']), flush=True)
                        collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':-1, 'SIZE':-1, 'DESIG':-1})
                
                else:
                    print("Did not find MMSI and IMO: " + str(mmsi_data['MMSI']) + " " + str(mmsi_data['IMO']), flush=True)
                    collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':-1, 'SIZE':-1, 'DESIG':-1})

            else:
                print("Did not find MMSI and IMO: " + str(mmsi_data['MMSI']) + " " + str(mmsi_data['IMO']))
                # still append to list so we don't search again, all values -1 as flag
                collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':-1, 'SIZE':-1, 'DESIG':-1})
        else:
            print("Failed to retrieve page " + str(tgt), flush=True)
            collection.append({'MMSI':mmsi_data['MMSI'], 'DWT':-1, 'SIZE':-1, 'DESIG':-1})
    
    mmsi_db = pd.DataFrame(collection)
    return mmsi_db
