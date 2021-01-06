# Author: Zi Wang
import kitchen2d.kitchen_stuff as ks
from kitchen2d.kitchen_stuff import Kitchen2D
from kitchen2d.gripper import Gripper
import numpy as np
import time
import active_learners.helper as helper
SETTING = {
    'do_gui': False,
    'sink_w': 10.,
    'sink_h': 5.,
    'sink_d': 1.,
    'sink_pos_x': 20.,
    'left_table_width': 50.,
    'right_table_width': 50.,
    'faucet_h': 12.,
    'faucet_w': 5.,
    'faucet_d': 0.5,
    'planning': False,
    'overclock': 50 # number of frames to skip when showing graphics.
}


def query_gui(action_type, kitchen):
    choice = raw_input('Show GUI for {}? [y/n]'.format(action_type))
    if choice == 'y':
        print('Enabling GUI...')
        kitchen.enable_gui()
    else:
        print('Disabling GUI...')
        kitchen.disable_gui()

def main():
    kitchen = Kitchen2D(**SETTING)
    # expid_pour, expid_scoop = 0, 0 

    pour_to_w = 4.17393549546
    pour_to_h = 4.05998671658
    pour_from_w = 3.61443970857
    pour_from_h = 4.51052132521

    scoop_w = 5.388370713
    scoop_h = 4.52898336641
    holder_d = 0.5

    # Create objects
    gripper = Gripper(kitchen, (20,40), 0)
    cup1 = ks.make_cup(kitchen, (10,0), 0, pour_from_w, pour_from_h, holder_d)
    cup2 = ks.make_cup(kitchen, (-25,0), 0, pour_to_w, pour_to_h, holder_d)
    block = ks.make_block(kitchen, (-9,0), 0, 4, 4)
    large_cup = ks.make_cup(kitchen, (0, 0), 0, scoop_w, scoop_h, holder_d)
    
    # Move
    query_gui('MOVE', kitchen)
    gripper.find_path((-5., 10), 0, maxspeed=0.5)

    # Push
    query_gui('PUSH', kitchen)
    gripper.push(block, (1.,0.), -6, 0.5)

    # Pick
    query_gui('GRASP', kitchen)
    grasp = 0.306249162768
    rel_x = 3.70183788428
    rel_y = 9.01263886707
    dangle = 1.59620914618
    dangle *= np.sign(rel_x)

    gripper.find_path((15, 10), 0)
    gripper.grasp(cup1, grasp)

    # Get water
    query_gui('GET-WATER', kitchen)
    gripper.get_liquid_from_faucet(1) # 5 true

    # Pour
    query_gui('POUR', kitchen)
    print(gripper.pour(cup2, (rel_x, rel_y), dangle))

    # Place
    query_gui('PLACE', kitchen)
    gripper.place((10, 0), 0)
    
    # Scoop
    kitchen.gen_liquid_in_cup(large_cup, 10, 'sugar') # 1000 true
    kitchen.gen_liquid_in_cup(cup1, 10) # 200 true
    spoon = ks.make_spoon(kitchen, (23, 10), 0, 0.2, 3, 1.)

    query_gui('SCOOP', kitchen)
    rel_x1 = 0.0276296492162
    rel_y1 = 0.611922721287
    rel_x2 = 0.846900041891
    rel_y2 = 0.056968220054
    rel_x3 = 0.960750333945
    rel_y3 = 0.126499043204
    grasp = 0.883195866437

    rel_pos1 = (rel_x1, rel_y1); rel_pos2 = (rel_x2, rel_y2); rel_pos3 = (rel_x3, rel_y3)
    gripper.set_grasped(spoon, grasp, (23, 10), 0)
    print(gripper.scoop(large_cup, rel_pos1, rel_pos2, rel_pos3))

    # Dump
    query_gui('DUMP', kitchen)
    gripper.dump(cup1, 0.9)
    
    # Place
    query_gui('PLACE', kitchen)
    gripper.place((0, 10.), 0)

    # Stir
    query_gui('STIR', kitchen)
    stirrer = ks.make_stirrer(kitchen, (0, 3.5), 0., 0.2, 5., 0.5)
    gripper.set_grasped(stirrer, 0.8, (10, 10), 0)
    gripper.stir(cup1, (0, 0.0), (1, 0.0))
    gripper.find_path(gripper.position + [0, 5], 0)


if __name__ == '__main__':
    main()




# TODO
# [x] Test with different arrangement of objects --> parameters unaffected!
# [] Test with more objects and calls
# [] Add abstraction to fit "API" functionality
# [] Add "coffee bag", or alternatively, coffee faucet
# [] Add "drawers" to hide cups and other objects
# [] Change color of setting to become Kitchen for Progress 2D
# [] Clean code to remove unnecessary portions