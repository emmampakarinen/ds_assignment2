from xmlrpc.server import SimpleXMLRPCServer
import xml.etree.ElementTree as ET
import requests

S = requests.Session()
xml_data = "notes.xml"

# Design challenges taken into consideration:
# - Heterogeneity: different components are able to ineract (server, client, wikipedia API's)
# - Openness: system allows components to be added to database
# - Security: this is a quite simple system but security has been taken into consideration by checking for example user inputs in client side
# - scalability: using multiple servers and tested the system by using 2 users simultaneously
# - failure handling: using try-except blocks on the code for the system to recover from errors and avoiding the program from crashing
# - transparency: calls to server and APIs are not shown to client/users of the system. 

def add_note(note_topic, note_name, note_text, timestamp):
    try:
        tree = ET.parse(xml_data)
        root = tree.getroot()
    except Exception as e:
        root = ET.Element("data")
        tree = ET.ElementTree(root)

    # checking if the topic sent from client already exists
    topic = None
    for t in root.findall("topic"):
        if t.attrib["name"] == note_topic: # if there is a topic existing, adding the data under the existing topic
            topic = t
            break
    
    if topic == None: # if the topic name was not found -> create new topic
        topic = ET.SubElement(root, "topic", name=note_topic)

    # creating a new note within topic
    note = ET.SubElement(topic, "note", name=note_name)
    ET.SubElement(note, "text").text = note_text
    ET.SubElement(note, "timestamp").text = timestamp

    tree.write(xml_data)
    return "Note added successfully."


def get_notes(note_topic):
    notes = {}
    wikiInfo = []

    try:
        tree = ET.parse(xml_data)
        root = tree.getroot()
    except Exception as e:
        return e

    topic = None
    for t in root.findall("topic"):
        if t.attrib["name"] == note_topic:
            topic = t

            # checking if wikipedia link or summary are found from topic
            link_element = topic.find("link")
            summary_element = topic.find("summary")
    
            if link_element is not None:
                wikiInfo.append(link_element.text)

            if summary_element is not None:
                wikiInfo.append(summary_element.text)
            break

    if topic == None: # if the topic name was not found -> return
        return([notes, wikiInfo])
    
    if (topic.find("note") is not None):
        # if there are note elements in topic, adding notes to the dictionary element
        for note in topic.findall("note"):
            notes[note.attrib["name"]] = {"text": note.find('text').text, "timestamp": note.find('timestamp').text}

    return [notes, wikiInfo]
    

def add_wiki(note_topic):
    try:
        tree = ET.parse(xml_data)
        root = tree.getroot()
    except:
        root = ET.Element("data")
        tree = ET.ElementTree(root)

    # checking if the topic sent from client already exists
    topic = None
    for t in root.findall("topic"):
        if t.attrib["name"] == note_topic: # if there is a topic existing, adding the data under the existing topic
            topic = t
            break
    
    if topic == None: # if the topic name was not found -> create new topic
        topic = ET.SubElement(root, "topic", name=note_topic)

    URL = "https://en.wikipedia.org/w/api.php" # query wikipedia at server to get additional information about topic
    PARAMS = {
        "action": "opensearch",
        "namespace": "0",
        "search": note_topic,
        "limit": "1",
        "format": "json"
    }
    response = S.get(url=URL, params=PARAMS)
    data = response.json()
    
    url2 = "https://en.wikipedia.org/api/rest_v1/page/summary/" + note_topic
    resp2 = S.get(url=url2)
    data2 = resp2.json()

    # adding the wikipedia summary and link within topic
    ET.SubElement(topic, "summary").text = data2["extract"]
    ET.SubElement(topic, "link").text = data[3][0]

    tree.write(xml_data)
    return "Wikipedia information added successfully."


server = SimpleXMLRPCServer(("localhost", 8000))
print("Listening on port 8000...")
server.register_function(add_note, "add_note")
server.register_function(get_notes, "get_notes")
server.register_function(add_wiki, "add_wiki")
server.serve_forever()