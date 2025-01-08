
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyodbc
import arcpy



def gui_input():
    root = tk.Tk()
    root.title("POSM Database and Geodatabase Field Mapper")
    root.geometry('500x400')  # Adjusted for better visibility

    frame = tk.Frame(root)
    frame.pack(pady=20)

    tk.Label(frame, text="Access Database Path:").grid(row=0, column=0, sticky='e')
    access_db_entry = tk.Entry(frame, width=40)
    access_db_entry.grid(row=0, column=1)
    tk.Button(frame, text="Browse", command=lambda: browse_file(access_db_entry)).grid(row=0, column=2)

    tk.Label(frame, text="Geodatabase Path:").grid(row=1, column=0, sticky='e')
    gdb_path_entry = tk.Entry(frame, width=40)
    gdb_path_entry.grid(row=1, column=1)
    tk.Button(frame, text="Browse", command=lambda: browse_folder(gdb_path_entry)).grid(row=1, column=2)

    tk.Label(frame, text="Select Feature Class:").grid(row=2, column=0, sticky='e')
    feature_class_var = tk.StringVar()
    feature_class_dropdown = ttk.Combobox(frame, textvariable=feature_class_var, width=37)
    feature_class_dropdown.grid(row=2, column=1)

    tk.Button(frame, text="Load Feature Classes", command=lambda: load_feature_classes(gdb_path_entry.get(), feature_class_dropdown)).grid(row=3, column=0, columnspan=3)

    tk.Button(root, text="Setup Field Mappings", command=lambda: setup_field_mappings(access_db_entry.get(), feature_class_dropdown.get())).pack(pady=10)

    root.mainloop()

def browse_file(entry):
    filepath = filedialog.askopenfilename(filetypes=[("Access Files", "*.mdb;*.accdb")])
    entry.delete(0, tk.END)
    entry.insert(0, filepath)

def browse_folder(entry):
    folderpath = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folderpath)

def load_feature_classes(gdb_path, dropdown):
    arcpy.env.workspace = gdb_path
    feature_classes = arcpy.ListFeatureClasses()
    dropdown['values'] = feature_classes
    if feature_classes:
        dropdown.current(0)

def setup_field_mappings(access_db_path, feature_class):
    conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path}'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM POSMGIS")
    access_fields = [column[0] for column in cursor.description]

    geo_fields = [field.name for field in arcpy.ListFields(feature_class)]

    root = tk.Tk()
    root.title("Field Mapping")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)

    my_canvas = tk.Canvas(main_frame)
    my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
    my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    my_canvas.configure(yscrollcommand=my_scrollbar.set)
    my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

    second_frame = tk.Frame(my_canvas)
    my_canvas.create_window((0,0), window=second_frame, anchor="nw")

    mappings = []
    for geo_field in geo_fields:
        label = tk.Label(second_frame, text=geo_field)
        label.pack()
        field_combo = ttk.Combobox(second_frame, values=access_fields)
        field_combo.pack()
        mappings.append((geo_field, field_combo))

    execute_button = tk.Button(root, text="Execute Mapping", command=lambda: execute_field_mapping(mappings, access_db_path, feature_class))
    execute_button.pack(pady=20)

    cursor.close()
    conn.close()
    root.mainloop()


def execute_field_mapping(mappings, access_db_path, feature_class):
    if messagebox.askyesno("Confirm Delete", "Do you want to delete existing data in POSMGIS before mapping new data?"):
        if delete_existing_data(access_db_path):
            append_new_data(mappings, access_db_path, feature_class)
        else:
            messagebox.showerror("Error", "Failed to delete existing data. Operation aborted.")
    else:
        messagebox.showinfo("Cancelled", "Operation cancelled by user.")


def delete_existing_data(access_db_path):
    conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path}')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM POSMGIS")
        conn.commit()
        print("Existing data deleted from POSMGIS table.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def append_new_data(mappings, access_db_path, feature_class):
    """ Appends new data to the POSMGIS table based on the specified mappings. """
    conn = pyodbc.connect(f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={access_db_path}')
    cursor = conn.cursor()

    try:
        # Creating a list of access_fields and the corresponding feature class fields from mappings
        access_fields = [combo.get() for _, combo in mappings if combo.get()]
        feature_class_fields = [geo_field for geo_field, combo in mappings if combo.get()]

        # Ensuring that only valid fields with mappings are processed
        if access_fields and feature_class_fields:
            with arcpy.da.SearchCursor(feature_class, feature_class_fields) as cursor_fc:
                for row in cursor_fc:
                    # Prepare and execute one INSERT statement per row in the feature class
                    sql = f"INSERT INTO POSMGIS ({', '.join(access_fields)}) VALUES ({', '.join(['?']*len(access_fields))})"
                    cursor.execute(sql, row)

        conn.commit()
        messagebox.showinfo("Success", "New data appended successfully!")
    except Exception as e:
        print(f"An error occurred while appending data: {e}")
        messagebox.showerror("Error", "Failed to append new data.")
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    gui_input()
