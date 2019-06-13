"""
    Package to be installed --> google-cloud-datastore==1.7.3
"""

from google.cloud import datastore


def create_new_entity(kind, namespace, old_version_name, new_version_name):
    print("kind", kind)
    datastore_client = datastore.Client()
    old_version_properties = datastore_client.key(kind, old_version_name, namespace=namespace)
    print("old_version_properties", old_version_properties)
    old_version_properties_obj_dict = datastore_client.get(old_version_properties)
    if not old_version_properties_obj_dict:
        msg = "Please pass valid information. " \
              "Namespace or version are not matching."
        print(msg)
        return msg
    new_version_properties = datastore_client.key(kind, new_version_name, namespace=namespace)
    task = datastore.Entity(key=new_version_properties, exclude_from_indexes=('service_account_key',))
    for k, v in old_version_properties_obj_dict.items():
        task[k] = v
    datastore_client.put(task)
    print("Datstore got updated successfully")


def accept_datastore_input_with_kind():
    kind = 'Properties'
    namespace = input("Enter the Namespace name where you want to copy from?\n")
    old_version_name = input("Enter the Version name where you want to copy from?\n")
    new_version_name = input("Enter the New Version name where you want to copy to?\n")
    while True:
        res = input("You want to change the kind. Press y or n\n")
        if res in ["Yes", "y", "yes", "Y"]:
            kind = input("Enter the kind where you want to copy from.\n")
            create_new_entity(kind, namespace, old_version_name, new_version_name)
            break
        elif res in ["No", "n", "no", "N"]:
            print("Default kind is Properties.\n")
            create_new_entity(kind, namespace, old_version_name, new_version_name)
            break
        else:
            print("Enter right choice.\n")


def accept_datastore_input_without_kind():
    kind = 'Properties'
    namespace = input("Enter the Namespace name where you want to copy from?\n")
    old_version_name = input("Enter the Version name where you want to copy from?\n")
    new_version_name = input("Enter the New Version name where you want to copy to?\n")
    create_new_entity(kind, namespace, old_version_name, new_version_name)


if __name__ == '__main__':
    # accept_datastore_input_with_kind()
    accept_datastore_input_without_kind()
