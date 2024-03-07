from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import xmlrpc.client

server = xmlrpc.client.ServerProxy('http://localhost:8000') 
S = requests.Session()

# Design challenges taken into consideration:
# - Heterogeneity: different components are able to ineract (server, client, wikipedia API's)
# - Openness: system allows components to be added to database
# - Security: this is a quite simple system but security has been taken into consideration by checking for example user inputs in client side
# - scalability: using multiple servers and tested the system by using 2 users simultaneously
# - failure handling: using try-except blocks on the code for the system to recover from errors and avoiding the program from crashing
# - transparency: calls to server and APIs are not shown to client/users of the system.

while True:
    selection = input("1) Enter new note.\n2) Fetch notes by a topic.\n3) Fetch topic information from Wikipedia.\n0) Exit.\nSelection: ")
    match selection:
        case "1":
            try:
                topic = input("Give a topic for the note: ")
                name = input("Give a name for the note: ")
                text = input("Give a note: ")

                if (topic == "" or name == "" or text == ""):
                    raise ValueError
                
                now = datetime.now() 
                date_time = now.strftime("%m/%d/%Y - %H:%M:%S")
                print("Your note with topic: ", topic, " and text: ", text, " Timestamp: ", date_time)

                try: 
                    print(server.add_note(topic, name, text, date_time)) # fetching server and sending the note information to be added
                except:
                    print("Error occurred when trying to add data to database.\n")
            except Exception as e:
                print("An error occurred.\n")

        case "2":
            topic = input("Give a topic to be fetched: ")

            try: 
                [notes, wiki] = server.get_notes(topic) # calling server and sending the topic we want to fetch the corresponding notes

                if not notes and len(wiki) == 0: # if notes dictionary is empty
                    print("\nThere weren't notes under topic name:", topic, "\n")
                else:
                    
                    if (notes):
                        for note in notes:
                            print(note, "\n" + notes[note]["text"] + "\n" + notes[note]["timestamp"], "\n")
                    
                    if (len(wiki) != 0):
                        print("Summary:\n"+ wiki[1])
                        print("Link:\n" + wiki[0] + "\n")
            except:
                print("Error occurred when trying to fetch topic.\n")

        case "3":
            topic = input("Give a topic to be fetched from Wikipedia: ")
            URL = "https://en.wikipedia.org/w/api.php"
            PARAMS = {
                "action": "opensearch",
                "namespace": "0",
                "search": topic,
                "limit": "1",
                "format": "json"
            }
            response = S.get(url=URL, params=PARAMS)
            data = response.json()
            
            # wikipedia REST API https://en.wikipedia.org/api/rest_v1/
            url2 = "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic
            resp2 = S.get(url=url2)
            data2 = resp2.json()
            
            try:
                # if return type is not "ok" or multiple searches was found, raising TypeError
                if (data2["type"] == "disambiguation"):
                    raise TypeError
                
                # checking if the links to wikipedia pages match from both APIs
                if (data2["content_urls"]["desktop"]["page"] == data[3][0]):
                    print("\nFollowing data was found from Wikipedia on your searched topic:\n")
                    print("Title:", data[1][0])
                    print("Summary:", data2["extract"])
                    print("Link:", data[3][0], "\n")

                a = input("Do you want to add this information to given topic? (y/n): ")
                if(a == "y"):
                    try:
                        print(server.add_wiki(topic), "\n")
                    except:
                        print("An error occurred when adding wikipedia info to database.\n")

            except: 
                print("Wikipedia page was not found with given topic.\n")

        case "0":
            break
        case _:
            print("Invalid input.\n")
