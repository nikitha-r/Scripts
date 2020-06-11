system_properties = [
  {
    "entityName": "phont50067us.homeoffice.wal-mart.com",
    "lastSeenDate": 1581120000000,
    "property": "system_data_center",
    "value": "ndc",
    "datafeedSource": "ipam_enrichment"
  },
  {
    "entityName": "phont50067us.homeoffice.wal-mart.com",
    "lastSeenDate": 1581120000000,
    "property": "system_data_center",
    "value": "ndc",
    "datafeedSource": "ipam_enrichment"
  },
  {
    "entityName": "phont50067us.homeoffice.wal-mart.com",
    "lastSeenDate": 1581120000000,
    "property": "system_tags",
    "value": "Data Center",
    "datafeedSource": "ok"
  },
  {
    "entityName": "phont50067us.homeoffice.wal-mart.com",
    "lastSeenDate": 1581120000000,
    "property": "system_data_center",
    "value": "edc",
    "datafeedSource": "ipam_enrichment"
  },
  {
    "entityName": "oser500970.wal-mart.com",
    "lastSeenDate": 1581120000000,
    "property": "system_data_center",
    "value": "cdc",
    "datafeedSource": "ipam_enrichment"
  }
]

#I wrote
def fetch_system_data_centers1(fetch_coordinates):
    result_dict = {}
    if system_properties:
        all_data_centers = []
        entity_add_list = [i.get('entityName') for i in system_properties]
        entity_add_list = set(entity_add_list)
        for entity in entity_add_list:
            data_centers = []
            for i in system_properties:
                if i.get('entityName') == entity and  i.get('property') == 'system_data_center' and i.get('datafeedSource') == 'ipam_enrichment':
                    data_centers.append(i.get('value'))
                    all_data_centers.append(i.get('value'))
            result_dict.update({entity: set(data_centers)})
    return result_dict


#Improvised(How to remove for loops.)
def fetch_system_data_centers(fetch_coordinates):
     all_data_centers = set([])
     result_dict = {}
     for property in data:
         entity = property.get('entityName')

         if entity not in result_dict:
             result_dict[entity] = []

         if property.get('property') == 'system_data_center' and property.get('datafeedSource') == 'ipam_enrichment':
             dc = property.get('value')
             all_data_centers.add(dc)

             if dc not in result_dict[entity]:
                 result_dict[entity].append(dc)



if __name__ == '__main__':
    result_dict = fetch_system_data_centers(fetch_coordinates=True)
    print(result_dict)
