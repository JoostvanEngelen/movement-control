import PySimpleGUI as sg

def home_window(LTS_setup):
    sg.theme('Default 1')
    layout = [
        [sg.Text("Connection with LTS300\\Ms established successfully.")],
        [sg.Text("The stages should be homed before continuing.")],
        [sg.Text('Make sure the linear stages can move unobstructedly to their 0-point.')],
        [sg.Text('\nOnce homing is done succesfully, a new window should appear.')],
        [sg.Button("Home stages"), sg.Button('Abort movement'), sg.Button("Cancel")],
        [sg.Text('Note: aborting a movement will raise an exception one minute after initiating homing.')]
    ]
    window = sg.Window("Concept", layout, modal=True, keep_on_top=True, icon='images/favicon.ico')
    state = 0

    while True:
        event, values = window.read()

        window.refresh()   

        if event == sg.WINDOW_CLOSED or event == "Cancel":
            break

        elif event == "Home stages":
            LTS_setup.home_window_thread(window)
            print('homing started')
            state = 1

        elif event == "Abort movement":
            LTS_setup.abort_movement()
            state = 0

        elif event == '-HOMING DONE-' and state == 1:
            print('homing done')
            break
            

    print('all done homing! ...or not...')
    window.close()
            
  

def input_coordinates_popup():
    sg.theme('Default 1')
    layout = [
        [sg.Text("Enter Coordinates:")],
        [sg.Text("X1:", size=(5,1)), sg.InputText("", size=(10, 1), key='-X1-')],
        [sg.Text("X2:", size=(5,1)), sg.InputText("", size=(10, 1), key='-X2-')],
        [sg.Text("Y1:", size=(5,1)), sg.InputText("", size=(10, 1), key='-Y1-')],
        [sg.Text("Y2:", size=(5,1)), sg.InputText("", size=(10, 1), key='-Y2-')],
        [sg.Button("OK"), sg.Button("Cancel")]
    ]

    # Create the popup window
    window = sg.Window("Enter Coordinates", layout, finalize=True,  icon='images/favicon.ico')

    # Event loop for the popup window
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            coordinates = None
            break

        if event == "OK":
            try:
                x1 = float(values['-X1-'])
                x2 = float(values['-X2-'])
                y1 = float(values['-Y1-'])
                y2 = float(values['-Y2-'])
                coordinates = {
                    'x1': x1,
                    'x2': x2,
                    'y1': y1,
                    'y2': y2
                }
                break
            except:
                sg.Popup("Please enter a valid target position", keep_on_top=True)

    # Close the popup window
    window.close()
    return coordinates


def input_aperture_popup():
    sg.theme('Default 1')
    layout = [
        [sg.Text("Select aperture dimensions:")],
        [sg.Combo(values=('Elliptical', 'Rectangular'), default_value='Elliptical', readonly=True, k='-SHAPE-')],
        [sg.Text("Center X (mm):", size=(12,1)), sg.InputText("", size=(10, 1), key='-CX-')],
        [sg.Text("Center Y (mm):", size=(12,1)), sg.InputText("", size=(10, 1), key='-CY-')],
        [sg.Text("Height (mm):", size=(12,1)), sg.InputText("", size=(10, 1), key='-HEIGHT-')],
        [sg.Text("Width (mm):", size=(12,1)), sg.InputText("", size=(10, 1), key='-WIDTH-')],
        [sg.Text("Angle (degrees):", size=(12,1)), sg.InputText("0", size=(10, 1), key='-ANGLE-')],
        [sg.Button("OK"), sg.Button("Cancel")]
    ]

    # Create the popup window
    window = sg.Window("Enter Coordinates", layout, finalize=True,  icon='images/favicon.ico')

    # Event loop for the popup window
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Cancel":
            aperture_characteristics = None
            break
        
        if event == 'OK':
            try:
                shape = values['-SHAPE-']
                center_x = float(values['-CX-'])
                center_y = float(values['-CY-'])
                height = float(values['-HEIGHT-'])
                width = float(values['-WIDTH-'])
                angle = float(values['-ANGLE-'])

                aperture_characteristics = {
                    'shape': shape,
                    'center_x': center_x,
                    'center_y': center_y,
                    'height': height,
                    'width': width,
                    'angle': angle
                }
                break

            except Exception as e:
                sg.Popup(f"Please enter a valid aperture shape: {e}", keep_on_top=True)
            

    return aperture_characteristics

