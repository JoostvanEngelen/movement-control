

def get_setup_position(LTS_setup):
    x1 = float(str(LTS_setup.stages['x1'].device.Position))
    x2 = float(str(LTS_setup.stages['x2'].device.Position))
    y1 = float(str(LTS_setup.stages['y1'].device.Position))
    y2 = float(str(LTS_setup.stages['y2'].device.Position))
    return x1, x2, y1, y2

def get_setup_position_dict(LTS_setup):
    position_dic = {id: float(str(LTS_setup.stages[id].device.Position)) for id in LTS_setup.IDs}
    return

def is_valid_target_position(target_position):
    for id in target_position:
        if not isinstance(target_position[id], float) and not isinstance(target_position[id], float):
            return False
    return True
