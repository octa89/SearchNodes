import pyodbc
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection


def list_feature_layers(feature_layers):
    print("Available Feature Layers:")
    for idx, layer in enumerate(feature_layers, 1):
        print(f"{idx}. {layer.properties.name} (ID: {layer.properties.id})")


def get_selected_feature_layer(gis, service_url):
    try:
        # Access the feature service directly from the URL
        service = FeatureLayerCollection(service_url, gis)
        feature_layers = service.layers

        if not feature_layers:
            raise ValueError(f"No feature layers found in the service URL: {service_url}")

        list_feature_layers(feature_layers)

        selected_idx = int(input("Select the feature layer by number: ")) - 1
        selected_layer = feature_layers[selected_idx]
        return selected_layer
    except Exception as e:
        print(f"Error fetching feature layer: {e}")
        return None


def get_field_mappings(feature_layer, access_table, accdb_cursor):
    if feature_layer is None:
        raise ValueError("No valid feature layer selected.")

    # List fields from the feature layer
    geo_fields = [field['name'] for field in feature_layer.properties.fields]
    print("Feature Layer Fields:")
    for idx, field in enumerate(geo_fields, 1):
        print(f"{idx}. {field}")

    # Query Access to list its table columns
    accdb_cursor.execute(f"SELECT * FROM {access_table}")
    access_columns = [column[0] for column in accdb_cursor.description]
    print("\nAccess Database Fields:")
    for idx, column in enumerate(access_columns, 1):
        print(f"{idx}. {column}")

    # Prompt for field mapping
    field_map = {}
    print("\nEnter '0' to omit a field.")
    for geo_field in geo_fields:
        print(f"\nAvailable Access Database Fields for mapping {geo_field}:")
        for idx, column in enumerate(access_columns, 1):
            print(f"{idx}. {column}")
        access_field_idx = input(f"Map {geo_field} (Enter number or '0' to skip): ")
        if access_field_idx.isdigit() and int(access_field_idx) > 0 and int(access_field_idx) <= len(access_columns):
            selected_field = access_columns[int(access_field_idx) - 1]
            field_map[geo_field] = selected_field
        elif access_field_idx == '0':
            continue  # Skip mapping this field
        else:
            print("Invalid input, skipping this field.")
    return field_map


def delete_existing_data(table_name, cursor):
    cursor.execute(f"DELETE FROM {table_name}")
    cursor.commit()
    print("Existing data deleted from the table.")


def construct_sql_query(field_map):
    access_fields = ', '.join(field_map.values())
    placeholders = ', '.join(['?' for _ in field_map.values()])
    sql_query = f"INSERT INTO POSMGIS ({access_fields}) VALUES ({placeholders})"
    return sql_query


def ensure_double_data_type(cursor, table_name, fields):
    for field in fields:
        try:
            cursor.execute(f"ALTER TABLE {table_name} ALTER COLUMN {field} DOUBLE")
            cursor.commit()
        except pyodbc.Error as e:
            print(f"Error updating data type for {field}: {e}")


def transfer_data(access_db_path, feature_service_url):
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path}'
    conn = pyodbc.connect(conn_str)
    accdb_cursor = conn.cursor()
    gis = GIS()
    feature_layer = get_selected_feature_layer(gis, feature_service_url)

    if feature_layer is None:
        print("Failed to select a valid feature layer.")
        return

    access_table = 'POSMGIS'
    delete_existing_data(access_table, accdb_cursor)
    field_map = get_field_mappings(feature_layer, access_table, accdb_cursor)
    if not field_map:
        print("No fields mapped for transfer.")
        return
    features = feature_layer.query(where="1=1", out_fields="*", return_geometry=False).features
    sql_query = construct_sql_query(field_map)
    for feature in features:
        row = [feature.attributes[field] for field in field_map.keys()]
        accdb_cursor.execute(sql_query, row)
        conn.commit()
    double_fields = ['ManholeStartX', 'ManholeStartY', 'ManholeEndX', 'ManholeEndY']
    ensure_double_data_type(accdb_cursor, 'POSMGIS', double_fields)

    # Manual input for City and Coordinate system
    city = input("Enter the City: ")
    coord_system = input("Enter the Coordinate System: ")

    print(f"City: {city}, Coordinate System: {coord_system}")

    # Validate and check columns
    accdb_cursor.execute("SELECT * FROM POSMGIS")
    columns = [column[0] for column in accdb_cursor.description]
    print(f"Columns in POSMGIS: {columns}")

    if "City" not in columns or "Coordinate_System" not in columns:
        print("The columns 'City' and/or 'Coordinate_System' do not exist in the POSMGIS table.")
        return

    # Execute the update statement
    update_query = "UPDATE POSMGIS SET City = ?, Coordinate_System = ?"
    accdb_cursor.execute(update_query, (city, coord_system))
    conn.commit()

    print("Data transfer complete.")
    accdb_cursor.close()
    conn.close()


# Input database path from user
access_db_path = input("Enter the full path to your Access database (e.g., C:\\path\\to\\your\\database.mdb): ")
feature_service_url = input(
    "Enter the URL to your feature service layer (e.g., https://services9.arcgis.com/NJ6w02jClScR3ZJk/arcgis/rest/services/Ethridge_POSM_Online_Mapreader/FeatureServer): ")

# Call the function to transfer data
transfer_data(access_db_path, feature_service_url)
